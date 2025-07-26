import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, StockItem, Order, OrderItem

# Load environment variables
load_dotenv()

# Create database engine
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DATABASE_URL)

# Create tables if they don't exist
Base.metadata.create_all(engine)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Add sample inventory items
    laptop = StockItem(
        name="Laptop", 
        description="High-performance gaming laptop",
        cost=800.00,
        price=1299.99,
        quantity=10
    )
    
    smartphone = StockItem(
        name="Smartphone", 
        description="Latest model smartphone",
        cost=700.00,
        price=999.99,
        quantity=15
    )
    
    headphones = StockItem(
        name="Headphones", 
        description="Wireless noise-cancelling headphones",
        cost=150.00,
        price=299.99,
        quantity=20
    )
    
    # Add items to session
    session.add_all([laptop, smartphone, headphones])
    session.flush()  # Flush to get IDs
    
    # Create an order with multiple items
    order1 = Order(status='completed')
    order1.items = [
        OrderItem(
            inventory_item_id=laptop.id,
            quantity=1,
            unit_cost=laptop.cost,
            unit_price=laptop.price
        ),
        OrderItem(
            inventory_item_id=headphones.id,
            quantity=2,
            unit_cost=headphones.cost,
            unit_price=headphones.price
        )
    ]
    
    # Create a draft order
    order2 = Order(status='draft')
    order2.items = [
        OrderItem(
            inventory_item_id=smartphone.id,
            quantity=1,
            unit_cost=smartphone.cost,
            unit_price=smartphone.price
        )
    ]
    
    # Add orders to session
    session.add_all([order1, order2])
    
    # Calculate and set order totals
    for order in [order1, order2]:
        order.total_amount = sum(item.total_price for item in order.items)
    
    # Commit the transaction
    session.commit()
    
    print("Database seeded successfully!")
    
except Exception as e:
    print(f"Error seeding database: {e}")
    session.rollback()
finally:
    session.close()
