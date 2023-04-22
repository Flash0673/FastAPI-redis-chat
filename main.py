from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocket
from fastapi.templating import Jinja2Templates

from redis_services import connection, redis_connector

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    async with connection.pubsub() as pubsub:
        await pubsub.psubscribe("channel:*")
    return templates.TemplateResponse("index.html", {
        "request": request,
    })


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await redis_connector(websocket)
