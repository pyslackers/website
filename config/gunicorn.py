import multiprocessing
import os


accesslog = '-'

bind = f'{os.getenv("GUNICORN_HOST", "0.0.0.0")}:{os.getenv("GUNICORN_PORT", "8000")}'  # noqa

capture_output = True

syslog = os.getenv('LOG_SYSLOG', 'false').lower() in ['true', '1', 'yes']

threads = int(os.getenv('GUNICORN_THREADS', multiprocessing.cpu_count() * 2 + 1))  # noqa

workers = int(os.getenv('GUNICORN_WORKERS', 1))

worker_class = 'gthread'
