import os,secrets
from dotenv import load_dotenv
from fastapi import FastAPI,Query
from fastapi.responses import FileResponse
from livekit import api
load_dotenv(); app=FastAPI(title="LiveKit microphone test")
@app.get("/")
async def index(): return FileResponse("static/index.html")
@app.get("/token")
async def token(room:str=Query(default="teste-microfone",min_length=1,max_length=100),identity:str|None=None):
    identity=identity or f"usuario-{secrets.token_hex(4)}"
    t=(api.AccessToken(os.environ["LIVEKIT_API_KEY"],os.environ["LIVEKIT_API_SECRET"]).with_identity(identity).with_name("Usuário do microfone").with_grants(api.VideoGrants(room_join=True,room=room,can_publish=True,can_subscribe=True)))
    return {"token":t.to_jwt(),"url":os.getenv("PUBLIC_LIVEKIT_URL","ws://localhost:7880"),"room":room,"identity":identity}
@app.get("/health")
async def health(): return {"ok":True}
