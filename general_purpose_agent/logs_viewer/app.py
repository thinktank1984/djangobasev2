"""
FastAPI Log Viewer Application
Displays logs from configured log folders with real-time updates
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import asyncio
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Add config to path - handle both Docker and local environments
config_path = Path("/app/config") if Path("/app/config").exists() else Path(__file__).parent.parent.parent.parent / "config"
sys.path.insert(0, str(config_path))
from config_utils import ConfigManager

app = FastAPI(title="Log Viewer", description="Real-time log viewer for migration logs")

# Initialize config manager
config_manager = ConfigManager()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

def translate_path_for_docker(path: str) -> str:
    """Translate host paths to Docker container paths"""
    # In Docker, paths are mounted differently
    if Path("/target_blazor_app").exists():
        # We're in Docker
        path = path.replace("/Users/ed.sharood2/code/target_blazor_app", "/target_blazor_app")
        path = path.replace("/Users/ed.sharood2/code/tool-access-modernisation/documentation", "/documentation")
    return path

def get_log_sections() -> Dict[str, str]:
    """Get all log folder sections from config"""
    return {
        "services_creation": translate_path_for_docker(config_manager.get_logs_folder_for_services_creation()),
        "pages_creation": translate_path_for_docker(config_manager.get_logs_folder_for_pages_creation()),
        "pages_testing": translate_path_for_docker(config_manager.get_logs_folder_for_pages_testing()),
        "vba_services": translate_path_for_docker(config_manager.get_logs_folder_for_vba_services_creation()),
        "documentation": translate_path_for_docker(config_manager.get_documentation_folder()),
        "all_logs": translate_path_for_docker(config_manager.get_logs_folder())
    }

def get_log_files(section_path: str) -> List[Dict[str, str]]:
    """Get all log files in a section"""
    if not os.path.exists(section_path):
        return []

    files = []
    for root, dirs, filenames in os.walk(section_path):
        for filename in filenames:
            if filename.endswith(('.log', '.txt', '.json', '.md')):
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, section_path)
                stat = os.stat(full_path)
                files.append({
                    "name": rel_path,
                    "full_path": full_path,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

    return sorted(files, key=lambda x: x['modified'], reverse=True)

def read_log_file(file_path: str, tail_lines: int = 1000) -> str:
    """Read log file, optionally tailing last N lines"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            if tail_lines:
                lines = f.readlines()
                return ''.join(lines[-tail_lines:])
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main page with log viewer UI"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            background: #2d2d30;
            padding: 15px 20px;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .header h1 {
            font-size: 20px;
            color: #cccccc;
        }

        .status {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4ec9b0;
            animation: pulse 2s infinite;
        }

        .status-indicator.disconnected {
            background: #f48771;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }

        .sidebar {
            width: 200px;
            background: #252526;
            border-right: 1px solid #3e3e42;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }

        .section {
            border-bottom: 1px solid #3e3e42;
        }

        .section-header {
            padding: 12px 15px;
            background: #2d2d30;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
        }

        .section-header:hover {
            background: #37373d;
        }

        .section-header.active {
            background: #094771;
        }

        .section-title {
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .file-count {
            background: #3e3e42;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
        }

        .file-list-pane {
            width: 300px;
            background: #252526;
            border-right: 1px solid #3e3e42;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }

        .file-list-header {
            padding: 12px 15px;
            background: #2d2d30;
            border-bottom: 1px solid #3e3e42;
            font-weight: 600;
            font-size: 13px;
            color: #cccccc;
        }

        .file-list {
            flex: 1;
            overflow-y: auto;
        }

        .file-item {
            padding: 10px 15px;
            cursor: pointer;
            font-size: 12px;
            border-left: 3px solid transparent;
            border-bottom: 1px solid #3e3e42;
        }

        .file-item:hover {
            background: #2a2d2e;
        }

        .file-item.active {
            background: #37373d;
            border-left-color: #007acc;
        }

        .file-name {
            color: #d4d4d4;
            margin-bottom: 4px;
            word-break: break-word;
        }

        .file-meta {
            font-size: 10px;
            color: #858585;
            margin-top: 3px;
        }

        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .toolbar {
            background: #2d2d30;
            padding: 10px 15px;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .btn {
            background: #0e639c;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }

        .btn:hover {
            background: #1177bb;
        }

        .btn.secondary {
            background: #3e3e42;
        }

        .btn.secondary:hover {
            background: #505050;
        }

        .log-content {
            flex: 1;
            overflow: auto;
            padding: 20px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
            background: #1e1e1e;
        }

        .log-line {
            margin: 0;
            padding: 2px 0;
            font-family: 'Consolas', 'Courier New', monospace;
        }

        .log-line.error {
            color: #f48771;
            background: rgba(244, 135, 113, 0.1);
            padding: 2px 4px;
        }

        .log-line.warning {
            color: #ce9178;
            background: rgba(206, 145, 120, 0.1);
            padding: 2px 4px;
        }

        .log-line.success {
            color: #4ec9b0;
        }

        .log-line.info {
            color: #569cd6;
        }

        .log-line.timestamp {
            color: #858585;
        }

        .log-line.debug {
            color: #808080;
        }

        /* JSON Syntax Highlighting */
        .json-content {
            font-family: 'Consolas', 'Courier New', monospace;
            white-space: pre;
            color: #d4d4d4;
        }

        .json-key {
            color: #9cdcfe;
        }

        .json-string {
            color: #ce9178;
        }

        .json-number {
            color: #b5cea8;
        }

        .json-boolean {
            color: #569cd6;
        }

        .json-null {
            color: #569cd6;
        }

        /* Markdown Rendering */
        .markdown-content {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #d4d4d4;
        }

        .markdown-content h1 {
            color: #4ec9b0;
            border-bottom: 2px solid #4ec9b0;
            padding-bottom: 8px;
            margin-top: 24px;
            margin-bottom: 16px;
        }

        .markdown-content h2 {
            color: #569cd6;
            border-bottom: 1px solid #569cd6;
            padding-bottom: 6px;
            margin-top: 20px;
            margin-bottom: 12px;
        }

        .markdown-content h3 {
            color: #dcdcaa;
            margin-top: 16px;
            margin-bottom: 8px;
        }

        .markdown-content code {
            background: #2d2d30;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Courier New', monospace;
            color: #ce9178;
        }

        .markdown-content pre {
            background: #2d2d30;
            padding: 12px;
            border-radius: 4px;
            overflow-x: auto;
            border-left: 3px solid #007acc;
        }

        .markdown-content pre code {
            background: none;
            padding: 0;
        }

        .markdown-content ul, .markdown-content ol {
            margin-left: 20px;
        }

        .markdown-content li {
            margin: 4px 0;
        }

        .markdown-content a {
            color: #569cd6;
            text-decoration: none;
        }

        .markdown-content a:hover {
            text-decoration: underline;
        }

        .markdown-content blockquote {
            border-left: 4px solid #4ec9b0;
            padding-left: 16px;
            margin-left: 0;
            color: #858585;
        }

        .markdown-content table {
            border-collapse: collapse;
            margin: 12px 0;
        }

        .markdown-content th, .markdown-content td {
            border: 1px solid #3e3e42;
            padding: 8px 12px;
        }

        .markdown-content th {
            background: #2d2d30;
            font-weight: 600;
        }

        .placeholder {
            text-align: center;
            padding: 40px;
            color: #858585;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #4ec9b0;
        }

        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }

        ::-webkit-scrollbar-track {
            background: #1e1e1e;
        }

        ::-webkit-scrollbar-thumb {
            background: #424242;
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #4e4e4e;
        }

        .flower-iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Log Viewer - Migration Logs</h1>
        <div class="status">
            <div class="status-indicator" id="wsStatus"></div>
            <span id="statusText">Connected</span>
        </div>
    </div>

    <div class="container">
        <div class="sidebar" id="sidebar">
            <div class="loading">Loading sections...</div>
        </div>

        <div class="file-list-pane">
            <div class="file-list-header" id="fileListHeader">Select a folder</div>
            <div class="file-list" id="fileListContent">
                <div class="placeholder">Select a folder from the left sidebar</div>
            </div>
        </div>

        <div class="main-content">
            <div class="toolbar">
                <button class="btn" onclick="refreshLog()">Refresh</button>
                <button class="btn secondary" onclick="clearLog()">Clear</button>
                <button class="btn secondary" onclick="toggleAutoScroll()">
                    <span id="autoScrollText">Auto-scroll: ON</span>
                </button>
                <button class="btn secondary" onclick="downloadLog()">Download</button>
                <button class="btn secondary" onclick="showFlower()">Flower Monitor</button>
            </div>

            <div class="log-content" id="logContent">
                <div class="placeholder">Select a log file to view</div>
            </div>
        </div>
    </div>

    <script>
        let ws;
        let currentFile = null;
        let autoScroll = true;
        let sections = {};
        let currentSection = null;
        let filesCache = {};

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

            ws.onopen = () => {
                document.getElementById('wsStatus').classList.remove('disconnected');
                document.getElementById('statusText').textContent = 'Connected';
            };

            ws.onclose = () => {
                document.getElementById('wsStatus').classList.add('disconnected');
                document.getElementById('statusText').textContent = 'Disconnected';
                setTimeout(connectWebSocket, 3000);
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'log_update' && data.file === currentFile) {
                    appendLogContent(data.content);
                }
            };
        }

        async function loadSections() {
            const response = await fetch('/api/sections');
            sections = await response.json();
            renderSidebar();
        }

        function renderSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.innerHTML = '';

            for (const [sectionKey, sectionPath] of Object.entries(sections)) {
                const sectionDiv = document.createElement('div');
                sectionDiv.className = 'section';

                const header = document.createElement('div');
                header.className = 'section-header';
                header.onclick = () => selectSection(sectionKey);

                const title = document.createElement('div');
                title.className = 'section-title';
                title.textContent = sectionKey.replace(/_/g, ' ');

                const count = document.createElement('div');
                count.className = 'file-count';
                count.id = `count-${sectionKey}`;
                count.textContent = '...';

                header.appendChild(title);
                header.appendChild(count);

                sectionDiv.appendChild(header);
                sidebar.appendChild(sectionDiv);

                loadFilesCount(sectionKey);
            }
        }

        async function loadFilesCount(sectionKey) {
            const response = await fetch(`/api/files/${sectionKey}`);
            const files = await response.json();

            filesCache[sectionKey] = files;
            document.getElementById(`count-${sectionKey}`).textContent = files.length;
        }

        async function selectSection(sectionKey) {
            currentSection = sectionKey;

            // Update active state in sidebar
            document.querySelectorAll('.section-header').forEach(el => {
                el.classList.remove('active');
            });
            event.target.closest('.section-header').classList.add('active');

            // Load files if not cached
            if (!filesCache[sectionKey]) {
                const response = await fetch(`/api/files/${sectionKey}`);
                filesCache[sectionKey] = await response.json();
            }

            renderFileList(sectionKey, filesCache[sectionKey]);
        }

        function renderFileList(sectionKey, files) {
            const header = document.getElementById('fileListHeader');
            header.textContent = sectionKey.replace(/_/g, ' ').toUpperCase() + ` (${files.length})`;

            const fileListContent = document.getElementById('fileListContent');
            fileListContent.innerHTML = '';

            if (files.length === 0) {
                fileListContent.innerHTML = '<div class="placeholder">No log files found</div>';
                return;
            }

            files.forEach(file => {
                const fileDiv = document.createElement('div');
                fileDiv.className = 'file-item';
                fileDiv.onclick = () => loadLog(file.full_path);

                const name = document.createElement('div');
                name.className = 'file-name';
                name.textContent = file.name;

                const meta = document.createElement('div');
                meta.className = 'file-meta';
                const size = (file.size / 1024).toFixed(1);
                const date = new Date(file.modified).toLocaleString();
                meta.textContent = `${size} KB - ${date}`;

                fileDiv.appendChild(name);
                fileDiv.appendChild(meta);
                fileListContent.appendChild(fileDiv);
            });
        }

        async function loadLog(filePath) {
            currentFile = filePath;

            // Update active state
            document.querySelectorAll('.file-item').forEach(el => {
                el.classList.remove('active');
            });
            event.target.closest('.file-item').classList.add('active');

            const response = await fetch(`/api/log?file=${encodeURIComponent(filePath)}`);
            const content = await response.text();

            const logContent = document.getElementById('logContent');
            logContent.innerHTML = '';

            // Detect file type and apply appropriate formatting
            const fileExt = filePath.split('.').pop().toLowerCase();
            renderContent(content, fileExt);
        }

        function renderContent(content, fileType) {
            const logContent = document.getElementById('logContent');

            if (fileType === 'json') {
                renderJSON(content);
            } else if (fileType === 'md') {
                renderMarkdown(content);
            } else {
                renderPlainLog(content);
            }

            if (autoScroll) {
                logContent.scrollTop = logContent.scrollHeight;
            }
        }

        function renderJSON(content) {
            const logContent = document.getElementById('logContent');
            try {
                const jsonObj = JSON.parse(content);
                const formatted = JSON.stringify(jsonObj, null, 2);
                const highlighted = syntaxHighlightJSON(formatted);

                const pre = document.createElement('pre');
                pre.className = 'json-content';
                pre.innerHTML = highlighted;
                logContent.appendChild(pre);
            } catch (e) {
                // If parsing fails, render as plain text
                renderPlainLog(content);
            }
        }

        function syntaxHighlightJSON(json) {
            json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
                let cls = 'json-number';
                if (/^"/.test(match)) {
                    if (/:$/.test(match)) {
                        cls = 'json-key';
                    } else {
                        cls = 'json-string';
                    }
                } else if (/true|false/.test(match)) {
                    cls = 'json-boolean';
                } else if (/null/.test(match)) {
                    cls = 'json-null';
                }
                return '<span class="' + cls + '">' + match + '</span>';
            });
        }

        function renderMarkdown(content) {
            const logContent = document.getElementById('logContent');
            const div = document.createElement('div');
            div.className = 'markdown-content';

            // Simple markdown parser
            let html = content
                // Headers
                .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                .replace(/^# (.*$)/gim, '<h1>$1</h1>')
                // Bold
                .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
                // Italic
                .replace(/\*(.*?)\*/gim, '<em>$1</em>')
                // Code blocks
                .replace(/```([\\s\\S]*?)```/gim, '<pre><code>$1</code></pre>')
                // Inline code
                .replace(/`([^`]+)`/gim, '<code>$1</code>')
                // Links
                .replace(/\\[([^\\]]+)\\]\\(([^\\)]+)\\)/gim, '<a href="$2" target="_blank">$1</a>')
                // Line breaks
                .replace(/\\n/g, '<br>');

            div.innerHTML = html;
            logContent.appendChild(div);
        }

        function renderPlainLog(content) {
            const logContent = document.getElementById('logContent');
            const lines = content.split('\\n');

            lines.forEach(line => {
                if (line.trim() === '') {
                    return; // Skip empty lines
                }

                const lineDiv = document.createElement('div');
                lineDiv.className = 'log-line';

                const lowerLine = line.toLowerCase();

                if (lowerLine.includes('error') || lowerLine.includes('fail') || lowerLine.includes('exception')) {
                    lineDiv.classList.add('error');
                } else if (lowerLine.includes('warning') || lowerLine.includes('warn')) {
                    lineDiv.classList.add('warning');
                } else if (lowerLine.includes('success') || lowerLine.includes('complete')) {
                    lineDiv.classList.add('success');
                } else if (lowerLine.includes('info:')) {
                    lineDiv.classList.add('info');
                } else if (lowerLine.includes('debug')) {
                    lineDiv.classList.add('debug');
                } else if (line.match(/^\d{4}-\d{2}-\d{2}/) || line.match(/^\[\d{4}/)) {
                    lineDiv.classList.add('timestamp');
                }

                lineDiv.textContent = line;
                logContent.appendChild(lineDiv);
            });
        }

        function appendLogContent(content) {
            // For real-time updates, use plain log rendering
            renderPlainLog(content);
        }

        function refreshLog() {
            if (currentFile) {
                loadLog(currentFile);
            }
        }

        function clearLog() {
            document.getElementById('logContent').innerHTML = '';
        }

        function toggleAutoScroll() {
            autoScroll = !autoScroll;
            document.getElementById('autoScrollText').textContent =
                `Auto-scroll: ${autoScroll ? 'ON' : 'OFF'}`;
        }

        function downloadLog() {
            if (currentFile) {
                window.location.href = `/api/download?file=${encodeURIComponent(currentFile)}`;
            }
        }

        function showFlower() {
            const logContent = document.getElementById('logContent');
            logContent.innerHTML = '<iframe class="flower-iframe" src="http://localhost:5555"></iframe>';
        }

        // Auto-refresh every 5 seconds
        setInterval(() => {
            if (currentFile && autoScroll) {
                refreshLog();
            }
        }, 5000);

        // Load sections immediately on page load
        loadSections();

        // Connect WebSocket for real-time updates
        connectWebSocket();
    </script>
</body>
</html>
    """)

@app.get("/api/sections")
async def api_sections():
    """Get all log sections"""
    return get_log_sections()

@app.get("/api/files/{section}")
async def api_files(section: str):
    """Get files in a section"""
    sections = get_log_sections()
    if section not in sections:
        raise HTTPException(status_code=404, detail="Section not found")

    section_path = sections[section]
    return get_log_files(section_path)

@app.get("/api/log")
async def api_log(file: str, tail: int = 1000):
    """Get log file content"""
    if not os.path.exists(file):
        raise HTTPException(status_code=404, detail="File not found")

    return read_log_file(file, tail)

@app.get("/api/download")
async def api_download(file: str):
    """Download log file"""
    if not os.path.exists(file):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file,
        media_type='text/plain',
        filename=os.path.basename(file)
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def watch_logs():
    """Background task to watch for log changes"""
    # This would monitor log files and broadcast changes
    # For now, clients poll via auto-refresh
    pass

if __name__ == "__main__":
    print("Starting Log Viewer on http://localhost:8000")
    print(f"Watching logs in: {config_manager.get_logs_folder()}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
