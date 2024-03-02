from fastapi import FastAPI
from rknnlite.api import RKNNLite

DEVICE_COMPATIBLE_NODE = '/proc/device-tree/compatible'

app = FastAPI()

@app.get("/")
async def root():
    device_compatible_str = ""
    with open(DEVICE_COMPATIBLE_NODE) as f:
        device_compatible_str = f.read()

    return {"device_compatible": device_compatible_str}
