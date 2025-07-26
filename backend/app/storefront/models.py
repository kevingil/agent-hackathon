from datetime import datetime
from uuid import uuid4
from app.database import db

class StockItem(db.Model):
    __tablename__ = 'stock_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1000))
    cost = db.Column(db.Numeric(10, 2), nullable=False)  # Cost to us
    list_price = db.Column(db.Numeric(10, 2), nullable=False)  # Selling price
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(100), unique=True, nullable=False, default=lambda: str(uuid4())[:8].upper())
    status = db.Column(db.String(50), default='draft')  # draft, submitted, processing, shipped, completed, cancelled
    total_amount = db.Column(db.Numeric(10, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False)  # Cost at time of order
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)  # Price at time of order
    
    # Relationships
    order = db.relationship("Order", back_populates="items")
    stock_item = db.relationship("StockItem")
    
    @property
    def total_cost(self):
        return self.unit_cost * self.quantity
        
    @property
    def total_price(self):
        return self.unit_price * self.quantity
