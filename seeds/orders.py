import argparse
from random import randint, choice
from models.products import Product
from models.orders import Order, OrderItem
from db.sql import get_session
from sqlmodel import select, delete
from services.orders import normalize_order_items
from utils.logger import logger

BATCH_SIZE = 20

def generate_fake_order_items(num_orders, products):
    order_list = []
    # Generate fake orders
    for _ in range(num_orders):
        num_items = randint(1, 5)
        order = Order(total_price=0)
        order_total = 0
        order_items = []
        for _ in range(num_items):
            product = choice(products)
            quantity = randint(1, 10)
            unit_price = product['price']
            order_total += quantity * unit_price
            order_item = OrderItem(product_id=product['id'], quantity=quantity, unit_price=unit_price)

            order_items.append(order_item)

        order.total_price = round(order_total, 2)
        order_list.append((order, normalize_order_items(order_items)))

    return order_list

async def seed_orders(n=1000, clear_existing=False):
    try:
        session_gen = get_session()
        session = await session_gen.__anext__()

        if not clear_existing:
            first_order_stmt = select(Order.id).limit(1)
            results = await session.execute(first_order_stmt)
            first_order = results.scalars().first()
            if first_order:
                logger.info(f"Database already contains data, skipping seeding.!")
                return

        if clear_existing:
            stmt = delete(Order)
            await session.execute(stmt)
            await session.commit()

        products_stmt = select(Product.id, Product.price).limit(1000)
        product_results = await session.execute(products_stmt)
        products = product_results.mappings().all()

        if not products:
            raise Exception('No products found.')

        # products = products[:2]

        # logger.info(f"{products=}")

        _n = n
        while _n > 0:
            curr_batch = min(_n, BATCH_SIZE)
            order_list = generate_fake_order_items(curr_batch, products)

            for order, order_items in order_list:
                session.add(order)
                for o in order_items:
                    o.order = order
                session.add_all(order_items)

            await session.commit()

            _n = _n - BATCH_SIZE
            
            logger.info(f"Seeded batch with {curr_batch} orders successfully!")
        logger.info(f"Seeded all {n} orders successfully!")
    except Exception as e:
        logger.error(f"Exception in seed_orders ==> {e}")

def parse_args():
    parser = argparse.ArgumentParser(description="Seed orders script")
    parser.add_argument("-n", type=int, help="Number of orders to seed", required=False)
    parser.add_argument("--clear_existing", action="store_true", help="Clear existing orders before seeding")
    return parser.parse_args()

if __name__ == "__main__":
    import asyncio

    args = parse_args()
    n = args.n if args.n else 200
    clear_existing = bool(args.clear_existing)

    asyncio.run(seed_orders(n=n, clear_existing=clear_existing))
