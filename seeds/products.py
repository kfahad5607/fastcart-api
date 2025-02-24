import argparse
from random import randint, uniform
from faker import Faker
from models.products import Product
from db.sql import get_session
from sqlmodel import select, delete
from utils.logger import logger

BATCH_SIZE = 500

def generate_fake_products(n=50):
    fake = Faker()
    products = []

    # Generate fake products
    for i in range(n):
        product = Product(
            name=f"Product {i + 1}",
            description=fake.sentence(),
            price=round(uniform(5.0, 500.0), 2),
            stock=randint(10, 100),
        )
        products.append(product)

    return products

async def seed_products(n=1000, clear_existing=False):
    try:
        session_gen = get_session()
        session = await session_gen.__anext__()

        if not clear_existing:
            first_product_stmt = select(Product.id).limit(1)
            results = await session.execute(first_product_stmt)
            first_product = results.scalars().first()
            if first_product:
                logger.info(f"Database already contains data, skipping seeding.!")
                return

        if clear_existing:
            stmt = delete(Product)
            await session.execute(stmt)
            await session.commit()
        
        _n = n
        while _n > 0:
            curr_batch = min(_n, BATCH_SIZE)
            products = generate_fake_products(curr_batch)
            session.add_all(products)
            await session.commit()

            _n = _n - BATCH_SIZE
            
            logger.info(f"Seeded batch with {curr_batch} products successfully!")
        logger.info(f"Seeded all {n} products successfully!")
    except Exception as e:
        logger.error(f"Exception in seed_products ==> {e}")

def parse_args():
    parser = argparse.ArgumentParser(description="Seed products script")
    parser.add_argument("-n", type=int, help="Number of products to seed", required=False)
    parser.add_argument("--clear_existing", action="store_true", help="Clear existing products before seeding")
    return parser.parse_args()

if __name__ == "__main__":
    import asyncio

    args = parse_args()
    n = args.n if args.n else 200
    clear_existing = bool(args.clear_existing)

    asyncio.run(seed_products(n=n, clear_existing=clear_existing))
