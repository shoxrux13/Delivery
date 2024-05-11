from pydantic import BaseModel
from typing import  Optional

class SignUpModel(BaseModel):
    id : Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "shoxrux13",
                "email": "woxrux6070@gmail.com",
                "password": "woxrux6070",
                "is_staff": False,
                "is_active": True
            }
        }

class Settings(BaseModel):
    authjwt_secret_key: str = "f2942efb386863c247766aec5a867243538534f5de97d217af8eadebd9c12b2e"


class LoginModel(BaseModel):
    username_or_email: str
    password: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username_or_email": "jhon or jhon@gmail.com",
                "password": "jhon123"
            }
        }    


class OrderModel(BaseModel):
    quantity: int
    order_status: Optional[str] = "PENDING"
    user_id: Optional[int]
    product_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "quantity": 2
            }
        }

class OrderStatusModel(BaseModel):
    order_status: Optional[str] = "PENDING"

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "order_status": "PENDING"
            }
        }
        
class ProductModel(BaseModel):
    name: str
    description: str
    price: int
    quantity: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Iphone 12",
                "description": "Iphone 12 pro max",
                "price": 2000,
                "quantity": 10
            }
        }