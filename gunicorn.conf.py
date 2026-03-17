# Gunicorn configuration for Phone Control API
#
# Concurrency model: workers × threads = total concurrent requests
#   4 workers × 4 threads = 16 concurrent requests
#
# Why these values?
#   - Each ADB call runs a subprocess that can take 2-3 seconds.
#   - A secondary service polls multiple phones every ~2 seconds.
#   - 16 concurrent slots gives plenty of headroom for 5+ phones.
#
# Scaling guidance:
#   - More phones / higher poll frequency → increase workers or threads.
#   - Rule of thumb: workers = (2 × CPU cores) + 1
#   - Keep threads ≤ 4-8; too many threads per worker adds overhead.
#   - Example for 10 phones: workers = 4, threads = 8  (32 concurrent)

bind = "127.0.0.1:5000"      # Localhost only — matches current security model
workers = 4                   # Separate processes; isolates slow ADB calls
threads = 4                   # Threads per worker (gthread worker class required)
worker_class = "gthread"      # Threaded worker — required when threads > 1
timeout = 60                  # Generous timeout for slow ADB-over-network calls
keepalive = 2                 # Keep-alive connections (seconds)
accesslog = "-"               # Log access to stdout
errorlog = "-"                # Log errors to stderr
loglevel = "info"
