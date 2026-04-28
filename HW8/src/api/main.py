"""Система бронирования авиабилетов FastAPI."""
import sys
from pathlib import Path as Path

sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI

from routers import main_router

app = FastAPI(title='User Management API')
app.include_router(main_router)

