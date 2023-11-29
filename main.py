from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import motor.motor_asyncio
from typing import List
import os
from dotenv import load_dotenv
from models.products import Product, ProductCreate, ProductUpdate

app = FastAPI()


# Load environment variables from .env file
load_dotenv()
# MongoDB configuration
MONGO_DB = "ecomm"
MONGO_COLLECTION_PRODUCTS = "products"
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# MongoDB connection setup
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
database = client[MONGO_DB]
products_collection = database[MONGO_COLLECTION_PRODUCTS]

@app.post("/products/", response_model=Product)
async def create_product(product: ProductCreate):
    # Convert Pydantic model to dict for MongoDB
    product_dict = product.dict()

    # Insert the product into MongoDB
    result = await products_collection.insert_one(product_dict)

    # Assign the inserted document's ID back to the Pydantic model
    product._get_valueid = str(result.inserted_id)

    return product

@app.get("/products/{product_id}", response_model=Product)
async def read_product(product_id: str):
    # Query MongoDB for the product with the specified ID
    result = await products_collection.find_one({"_id": product_id})

    # If the product is not found, raise an HTTPException
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Convert the MongoDB document to a Pydantic model
    return Product(**result)

@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate):
    # Query MongoDB for the product with the specified ID
    existing_product = await products_collection.find_one({"_id": product_id})

    # If the product is not found, raise an HTTPException
    if existing_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update the product fields based on the provided update
    update_dict = product_update.dict(exclude_unset=True)
    updated_product = {**existing_product, **update_dict}

    # Update the product in MongoDB
    await products_collection.update_one({"_id": product_id}, {"$set": updated_product})

    # Convert the updated MongoDB document to a Pydantic model
    return Product(**updated_product)

@app.delete("/products/{product_id}", response_model=Product)
async def delete_product(product_id: str):
    # Query MongoDB for the product with the specified ID
    result = await products_collection.find_one({"_id": product_id})

    # If the product is not found, raise an HTTPException
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete the product from MongoDB
    await products_collection.delete_one({"_id": product_id})

    # Convert the deleted MongoDB document to a Pydantic model
    return Product(**result)

@app.get("/products/", response_model=List[Product])
async def list_products():
    # Retrieve all products from MongoDB
    products = await products_collection.find().to_list(length=1000)
    # Convert the list of MongoDB documents to a list of Pydantic models
    return [Product(**product) for product in products]
