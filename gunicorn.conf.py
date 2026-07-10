# gunicorn.conf.py - Render.com optimized
import database as db
import os

# ═══ RENDER SPECIFIC ═══
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
workers = 1
worker_class = "gthread"  # Threading support
threads = 4  # 4 threads per worker
timeout = 120  # 2 min (Render dyno 30min idle timeout)
keepalive = 10

# Memory optimization
max_requests = 1000
max_requests_jitter = 100
preload_app = False

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

def post_fork(server, worker):
    """Called after worker forks."""
    import threading
    from api import resume_incomplete_tasks
    
    def startup():
        import time
        max_wait = 60  # 60 sn bekle
        start = time.time()
        
        while time.time() - start < max_wait:
            try:
                db.init_db()
                resume_incomplete_tasks()
                print("[STARTUP] DB initialized & recovery started")
                return
            except Exception as e:
                elapsed = int(time.time() - start)
                print(f"[STARTUP] ({elapsed}s) Retrying DB... {str(e)[:100]}")
                time.sleep(5)
        
        print("[STARTUP] WARNING: DB initialization failed after 60s!")
    
    # Daemon thread, kapanırsa process kapanmaz
    t = threading.Thread(target=startup, daemon=True)
    t.start()

def when_ready(server):
    print("[READY] Gunicorn server started on Render")
