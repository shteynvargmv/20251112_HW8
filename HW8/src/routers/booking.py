"""Endpoint-ы бронирования авиабилетов FastAPI."""
import sys
from pathlib import Path as lPath
from typing import Optional

import jwt

from fastapi import APIRouter, Cookie, Depends, FastAPI, HTTPException, Path, Request

sys.path.append(str(lPath(__file__).parent.parent))

from dotenv import dotenv_values

from menus.booking import Booking
from schemas.booking import BookingSchema
from services.fly_service import FlyService

env_path = lPath(__file__).parent.parent/ '.env'
dotenv = dotenv_values(env_path)

router = APIRouter(prefix='', tags=['Бронирование'])

service = FlyService()
app = FastAPI()

@router.get('/sflights/', summary='Просмотреть список рейсов')
def sflights():
    """Просмотреть список рейсов."""   
    service = FlyService()
    sflights = service.get_spfli_sflight((),())
    if len(sflights) > 0:
        return sflights
    else:
        raise HTTPException(status_code=404, detail='Рейсы не найдены')

@router.get('/bookings/', summary='Просмотреть список бронирований')
def bookings():
    """Просмотреть список бронирований."""
    bookings = service.get_bookings_ext()
    if bookings: 
        return bookings
    else:
        raise HTTPException(status_code=404, detail='Бронирования не найдены')

@router.get('/bookings/{bookid}', summary='Просмотреть бронирование')
def booking(
    bookid: int = Path(gt=0)):
    """Просмотреть бронирование."""
    bookings = service.get_bookings_ext(bookid)
    if bookings: 
        return bookings
    else:
        raise HTTPException(status_code=404, detail='Бронирование не найдено')


async def get_token_from_cookies_async(access_token: Optional[str] = Cookie(None, alias='access_token')) -> str:
    """Получение токена из куки."""
    if not access_token:
        raise HTTPException(status_code=401, detail='Token missing')
    return access_token

def get_token_from_cookies_sync(access_token: Optional[str] = Cookie(None, alias='access_token')) -> str:
    """Получение токена из куки."""
    if not access_token:
        raise HTTPException(status_code=401, detail='Token missing')
    return access_token

@router.post('/bookings/', summary='Создать бронирование', dependencies=[Depends(get_token_from_cookies_sync)])
def new_booking(booking:BookingSchema,
                request:Request):
    """Создать новое бронирование."""
    flight = f'{booking.carrcode}{booking.connid} {booking.fldate}'
    
    token = request.cookies.get(dotenv['JWT_ACCESS_COOKIE_NAME'])
    try:
        payload = jwt.decode(
                token, 
                dotenv['JWT_SECRET_KEY'],
                algorithms=['HS256']
        )            
        phone = payload.get('sub')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) # noqa: B904
    
    service = FlyService()
    service.set_customid(phone)
    service.get_spfli_sflight(('scarr.carrcode','spfli.connid'),(booking.carrcode,booking.connid))
    res = Booking(service).booking(flight, booking.pass_count)
    if len(res) > 0:
        bookids = ', '.join(str(bookid) for bookid in res)
        return {
            'success': True,
            'message': f'Успешно забронировано: {bookids}'
        }
    else:
        raise HTTPException(status_code=400, detail=f'Бронирование не создано {flight}')
    

    
@router.delete('/bookings/{bookid}', summary='Удалить бронирование', dependencies=[Depends(get_token_from_cookies_sync)])
def delete_booking(request:Request, bookid:int = Path(gt=0)):
    """Удалить бронирование."""
    token = request.cookies.get(dotenv['JWT_ACCESS_COOKIE_NAME'])
    try:
        payload = jwt.decode(
                token, 
                dotenv['JWT_SECRET_KEY'],
                algorithms=['HS256']
        )            
        phone = payload.get('sub')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # noqa: B904
    
    service = FlyService()
    sbook = service.get_sbook(('sbook.bookid',), (bookid,))
    if len(sbook) > 0:
        if sbook[0].customid != phone:
            raise HTTPException(status_code=403, detail=f'Бронирование {bookid} принадлежит другому пользователю. Удаление невозможно')       
        sflight = service.get_spfli_sflight(
            ('scarr.carrcode','spfli.connid','sflight.fldate'),
            (sbook[0].carrcode,sbook[0].connid,sbook[0].fldate))
        if len(sflight) > 0:
            sflight[0].seatsocc -= 1
            service.update_sflight(sflight[0])
        service.del_sbook(bookid)
        sbook = service.get_sbook(('sbook.bookid',), (bookid,))
        if len(sbook) == 0:
            return {
                'success': True,
                'message': f'Успешно удалено: {bookid}'
                }
        else:
            raise HTTPException(status_code=400, detail=f'Бронирование не удалено {bookid}')
    else:
        raise HTTPException(status_code=404, detail=f'Бронирование {bookid} не найдено')





