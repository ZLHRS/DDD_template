from fastapi import APIRouter

from .schemas import HealthCheckResponse


router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthCheckResponse)
async def health_check_handler() -> HealthCheckResponse:
    return HealthCheckResponse()


health_router = router
