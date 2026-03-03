"""
Web Dashboard for Content Agent.
Manage content sources, schedule posts, and view analytics.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


class ContentDashboard:
    """
    Web dashboard for content management.
    
    Features:
    - Content calendar
    - Source management
    - Post scheduler
    - Analytics visualization
    - Real-time logs
    """
    
    def __init__(self, content_agent, host="127.0.0.1", port=8788):
        if not HAS_FASTAPI:
            raise ImportError(
                "FastAPI required. Install with: pip install fastapi uvicorn"
            )
        
        self.agent = content_agent
        self.host = host
        self.port = port
        self.app = self._create_app()
    
    def _create_app(self) -> "FastAPI":
        """Create FastAPI application."""
        app = FastAPI(
            title="Content Agent Dashboard",
            description="Content curation and publishing management",
            version="0.2.0"
        )
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return self._get_dashboard_html()
        
        @app.get("/api/stats")
        async def get_stats():
            """Get agent statistics."""
            return self.agent.get_stats()
        
        @app.get("/api/sources")
        async def get_sources():
            """Get configured sources."""
            return {
                "sources": list(self.agent._sources.keys()),
                "available": ["moltbook", "clawdchat"]
            }
        
        @app.get("/api/platforms")
        async def get_platforms():
            """Get configured platforms."""
            return {
                "platforms": list(self.agent._publishers.keys()),
                "available": ["moltbook", "clawdchat"]
            }
        
        @app.post("/api/run")
        async def run_routine(background_tasks: BackgroundTasks):
            """Run daily routine in background."""
            background_tasks.add_task(self.agent.daily_routine)
            return {"status": "started", "message": "Daily routine started in background"}
        
        @app.post("/api/sources/{name}/fetch")
        async def fetch_source(name: str, limit: int = 20):
            """Fetch posts from a source."""
            source = self.agent._get_source(name)
            if not source:
                raise HTTPException(status_code=404, detail="Source not configured")
            
            try:
                posts = source.fetch_posts(limit=limit)
                return {"source": name, "posts": posts}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/generate")
        async def generate_content(data: Dict):
            """Generate content using LLM."""
            if not self.agent.generator:
                raise HTTPException(status_code=503, detail="LLM not configured")
            
            try:
                result = self.agent.generator.summarize_posts(
                    data.get("posts", []),
                    data.get("length", "medium")
                )
                return {"content": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/publish/{platform}")
        async def publish_to_platform(platform: str, post: Dict):
            """Publish to a platform."""
            publisher = self.agent._get_publisher(platform)
            if not publisher:
                raise HTTPException(status_code=404, detail="Platform not configured")
            
            try:
                result = publisher.publish(post)
                return {"status": "success", "result": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/configure/{platform}")
        async def configure_platform(platform: str, config: Dict):
            """Configure platform API keys."""
            self.agent.configure_platform(platform, config)
            return {"status": "configured", "platform": platform}
        
        @app.get("/api/reports")
        async def get_reports(limit: int = 10):
            """Get recent daily reports from memory."""
            # This would need to list cold storage
            return {"reports": []}
        
        return app
    
    def _get_dashboard_html(self) -> str:
        """Generate dashboard HTML."""
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>Content Agent Dashboard</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
            color: #e0e7ff;
            min-height: 100vh;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 2rem;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.8; }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .stat-card h3 {
            font-size: 0.875rem;
            opacity: 0.7;
            margin-bottom: 0.5rem;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #60a5fa;
        }
        .actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .action-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .action-card h3 {
            margin-bottom: 1rem;
            color: #93c5fd;
        }
        .btn {
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            width: 100%;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .status {
            margin-top: 1rem;
            padding: 0.75rem;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            font-family: monospace;
            font-size: 0.875rem;
        }
        .config-form {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        .config-form input {
            padding: 0.75rem;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: white;
        }
        .log-container {
            background: rgba(0,0,0,0.3);
            border-radius: 16px;
            padding: 1.5rem;
            height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.875rem;
        }
        .log-entry {
            padding: 0.25rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .log-time { color: #94a3b8; }
        .log-info { color: #60a5fa; }
        .log-success { color: #4ade80; }
        .log-error { color: #f87171; }
        .loading {
            text-align: center;
            padding: 2rem;
            opacity: 0.5;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📰 Content Agent Dashboard</h1>
        <p>AI-powered content curation and publishing</p>
    </div>
    
    <div class="container">
        <div class="stats-grid" id="stats">
            <div class="loading">Loading...</div>
        </div>
        
        <div class="actions">
            <div class="action-card">
                <h3>🚀 Quick Actions</h3>
                <button class="btn" onclick="runRoutine()">▶️ Run Daily Routine</button>
                <div id="routineStatus" class="status" style="display:none"></div>
            </div>
            
            <div class="action-card">
                <h3>⚙️ Configure Moltbook</h3>
                <div class="config-form">
                    <input type="password" id="moltbookKey" placeholder="API Key">
                    <button class="btn" onclick="configMoltbook()">💾 Save</button>
                </div>
            </div>
            
            <div class="action-card">
                <h3>⚙️ Configure 虾聊</h3>
                <div class="config-form">
                    <input type="password" id="clawdchatKey" placeholder="API Key">
                    <button class="btn" onclick="configClawdchat()">💾 Save</button>
                </div>
            </div>
        </div>
        
        <div class="action-card" style="margin-bottom: 2rem;">
            <h3>📋 Activity Log</h3>
            <div class="log-container" id="logs">
                <div class="log-entry">
                    <span class="log-time">[System]</span> 
                    <span class="log-info">Dashboard loaded</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function addLog(message, type = 'info') {
            const logs = document.getElementById('logs');
            const time = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = `
                <span class="log-time">[${time}]</span>
                <span class="log-${type}">${message}</span>
            `;
            logs.insertBefore(entry, logs.firstChild);
        }
        
        async function fetchStats() {
            try {
                const res = await fetch('/api/stats');
                const stats = await res.json();
                displayStats(stats);
            } catch (e) {
                console.error(e);
            }
        }
        
        function displayStats(stats) {
            const html = `
                <div class="stat-card">
                    <h3>💾 Memory Entries</h3>
                    <div class="stat-value">${stats.memory?.hot_entries + stats.memory?.warm_entries || 0}</div>
                </div>
                <div class="stat-card">
                    <h3>📡 Sources</h3>
                    <div class="stat-value">${stats.sources?.length || 0}</div>
                </div>
                <div class="stat-card">
                    <h3>📤 Platforms</h3>
                    <div class="stat-value">${stats.platforms?.length || 0}</div>
                </div>
                <div class="stat-card">
                    <h3>🧠 LLM Ready</h3>
                    <div class="stat-value">${stats.llm_configured ? '✓' : '✗'}</div>
                </div>
            `;
            document.getElementById('stats').innerHTML = html;
        }
        
        async function runRoutine() {
            const btn = document.querySelector('button[onclick="runRoutine()"]');
            const status = document.getElementById('routineStatus');
            btn.disabled = true;
            status.style.display = 'block';
            status.textContent = 'Running...';
            addLog('Starting daily routine...', 'info');
            
            try {
                const res = await fetch('/api/run', { method: 'POST' });
                const data = await res.json();
                status.textContent = data.message;
                addLog('Daily routine started', 'success');
            } catch (e) {
                status.textContent = 'Error: ' + e.message;
                addLog('Failed: ' + e.message, 'error');
            } finally {
                btn.disabled = false;
                setTimeout(() => status.style.display = 'none', 3000);
            }
        }
        
        async function configMoltbook() {
            const key = document.getElementById('moltbookKey').value;
            if (!key) return alert('Please enter API key');
            
            try {
                await fetch('/api/configure/moltbook', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({api_key: key})
                });
                addLog('Moltbook configured', 'success');
                document.getElementById('moltbookKey').value = '';
                fetchStats();
            } catch (e) {
                addLog('Config failed: ' + e.message, 'error');
            }
        }
        
        async function configClawdchat() {
            const key = document.getElementById('clawdchatKey').value;
            if (!key) return alert('Please enter API key');
            
            try {
                await fetch('/api/configure/clawdchat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({api_key: key})
                });
                addLog('虾聊 configured', 'success');
                document.getElementById('clawdchatKey').value = '';
                fetchStats();
            } catch (e) {
                addLog('Config failed: ' + e.message, 'error');
            }
        }
        
        // Initial load
        fetchStats();
        setInterval(fetchStats, 5000);
    </script>
</body>
</html>
        '''
    
    def run(self):
        """Run the dashboard server."""
        import uvicorn
        print(f"🌐 Starting Content Dashboard at http://{self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)


def launch_dashboard(content_agent, port: int = 8788):
    """
    Quick launch function.
    
    Usage:
        from content_agent import ContentAgent
        from content_agent.web.dashboard import launch_dashboard
        
        agent = ContentAgent()
        launch_dashboard(agent)
    """
    dashboard = ContentDashboard(content_agent, port=port)
    dashboard.run()
