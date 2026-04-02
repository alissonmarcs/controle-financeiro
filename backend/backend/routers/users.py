from fastapi import APIRouter, HTTPException, status, Depends

from backend.schemas import Message

router = APIRouter()

@router.get('/users/', response_model=Message)
def get_users():
    return {'message': 'hello'}