from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Numeric, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

class StockItem(Base):
    __tablename__ = 'stock_items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    cost = Column(Numeric(10, 2), nullable=False)  # Cost to us
    list_price = Column(Numeric(10, 2), nullable=False)  # Selling price
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    po_number = Column(String(100), unique=True, nullable=False, default=lambda: str(uuid4())[:8].upper())
    status = Column(String(50), default='draft')  # draft, submitted, processing, shipped, completed, cancelled
    total_amount = Column(Numeric(10, 2), default=0.00)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    stock_item_id = Column(Integer, ForeignKey('stock_items.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)  # Cost at time of order
    unit_price = Column(Numeric(10, 2), nullable=False)  # Price at time of order
    
    # Relationships
    order = relationship("Order", back_populates="items")
    stock_item = relationship("StockItem")
    
    @property
    def total_cost(self):
        return self.unit_cost * self.quantity
        
    @property
    def total_price(self):
        return self.unit_price * self.quantity
