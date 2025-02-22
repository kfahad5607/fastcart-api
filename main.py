from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.v1.routes import products, orders
from models.products import Product
from models.orders import Order, OrderItem
from db.sql import init_db
from utils.exceptions import BaseAppException
from utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("server is starting")
    await init_db()
    yield
    logger.critical("server is shutting down")

app = FastAPI(debug=True, lifespan=lifespan)

@app.exception_handler(BaseAppException)
async def app_exception_handler(request, exc):
    import traceback
    logger.exception(f"Application error traceback starts ==>")
    logger.error(traceback.format_exc())
    logger.exception(f"Application error traceback ends\n")
    logger.exception(f"Application error msg ==> {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )    

# Include routers
app.include_router(
    products.router, 
    prefix="/api/v1/products", 
    tags=["products"]
)
app.include_router(
    orders.router, 
    prefix="/api/v1/orders", 
    tags=["orders"]
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
