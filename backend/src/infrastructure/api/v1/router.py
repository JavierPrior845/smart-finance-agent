from fastapi import APIRouter

api_router = APIRouter(prefix="/v1")


@api_router.get("/status")
async def get_v1_status():
    return {"api_version": "v1", "status": "active"}
