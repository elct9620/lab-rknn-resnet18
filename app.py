import re
from typing import Annotated
from fastapi import FastAPI, Depends
from rknnlite.api import RKNNLite

MODEL_PATH = 'yolov5s-640-640.rknn'


app = FastAPI()


async def model():
    rknn = RKNNLite()
    try:
        rknn.load_rknn(MODEL_PATH)
        rknn.init_runtime()
        yield rknn
    finally:
        rknn.release()


@app.get("/")
async def root(model: Annotated[RKNNLite, Depends(model)]):
    sdk_version = model.get_sdk_version()
    api_version = re.search(r'API: (\d+\.\d+\.\d+)', sdk_version).group(1)
    driver_version = re.search(r'DRV: (\d+\.\d+\.\d+)', sdk_version).group(1)

    return {"api_version": api_version, "driver_version": driver_version}
