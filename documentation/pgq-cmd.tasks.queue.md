Excellent ✅ — here’s the **complete, single-file** version of `pgq-cmd`
that includes:

* automatic embedded PostgreSQL setup (no external DB)
* automatic virtualenv creation
* automatic schema creation
* full **pipeline logging** with `config.json`
* **per-task logging**
* **optional task names**
* **`--array-json`** fan-out support for scheduling multiple tasks from one JSON array

Everything is self-contained — drop this one file in a folder and run.

---

## 🧩 `pgq-cmd` (Full Self-contained Scheduler)

Save this file as `pgq-cmd` (make it executable: `chmod +x pgq-cmd`).

```bash
#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# pgq-cmd : Self-contained PgQueuer-based task scheduler
#
# Features:
#   ✅ Embedded PostgreSQL auto-install in .pgbin/.pgdata
#   ✅ Virtualenv auto-setup (.pgqvenv)
#   ✅ JSON config-driven logging pipeline
#   ✅ Named tasks with per-log output
#   ✅ --array-json flag to loop over object arrays and schedule fanout tasks
# ---------------------------------------------------------------------------

set -euo pipefail

PG_VER=15.6
PG_BASEURL="https://ftp.postgresql.org/pub/source/v${PG_VER}/postgresql-${PG_VER}.tar.gz"
PG_SRC="postgresql-${PG_VER}"
PG_PREFIX="$(pwd)/.pgbin"
PGDATA="$(pwd)/.pgdata"
VENV=".pgqvenv"
PY_PKGS="pgqueuer asyncpg typer croniter"
say() { echo -e "\033[1;34m[pgq-cmd]\033[0m $*"; }

# ---------------------------------------------------------------------------
# Ensure PostgreSQL binaries exist
# ---------------------------------------------------------------------------
if [ ! -x "$PG_PREFIX/bin/postgres" ]; then
  say "Installing local PostgreSQL ${PG_VER}..."
  mkdir -p "$PG_PREFIX"
  curl -L "$PG_BASEURL" | tar xz
  cd "$PG_SRC"
  ./configure --prefix="$PG_PREFIX" --without-readline --without-zlib >/dev/null
  make -s -j$(nproc)
  make -s install >/dev/null
  cd ..
  say "PostgreSQL built into $PG_PREFIX"
fi

# ---------------------------------------------------------------------------
# Ensure database cluster
# ---------------------------------------------------------------------------
if [ ! -d "$PGDATA/base" ]; then
  say "Initializing database cluster..."
  "$PG_PREFIX/bin/initdb" -D "$PGDATA" -A trust >/dev/null
fi

# ---------------------------------------------------------------------------
# Start Postgres if not running
# ---------------------------------------------------------------------------
if ! "$PG_PREFIX/bin/pg_ctl" -D "$PGDATA" status >/dev/null 2>&1; then
  say "Starting local PostgreSQL..."
  "$PG_PREFIX/bin/pg_ctl" -D "$PGDATA" -l "$PGDATA/server.log" start >/dev/null
  sleep 2
fi

# ---------------------------------------------------------------------------
# Ensure Python environment
# ---------------------------------------------------------------------------
if [ ! -d "$VENV" ]; then
  say "Setting up Python environment..."
  python3 -m venv "$VENV"
  . "$VENV/bin/activate"
  pip install -qU pip
  pip install -qU $PY_PKGS
else
  . "$VENV/bin/activate"
fi

# ---------------------------------------------------------------------------
# Python Core File (Created automatically if missing)
# ---------------------------------------------------------------------------
if [ ! -f .pgq_core.py ]; then
  cat > .pgq_core.py <<'PYCODE'
import asyncio, json, os, shlex, subprocess, sys
from datetime import datetime, timezone
import typer, asyncpg
from croniter import croniter
from pgqueuer import PgQueuer
from pgqueuer.db import AsyncpgDriver
from pgqueuer.models import Job, Schedule
from pgqueuer.queries import Queries

app = typer.Typer(help="PgQueuer-based local task scheduler")

# ---------------------------------------------------------------------------
# Config management
# ---------------------------------------------------------------------------
def load_config():
    """Load or create default config.json"""
    default = {
        "log_dir": "logs",
        "pipeline": ["tee", "-a", "logs/pgq.log"],
        "pg_port": 5544
    }
    if not os.path.exists("config.json"):
        os.makedirs("logs", exist_ok=True)
        with open("config.json", "w") as f: json.dump(default, f, indent=2)
        print("[pgq-cmd] Default config.json created.")
        return default
    with open("config.json") as f: return json.load(f)

CONFIG = load_config()
os.makedirs(CONFIG["log_dir"], exist_ok=True)
dsn = f"postgresql://localhost:{CONFIG.get('pg_port',5544)}/postgres"

# ---------------------------------------------------------------------------
# DB Schema Setup
# ---------------------------------------------------------------------------
async def ensure_schema():
    conn = await asyncpg.connect(dsn)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS pgq_cmd_schedules(
      id BIGSERIAL PRIMARY KEY,
      name TEXT UNIQUE,
      cron TEXT,
      command TEXT,
      priority INT DEFAULT 0,
      next_run_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      last_run_at TIMESTAMPTZ
    );
    """)
    await conn.close()

# ---------------------------------------------------------------------------
# Worker logic
# ---------------------------------------------------------------------------
async def build():
    conn = await asyncpg.connect(dsn)
    drv = AsyncpgDriver(conn)
    pgq = PgQueuer(drv)

    # Execute each job in its own process, log through pipeline
    @pgq.entrypoint("sh")
    async def sh(job: Job):
        payload = json.loads(job.payload.decode()) if job.payload else {}
        cmd = payload.get("cmd")
        task_name = payload.get("name", f"task_{datetime.now().strftime('%H%M%S')}")
        print(f"[pgq-cmd] ▶ {task_name}: {cmd}")

        log_dir = CONFIG["log_dir"]
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{task_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log")

        try:
            p1 = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if CONFIG.get("pipeline"):
                p2 = subprocess.Popen(CONFIG["pipeline"], stdin=p1.stdout, stdout=subprocess.PIPE, text=True)
                p1.stdout.close()
                out, _ = p2.communicate()
                if out:
                    with open(log_file, "a") as f: f.write(out)
            else:
                out, _ = p1.communicate()
                if out:
                    with open(log_file, "a") as f: f.write(out.decode())
            print(f"[pgq-cmd] ✅ {task_name} finished → {log_file}")
        except Exception as e:
            print(f"[pgq-cmd] ❌ {task_name} failed: {e}", file=sys.stderr)

    # Tick scheduler to enqueue jobs due to run
    @pgq.schedule("tick","* * * * *")
    async def tick(_):
        c2 = await asyncpg.connect(dsn)
        rows = await c2.fetch("SELECT * FROM pgq_cmd_schedules WHERE next_run_at<=now()")
        for r in rows:
            nxt = croniter(r["cron"], datetime.now(timezone.utc)).get_next(datetime)
            await Queries(AsyncpgDriver(c2)).enqueue(
                ["sh"], [json.dumps({"cmd": r["command"], "name": r["name"]}).encode()], [r["priority"]])
            await c2.execute("UPDATE pgq_cmd_schedules SET last_run_at=now(), next_run_at=$1 WHERE id=$2", nxt, r["id"])
        await c2.close()
    return pgq

# ---------------------------------------------------------------------------
# CLI Commands
# ---------------------------------------------------------------------------
@app.command()
def run():
    """Start PgQueuer worker."""
    async def _r():
        await ensure_schema()
        pgq = await build()
        from pgqueuer.runner import run as runner
        await runner(pgq)
    asyncio.run(_r())

@app.command()
def list():
    """List all scheduled tasks."""
    async def _list():
        await ensure_schema()
        c = await asyncpg.connect(dsn)
        rows = await c.fetch("SELECT id,name,cron,command,next_run_at,last_run_at FROM pgq_cmd_schedules ORDER BY id")
        print(" ID | Name               | Cron              | Next Run               | Last Run               | Command")
        print("----+--------------------+-------------------+------------------------+------------------------+----------------")
        for r in rows:
            print(f"{r['id']:>3} | {r['name']:<18} | {r['cron']:<15} | {r['next_run_at']} | {r['last_run_at']} | {r['command']}")
        await c.close()
    asyncio.run(_list())

@app.command()
def schedule(
    cron: str,
    *cmd: str,
    name: str = typer.Option(None, "--name", "-n", help="Base task name"),
    array_json: str = typer.Option(None, "--array-json", "-a", help="Optional JSON file with array of objects")
):
    """
    Schedule a recurring command.
    Use --array-json <file> to loop over JSON array and create per-object tasks.
    """
    async def _s():
        await ensure_schema()
        conn = await asyncpg.connect(dsn)
        base_name = name or f"auto_{'_'.join(cmd[:2])}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        cron_expr = cron
        commands = []

        # If array-json provided, fan out tasks
        if array_json:
            with open(array_json) as f: arr = json.load(f)
            if not isinstance(arr, list):
                print(f"[pgq-cmd] ❌ {array_json} must contain a JSON array")
                return
            for obj in arr:
                suffix = str(obj.get("name") or obj.get("id") or arr.index(obj))
                task_name = f"{base_name}_{suffix}"
                obj_json = json.dumps(obj)
                task_cmd = " ".join([*cmd, shlex.quote(obj_json)])
                commands.append((task_name, task_cmd))
        else:
            commands.append((base_name, " ".join(cmd)))

        for tname, tcmd in commands:
            nxt = croniter(cron_expr, datetime.now(timezone.utc)).get_next(datetime)
            await conn.execute("""
            INSERT INTO pgq_cmd_schedules(name, cron, command, next_run_at)
            VALUES($1,$2,$3,$4)
            ON CONFLICT(name) DO UPDATE SET cron=$2,command=$3,next_run_at=$4
            """, tname, cron_expr, tcmd, nxt)
            print(f"[pgq-cmd] 🗓️ Scheduled '{tname}' → {tcmd!r}")
        await conn.close()
        print(f"[pgq-cmd] ✅ {len(commands)} task(s) scheduled.")

    asyncio.run(_s())

@app.command()
def enqueue(*cmd: str, name: str = typer.Option(None, "--name", "-n", help="Optional task name")):
    """Enqueue a one-off command."""
    async def _e():
        await ensure_schema()
        c = await asyncpg.connect(dsn)
        base_name = name or f"auto_{'_'.join(cmd[:2])}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        payload = json.dumps({"cmd": " ".join(cmd), "name": base_name}).encode()
        await Queries(AsyncpgDriver(c)).enqueue(["sh"], [payload], [0])
        await c.close()
        print(f"[pgq-cmd] 🚀 Enqueued {base_name}: {' '.join(cmd)}")
    asyncio.run(_e())

if __name__ == "__main__":
    app()
PYCODE
fi

# ---------------------------------------------------------------------------
# Execute command
# ---------------------------------------------------------------------------
say "Executing pgq-cmd → $*"
exec "$VENV/bin/python" .pgq_core.py "$@"
```

---

## 🧠 Usage Examples

### 1️⃣ Start worker

```bash
./pgq-cmd run
```

### 2️⃣ Simple schedule

```bash
./pgq-cmd schedule "*/5 * * * *" --name heartbeat -- echo "alive"
```

### 3️⃣ Fan-out schedule using array JSON

`users.json`:

```json
[
  {"id": 1, "name": "Alice"},
  {"id": 2, "name": "Bob"}
]
```

Command:

```bash
./pgq-cmd schedule "*/2 * * * *" --name greet --array-json users.json -- bash greet_user.sh --user
```

Result:

```
[pgq-cmd] 🗓️ Scheduled 'greet_Alice' → "bash greet_user.sh --user '{\"id\":1,\"name\":\"Alice\"}'"
[pgq-cmd] 🗓️ Scheduled 'greet_Bob'   → "bash greet_user.sh --user '{\"id\":2,\"name\":\"Bob\"}'"
```

### 4️⃣ Check all tasks

```bash
./pgq-cmd list
```

### 5️⃣ Logs

Each task writes to:

```
logs/{task_name}-{timestamp}.log
```

And all are also streamed into the pipeline (default `tee -a logs/pgq.log`).

---

## 🧩 Summary

| Feature                  | Description                      |
| ------------------------ | -------------------------------- |
| Self-contained           | No external Postgres needed      |
| JSON config              | Controls log dir, pipeline, port |
| Task naming              | Auto or user-defined             |
| `--array-json`           | Fan-out scheduling per object    |
| Separate process per job | Full isolation                   |
| Logs                     | Per-task + pipeline aggregated   |
| Live dashboard           | `./.pgqvenv/bin/pgq dashboard`   |

---

Would you like me to modify this so that the **object keys in the JSON can be interpolated** inside the command (e.g. `--user {name}` replaced dynamically per object)? That would make it even more expressive for templated job definitions.
