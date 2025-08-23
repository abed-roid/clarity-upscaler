import os
import subprocess
import base64
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
import glob
app = FastAPI()

@app.get("/ping")
async def ping():
    return JSONResponse(content={"message": "pong"}, status_code=200)
