import re
import numpy as np
import cv2
from typing import Annotated
from fastapi import FastAPI, Depends, UploadFile
from rknnlite.api import RKNNLite
from synset_label import labels

MODEL_PATH = 'resnet18_for_rk3588.rknn'


app = FastAPI()


async def model():
    rknn = RKNNLite()
    try:
        rknn.load_rknn(MODEL_PATH)
        rknn.init_runtime()
        yield rknn
    finally:
        rknn.release()


def top5(result):
    output = result[0].reshape(-1)
    # Softmax
    output = np.exp(output) / np.sum(np.exp(output))
    # Get the indices of the top 5 largest values
    output_sorted_indices = np.argsort(output)[::-1][:5]

    selected = []
    for i, index in enumerate(output_sorted_indices):
        value = output[index]
        if value > 0:
            selected.append(labels[index])
    return selected


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
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.expand_dims(image, axis=0)

    outputs = model.inference(inputs=[image])

    return {"top5": top5(outputs)}
