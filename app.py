import re
import numpy as np
import cv2
from typing import Annotated
from fastapi import FastAPI, Depends, UploadFile
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

@app.post("/inference")
async def inference(model: Annotated[RKNNLite, Depends(model)], image: UploadFile):
    image = await image.read()
    image = np.frombuffer(image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image = cv2.resize(image, (640, 640))
    image = np.expand_dims(image, axis=0)

    outputs = model.inference(inputs=[image])

    return {"inference": outputs[0]}
