<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

## Django Blog Application

### 🚀 Quick Start

This project includes a Django blog application that can be run using the provided setup script.

### 📋 How to Run the Blog Application

**Default behavior (PostgreSQL + local dev):**
```bash
/workspace/run_bloggy.sh
```

This will automatically:
- ✅ Use PostgreSQL database (configured for devcontainer)
- ✅ Skip virtual environment creation (uses devcontainer environment)
- ✅ Run the Django development server

**Access the application at:**
- 🌐 **Blog:** `http://localhost:8000`
- 🔧 **Admin:** `http://localhost:8000/admin`

### 🗄️ Database Configuration

The application uses PostgreSQL by default in the devcontainer environment:

- **Database:** `djangobase`
- **User:** `postgres`
- **Password:** `postgres`
- **Host:** `localhost`
- **Port:** `5432`

### 👤 Default Login Credentials

- **Admin:** `admin@example.com` (set password on first login)
- **Sample Blogger:** `blogger` / `password123`

### 🛠️ Development Notes

- **Devcontainer Environment:** Dependencies are pre-installed via `uv` in the Dockerfile
- **PostgreSQL Setup:** Database and user are created automatically when first running the script
- **Sample Data:** Articles, categories, tags, and comments are created automatically
- **No Virtual Environment:** Script detects devcontainer and skips venv creation

### 📁 Project Structure

```
workspace/
├── runtime/                # Django application
│   ├── core/               # Django settings and configuration
│   ├── apps/               # Django apps (blog, dashboard, etc.)
│   ├── templates/          # HTML templates
│   ├── static/             # Static files
│   └── manage.py           # Django management script
├── run_bloggy.sh           # Main setup and run script
└── .devcontainer/          # Devcontainer configuration
    ├── docker-compose.yaml # PostgreSQL and Redis services
    └── devcontainer.json    # VS Code configuration
```

### 🐳 Devcontainer Services

The devcontainer includes these services:
- **PostgreSQL:** `pgvector/pgvector:pg16` on port 5432
- **Redis:** `redis:7-alpine` on port 6379
- **pgAdmin:** Database management interface