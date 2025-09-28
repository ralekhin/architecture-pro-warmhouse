from uuid import UUID, uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import asyncpg


app = FastAPI(title="Device Hub Service", version="0.1.0")

# todo: env
DATABASE_URL = "postgres://postgres:postgres@postgres:5432/smarthome"

@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)


@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()


class DeviceBase(BaseModel):
    name: str
    type: str
    location: str
    status: str


class DeviceCreate(DeviceBase):
    pass


class DeviceResponse(DeviceBase):
    id: UUID

    class Config:
        from_attributes = True


class DeviceRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.db = pool

    async def get_all_devices(self) -> List[DeviceResponse]:
        async with self.db.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM devices")
            return [DeviceResponse(**dict(row)) for row in rows]

    async def create_device(self, device: DeviceCreate) -> UUID:
        async with self.db.acquire() as conn:
            device_id = uuid4()
            await conn.execute(
                "INSERT INTO devices (id, name, type, location, status) VALUES ($1, $2, $3, $4, $5)",
                device_id,
                device.name,
                device.type,
                device.location,
                device.status
            )
            return device_id


    async def update_status(self, device_id: UUID, status: str) -> None:
        async with self.db.acquire() as conn:
            result = await conn.execute(
                "UPDATE devices SET status = $1 WHERE id = $2",
                status,
                device_id
            )
            if result == "UPDATE 0":
                raise HTTPException(status_code=404, detail="Device not found")


@app.get("/devices", response_model=List[DeviceResponse])
async def get_devices():
    repo = DeviceRepository(app.state.pool)
    return await repo.get_all_devices()

@app.post("/devices", response_model=UUID)
async def create_device(device: DeviceCreate):
    repo = DeviceRepository(app.state.pool)
    return await repo.create_device(device)

@app.patch("/devices/{device_id}/status")
async def update_status(device_id: UUID, status: str):
    repo = DeviceRepository(app.state.pool)
    await repo.update_status(device_id, status)
    return {"message": "Status updated successfully"}
