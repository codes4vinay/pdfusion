from redis import Redis
from rq import Queue

redis_collection = Redis(
    host="valkey",
    port="6379"
)

q = Queue(connection=redis_collection)
