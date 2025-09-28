from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime as dt
import random

app = FastAPI(title="Temperature API", version="0.1.0")


DEFAULT_SENSOR_LOCATION = {
    "1": "Living Room",
    "2": "Bedroom",
    "3": "Kitchen"
}


class TemperatureResponse(BaseModel):
    sensor_id: str
    location: str
    value: float
    timestamp: dt
    status: str



@app.get("/temperature", response_model=TemperatureResponse)
@app.get("/temperature/{sensorId}", response_model=TemperatureResponse)
async def temperature_by_location(
    location: Optional[str] = None,
    sensorId: Optional[str] = None,
):
    if not location:
        location = DEFAULT_SENSOR_LOCATION.get(sensorId, "Unknown")
    if not sensorId:
        sensorId = {v: k for k, v in DEFAULT_SENSOR_LOCATION.items()}.get(location, "0")

    return TemperatureResponse(
        sensor_id = sensorId,
        location = location,
        value = round(random.uniform(0.0, 50.0), 1),
        timestamp = dt.now().isoformat() + "Z",
        status = "active"
    )
