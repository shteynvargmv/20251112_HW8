from fastapi import APIRouter
from routers.auth import router as auth_router
from routers.booking import router as booking_router

main_router = APIRouter()

main_router.include_router(auth_router, tags=['Аутентификация'])
main_router.include_router(booking_router, tags=['Бронирование'])