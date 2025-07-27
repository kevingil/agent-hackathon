from typing import List, Optional
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from sqlalchemy import or_
from app.database import db
from ..models import StockItem

class InventoryService:
    """Service for handling inventory-related operations."""
    
    @staticmethod
    def create_stock_item(
        name: str, 
        description: str, 
        cost: float, 
        list_price: float, 
        quantity: int
    ) -> StockItem:
        """Create a new stock item."""
        try:
            with current_app.app_context():
                item = StockItem(
                    name=name,
                    description=description,
                    cost=cost,
                    list_price=list_price,
                    quantity=quantity
                )
                db.session.add(item)
                db.session.commit()
                return item
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to create stock item: {str(e)}")
    
    @staticmethod
    def get_stock_item(item_id: int) -> Optional[StockItem]:
        """Get a stock item by ID."""
        with current_app.app_context():
            return StockItem.query.get(item_id)
    
    @staticmethod
    def update_stock_item(
        item_id: int, 
        **updates
    ) -> Optional[StockItem]:
        """Update a stock item."""
        try:
            with current_app.app_context():
                item = StockItem.query.get(item_id)
                if not item:
                    return None
                
                for key, value in updates.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
                
                item.updated_at = datetime.utcnow()
                db.session.commit()
                return item
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to update stock item: {str(e)}")
    
    @staticmethod
    def delete_stock_item(item_id: int) -> bool:
        """Delete a stock item."""
        try:
            with current_app.app_context():
                item = StockItem.query.get(item_id)
                if not item:
                    return False
                
                db.session.delete(item)
                db.session.commit()
                return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to delete stock item: {str(e)}")
    
    @staticmethod
    def list_stock_items(
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: bool = False
    ) -> List[StockItem]:
        """List stock items with optional filtering."""
        with current_app.app_context():
            query = StockItem.query
            
            if search:
                query = query.filter(
                    or_(
                        StockItem.name.ilike(f"%{search}%"),
                        StockItem.description.ilike(f"%{search}%")
                    )
                )
                
            if min_price is not None:
                query = query.filter(StockItem.list_price >= min_price)
                
            if max_price is not None:
                query = query.filter(StockItem.list_price <= max_price)
                
            if in_stock:
                query = query.filter(StockItem.quantity > 0)
                
            return query.order_by(StockItem.name).all()
    
    @staticmethod
    def update_inventory(item_id: int, quantity_change: int) -> Optional[StockItem]:
        """Update the inventory quantity of a stock item."""
        try:
            with current_app.app_context():
                item = StockItem.query.get(item_id)
                if not item:
                    return None
                
                new_quantity = item.quantity + quantity_change
                if new_quantity < 0:
                    raise ValueError("Insufficient stock")
                
                item.quantity = new_quantity
                item.updated_at = datetime.utcnow()
                db.session.commit()
                return item
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to update inventory: {str(e)}")
