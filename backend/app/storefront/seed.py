import os
import random
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import create_app
from app.database import db
from app.storefront.models import StockItem, Order, OrderItem
from app.storefront.services.inventory import InventoryService

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app()
app.app_context().push()

# Initialize database
db.create_all()

try:
        # Define product categories and their items
    categories = {
        'Electronics': [
            ('Laptop', 'High-performance business laptop', 800.00, 1299.99, 25),
            ('Smartphone', 'Latest model smartphone', 700.00, 999.99, 30),
            ('Tablet', '10-inch touchscreen tablet', 250.00, 399.99, 40),
            ('Monitor', '27-inch 4K monitor', 350.00, 599.99, 20),
            ('Keyboard', 'Mechanical gaming keyboard', 60.00, 129.99, 50),
            ('Mouse', 'Wireless ergonomic mouse', 25.00, 49.99, 75),
            ('Headphones', 'Wireless noise-cancelling', 120.00, 249.99, 60),
            ('Smartwatch', 'Fitness tracking smartwatch', 150.00, 299.99, 45),
            ('Router', 'Wi-Fi 6 router', 120.00, 229.99, 30),
            ('External SSD', '1TB portable SSD', 80.00, 149.99, 50),
        ],
        'Office Supplies': [
            ('Desk Chair', 'Ergonomic office chair', 120.00, 249.99, 15),
            ('Standing Desk', 'Electric height-adjustable desk', 350.00, 599.99, 10),
            ('File Cabinet', '2-drawer letter size', 90.00, 179.99, 20),
            ('Desk Lamp', 'LED adjustable desk lamp', 25.00, 49.99, 40),
            ('Whiteboard', '4x6 feet magnetic whiteboard', 70.00, 129.99, 15),
            ('Stapler', 'Heavy-duty stapler', 8.00, 19.99, 100),
            ('Paper Shredder', '12-sheet cross-cut', 60.00, 119.99, 25),
            ('Desk Organizer', 'Multi-compartment organizer', 15.00, 29.99, 60),
            ('Printer Paper', 'Letter size, 10-ream case', 30.00, 59.99, 30),
            ('Ink Cartridge', 'Compatible black ink', 15.00, 34.99, 80),
        ],
        'Networking': [
            ('Network Switch', '24-port gigabit switch', 200.00, 399.99, 12),
            ('Wireless AP', 'Ceiling mount access point', 150.00, 299.99, 18),
            ('Patch Panel', '48-port cat6 patch panel', 80.00, 149.99, 25),
            ('Network Rack', '12U wall-mount rack', 150.00, 279.99, 8),
            ('Ethernet Cable', 'Cat6, 25ft', 5.00, 12.99, 200),
            ('Fiber Optic Cable', 'Single-mode, 10m', 25.00, 49.99, 40),
            ('Patch Cable', 'Cat6, 3ft, 5-pack', 12.00, 24.99, 60),
            ('Network Tool Kit', 'Basic networking tools', 50.00, 99.99, 15),
            ('Cable Tester', 'Network cable tester', 30.00, 59.99, 25),
            ('Rack Shelf', '1U universal shelf', 25.00, 49.99, 30),
        ],
        'Security': [
            ('Surveillance Camera', '4K IP camera', 120.00, 229.99, 20),
            ('NVR System', '8-channel NVR with 4TB', 400.00, 749.99, 8),
            ('Biometric Scanner', 'Fingerprint access control', 200.00, 399.99, 12),
            ('Security DVR', '16-channel 1080p DVR', 250.00, 449.99, 10),
            ('Motion Sensor', 'Wireless motion detector', 30.00, 59.99, 40),
            ('Door Access Kit', 'Keycard entry system', 150.00, 279.99, 15),
            ('Security Signage', '4-pack warning signs', 15.00, 29.99, 30),
            ('Security Camera Mount', 'Outdoor junction box', 20.00, 39.99, 35),
            ('CCTV Power Supply', '8-port power box', 35.00, 69.99, 25),
            ('BNC Connector', 'Pack of 10', 8.00, 19.99, 50),
        ],
        'Audio/Video': [
            ('Conference Phone', 'Full-duplex speakerphone', 250.00, 449.99, 15),
            ('PTZ Camera', 'Conference camera', 300.00, 549.99, 10),
            ('Audio Mixer', '8-channel audio mixer', 200.00, 379.99, 8),
            ('Wireless Mic', 'UHF wireless microphone', 150.00, 279.99, 12),
            ('Ceiling Speaker', '70V ceiling speaker', 80.00, 149.99, 25),
            ('HDMI Switcher', '4x1 HDMI switcher', 40.00, 79.99, 30),
            ('Projector Screen', '120" motorized screen', 200.00, 379.99, 8),
            ('Audio Cable', 'XLR cable, 25ft', 15.00, 29.99, 50),
            ('Speaker Stand', 'Adjustable speaker stand', 35.00, 69.99, 20),
            ('Tabletop Mic Stand', 'Adjustable boom arm', 20.00, 39.99, 35),
        ],
    }
    
    # Add more variations to reach 200+ items
    brands = ['Pro', 'Elite', 'Business', 'Enterprise', 'Premium', 'Advanced', 'Ultra', 'Max', 'Plus', 'Turbo']
    colors = ['Black', 'White', 'Silver', 'Gray', 'Blue', 'Red']
    
    # Create inventory service instance with db session
    inventory_service = InventoryService()
    
    # Add items from predefined categories
    items = []
    for category, products in categories.items():
        for name, desc, cost, price, qty in products:
            # Add some variations
            for brand in random.sample(brands, 2):
                for color in random.sample(colors, 2):
                    item_name = f"{brand} {name} ({color})"
                    item_desc = f"{desc} - {color} {brand} edition"
                    # Add some random variation to pricing
                    cost_variation = cost * random.uniform(0.9, 1.1)
                    price_variation = price * random.uniform(0.9, 1.2)
                    qty_variation = max(1, int(qty * random.uniform(0.8, 1.5)))
                    
                    item = inventory_service.create_stock_item(
                        name=item_name,
                        description=item_desc,
                        cost=round(Decimal(cost_variation), 2),
                        list_price=round(Decimal(price_variation), 2),
                        quantity=qty_variation
                    )
                    items.append(item)
    
    # Add some additional random items to reach 200+
    additional_items = [
        ('USB Hub', '4-port USB 3.0 hub', 8.00, 19.99, 100),
        ('Laptop Stand', 'Adjustable aluminum stand', 15.00, 34.99, 60),
        ('Webcam Cover', 'Sliding privacy cover', 2.00, 7.99, 200),
        ('Cable Ties', '100-pack assorted colors', 3.00, 9.99, 150),
        ('Screen Cleaner Kit', 'Includes microfiber cloth', 5.00, 14.99, 120),
        ('Laptop Lock', 'Kensington-style lock', 10.00, 24.99, 80),
        ('Monitor Stand', 'Ergonomic riser stand', 25.00, 49.99, 40),
        ('USB-C Adapter', 'Multi-port adapter', 20.00, 44.99, 75),
        ('Wireless Charger', 'Qi-certified charger', 25.00, 54.99, 60),
        ('Laptop Sleeve', 'Neoprene 15" sleeve', 10.00, 24.99, 90),
    ]
    
    for name, desc, cost, price, qty in additional_items:
        for color in random.sample(colors, 2):
            item_name = f"{random.choice(brands)} {name} ({color})"
            item_desc = f"{desc} - {color} color"
            item = inventory_service.create_stock_item(
                name=item_name,
                description=item_desc,
                cost=round(Decimal(cost * random.uniform(0.9, 1.1)), 2),
                list_price=round(Decimal(price * random.uniform(0.9, 1.2)), 2),
                quantity=max(1, int(qty * random.uniform(0.8, 1.2)))
            )
            items.append(item)
    
    print(f"Created {len(items)} stock items")
    
    # # Create an order with multiple items
    # order1 = Order(status='completed')
    # order1.items = [
    #     OrderItem(
    #         inventory_item_id=laptop.id,
    #         quantity=1,
    #         unit_cost=laptop.cost,
    #         unit_price=laptop.price
    #     ),
    #     OrderItem(
    #         inventory_item_id=headphones.id,
    #         quantity=2,
    #         unit_cost=headphones.cost,
    #         unit_price=headphones.price
    #     )
    # ]
    
    # # Create a draft order
    # order2 = Order(status='draft')
    # order2.items = [
    #     OrderItem(
    #         inventory_item_id=smartphone.id,
    #         quantity=1,
    #         unit_cost=smartphone.cost,
    #         unit_price=smartphone.price
    #     )
    # ]
    
    # # Add orders to session
    # session.add_all([order1, order2])
    
    # # Calculate and set order totals
    # for order in [order1, order2]:
    #     order.total_amount = sum(item.total_price for item in order.items)
    
    # Commit the transaction
    # db.session.commit()
    print("Database seeded successfully!")

except Exception as e:
    print(f"Error seeding database: {e}")
    db.session.rollback()
finally:
    db.session.remove()
