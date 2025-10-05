import os


wsgi_app = "src.app:init_app()"
bind = f"0.0.0.0:{os.environ['API_CONTAINER_PORT']}"
workers = (os.cpu_count() or 0) * 2 or 1
worker_class = "uvicorn_worker.UvicornWorker"
threads = 1
timeout = 45
graceful_timeout = 30
max_requests = 100_000
max_requests_jitter = 1_000
preload = True
