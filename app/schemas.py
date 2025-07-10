from pydantic import BaseModel, EmailStr
from enum import Enum
from app.models import UserRole, OrderStatus
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: EmailStr
    role: UserRole

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    product: Product

    class Config:
        orm_mode = True

class Cart(BaseModel):
    id: int
    items: List[CartItem]

    class Config:
        orm_mode = True

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    created_at: datetime
    status: OrderStatus
    payment_status: str
    shipping_status: str
    tracking_number: str | None = None
    shipping_carrier: str | None = None

    class Config:
        orm_mode = True

class OrderItemDetail(BaseModel):
    product_id: int
    product_name: str 
    quantity: int
    price: float

    class Config:
        orm_mode = True

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float
class OrderItem(BaseModel):
    product_name: Optional[str] = None
    quantity: int
    price: float

    class Config:
        orm_mode = True
class OrderBase(BaseModel):
    customer_name: str
    shipping_address: str
    total_amount: float
    status: str  # E.g., "pending", "shipped", etc.
class Order(BaseModel):
    id: int
    customer_name: Optional[str] = None
    shipping_address: Optional[str] = None
    total_amount: float
    items: List[OrderItem]  # A list of OrderItems related to this Order

    class Config:
        orm_mode = True

class OrderDetail(BaseModel):
    id: int
    user_id: int
    total_price: float
    created_at: datetime
    status: str
    payment_status: str
    shipping_status: str
    items: List[OrderItemDetail]

    class Config:
        orm_mode = True

class OrderItemSummary(BaseModel):
    product_id: int
    quantity: int
    price: float

    class Config:
        orm_mode = True

class OrderSummary(BaseModel):
    id: int
    user_id: int
    total_price: float
    created_at: datetime
    status: Optional[str]
    payment_status: Optional[str]  
    shipping_status: Optional[str]
    items: List[OrderItemSummary]

    class Config:
        orm_mode = True

class OrderStatusUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    shipping_status: Optional[str] = None

    class Config:
        orm_mode = True

class ProductPaginationResponse(BaseModel):
    products: List[Product]  
    total_count: int  
    
    class Config:
        orm_mode = True
          
class AddressBase(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str
    phone_number: str
    is_default: bool = False  

    class Config:
        orm_mode = True 
class AddressCreate(AddressBase):
    pass

class AddressUpdate(AddressBase):
    pass
class Address(AddressBase):
    id: int

    class Config:
        orm_mode = True
class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str

class OrderResponse(BaseModel):
    id: int
    total_price: float
    created_at: datetime
    status: OrderStatus
    payment_status: str

    class Config:
        orm_mode = True