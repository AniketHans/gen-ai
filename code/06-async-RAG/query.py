from rq import Queue
from redis import Redis
from rq.worker import SimpleWorker
from workers.process_query import print_message, process_query


redis_conn = Redis(host="redis")
q = Queue(connection=redis_conn)

# Take User Query
query = input("> ")

job = q.enqueue(process_query, query)
print(job)
