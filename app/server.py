from threading import Thread
from fastapi import FastAPI, Response
import uvicorn

app = FastAPI()

@app.get("/")
@app.head("/")
async def root():
    return Response(content='Server is Online.', media_type='text/plain')

def start():
    uvicorn.run(app, host="0.0.0.0", port=8080)

def server_thread():
    t = Thread(target=start)
    t.start()
