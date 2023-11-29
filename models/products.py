from pydantic import BaseModel

# Pydantic model for product
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float

class ProductUpdate(BaseModel):
    name: str = None
    description: str = None
    price: float = None

class Product(ProductCreate):
    _id: str