from typing import List, Dict
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update
from db.sql import get_session
from models.orders import Order, OrderItem, OrderCreate, OrderItemCreate
from models.products import Product, OrderWithProductRead
from utils.exceptions import BaseAppException, ValidationException
from utils.logger import logger

router = APIRouter()

def normalize_order_items(order_items: List[OrderItemCreate]):
    order_items_dict: Dict[int, int] = {}
    normalized_order_items: List[OrderItemCreate] = []

    for order_item in order_items:
        exist_prod_idx = order_items_dict.get(order_item.product_id)
        if exist_prod_idx is not None:
            normalized_order_items[exist_prod_idx].quantity += order_item.quantity
        else:
            normalized_order_items.append(order_item)
            order_items_dict[order_item.product_id] = len(normalized_order_items) - 1
        
    return normalized_order_items

@router.get("/")
async def get_orders():
    try:
        return {
            'current_page': 1,
            'page_size': 10,
            'total_records': 100,
            'total_pages': 10,
            'data': []
        }
    except Exception as e:
        logger.error(f"Exception in get_orders ==> {e}")

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderWithProductRead)
async def create_order(order_create: OrderCreate, session: AsyncSession=Depends(get_session)):
    try:
        order_create.items = normalize_order_items(order_create.items)
        product_ids = [p.product_id for p in order_create.items]

        stmt = select(Product.id, Product.name, Product.stock, Product.price).where(Product.id.in_(product_ids)).with_for_update()
        products = await session.execute(stmt)
        product_dict = { p.id: p for p in products}

        missing_products = set()
        order_items = []
        updated_products = []
        created_order = {
            "items": [],
            "total_price": 0
        }

        for order_item in order_create.items:
            product_id = order_item.product_id
            product = product_dict.get(product_id)

            if not product:
                missing_products.add(str(product_id))
            elif order_item.quantity > product.stock:
                raise ValidationException(
                    message=f"Insufficient stock for Product ID {product_id}. Requested: {order_item.quantity}, Available: {product.stock}"
                )
            else:
                updated_products.append({
                    'id': product.id,
                    'stock': product.stock - order_item.quantity,
                })
                created_order['items'].append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'quantity': order_item.quantity,
                    'price': product.price,
                })
                created_order['total_price'] += product.price * order_item.quantity
                
                new_order_item = OrderItem(product_id=order_item.product_id, quantity=order_item.quantity, unit_price=product.price)
                order_items.append(new_order_item) 

        if missing_products:
            raise ValidationException(
                message=f"Products not found for IDs: {', '.join(missing_products)}"
            )

        new_order = Order(total_price=created_order['total_price'])
        for order_item in order_items:
            order_item.order = new_order

        await session.execute(update(Product), updated_products)
        session.add_all(order_items)
        await session.commit()

        # new_order_data = {field.name: getattr(new_order, field.name) for field in product_public_fields}
        created_order['id'] = new_order.id
        created_order['status'] = new_order.status
        created_order['created_at'] = new_order.created_at

        return created_order

    except ValidationException as e:
        raise
    except Exception as e:
        logger.error(f"Exception in create_order ==> {e}")
        await session.rollback()
        raise BaseAppException("Could not create the order. Please try again later.") from e