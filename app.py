from typing import Annotated
from fastapi import FastAPI, Depends
from rknnlite.api import RKNNLite

MODEL_PATH = 'yolov5s-640-640.rknn'


app = FastAPI()


async def model():
    rknn = RKNNLite()
    try:
        rknn.load_model(model=MODEL_PATH)
        rknn.init_runtime()
        yield rknn
    finally:
        rknn.release()


@app.get("/")
async def root(model: Annotated[RKNNLite, Depends(model)]):
    sdk_version = model.get_sdk_version()
    return {"sdk_version": sdk_version}
