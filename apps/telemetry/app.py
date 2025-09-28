from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime as dt


app = FastAPI(title="Telemetry Service", version="0.1.0")

class TelemetryItem(BaseModel):
    device_id: str
    ts: dt
    value: float
    unit: str


# todo: "data storage"
_telemetryStorage: List[TelemetryItem] = []


@app.post("/telemetry", status_code=202)
async def telemetry_append(item: TelemetryItem):
    '''
    Временное решение
    :param item: TelemetryItem
    :return: 202 success
    '''
    _telemetryStorage.append(item)
    return {"status": "success"}


@app.get("/telemetry/{device_id}", response_model=List[TelemetryItem])
async def telemetry(device_id: str):
    return [item for item in _telemetryStorage if item['device_id'] == device_id]
