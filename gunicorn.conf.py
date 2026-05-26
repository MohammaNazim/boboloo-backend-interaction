# Gunicorn production config for Boboloo Backend
#
# Workers formula: (2 × vCPU) + 1
#   2 vCPU (t3.small/t3.medium) → 5 workers
#   4 vCPU (t3.large/c5.xlarge) → 9 workers
#
# Timeout is set high to handle large video uploads (up to 500 MB on slow
# connections). Gunicorn kills a worker if it does not respond within this
# many seconds, so it must exceed the expected max upload duration.

bind = "0.0.0.0:8080"
workers = 5
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 300           # 5 min — covers slow 500 MB uploads
keepalive = 5
worker_tmp_dir = "/dev/shm"   # shared memory fs — faster than /tmp on Linux

# Logging
errorlog = "-"          # stderr
accesslog = "-"         # stdout
loglevel = "info"
access_log_format = '%(h)s "%(r)s" %(s)s %(b)sB %(Dµs)µs'
