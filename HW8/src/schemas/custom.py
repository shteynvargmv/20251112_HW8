"""Схема для пользователей."""
import re

from pydantic import BaseModel, Field, field_validator


class CustomLoginSchema(BaseModel):
    """Схема пользователя для авторизации."""
    phone:str
    password:str = Field(max_len = 20)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, values: str) -> str:
        """Валидация номера телефона."""
        if not re.match(r'^\d{1,15}$', values):
            raise ValueError('Номер телефона должен содержать от 1 до 15 цифр')
        return values