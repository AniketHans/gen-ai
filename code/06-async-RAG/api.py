from fastapi import FastAPI, Query, Path
from workers.connection import queue
from workers.process_query import process_query


app = FastAPI()


@app.get("/")
def root():
    return {"status": 200, "message": "Welcome ji welcome"}


@app.post("/chat")
def chat(query: str = Query(..., description="chat message")):
    job = queue.enqueue(process_query, query)
    return {"status": "Queued", "job-id": job.id}


@app.get("/result/{job_id}")
def result(job_id: str = Path(..., description="Job ID")):
    job = queue.fetch_job(job_id=job_id)
    result = job.return_value()

    return {"result": result}
