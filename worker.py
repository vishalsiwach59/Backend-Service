import os
from redis import Redis
from rq import Worker

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = Redis.from_url(redis_url)

if __name__ == "__main__":
    with redis_conn.pipeline():
        worker = Worker(["default"], connection=redis_conn)
        worker.work()
