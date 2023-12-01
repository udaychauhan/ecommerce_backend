from pydantic import BaseModel, Field
from typing import Optional, List
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]

# Pydantic model for product
class Product(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    description: str
    price: float

class ProductUpdate(BaseModel):
    name: str = None
    description: str = None
    price: float = None


class ProductCollection(BaseModel):
    products: List[Product]