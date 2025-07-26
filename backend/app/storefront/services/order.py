from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from decimal import Decimal
from app.database import db
from ..models import Order, OrderItem, StockItem
from .inventory import InventoryService

class OrderService:
    """Service for handling order and cart operations."""
    
    @staticmethod
    def create_order(user_id: Optional[int] = None, **kwargs) -> Order:
        """Create a new order (cart)."""
        try:
            order = Order(
                user_id=user_id,
                status='draft',  # Start as draft (cart)
                total_amount=Decimal('0.00'),
                **kwargs
            )
            db.session.add(order)
            db.session.commit()
            return order
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to create order: {str(e)}")
    
    @staticmethod
    def get_order(order_id: int) -> Optional[Order]:
        """Get an order by ID."""
        return Order.query.get(order_id)
    
    @staticmethod
    def get_user_cart(user_id: int) -> Optional[Order]:
        """Get or create a user's cart (draft order)."""
        cart = Order.query.filter_by(user_id=user_id, status='draft').first()
        if not cart:
            cart = OrderService.create_order(user_id=user_id)
        return cart
    
    @staticmethod
    def add_item_to_cart(
        order_id: int, 
        stock_item_id: int, 
        quantity: int = 1
    ) -> Order:
        """Add an item to the cart (draft order)."""
        try:
            # Get the order and stock item
            order = Order.query.get(order_id)
            if not order:
                raise ValueError("Order not found")
                
            if order.status != 'draft':
                raise ValueError("Can only add items to a draft order")
                
            stock_item = StockItem.query.get(stock_item_id)
            if not stock_item:
                raise ValueError("Stock item not found")
                
            if stock_item.quantity < quantity:
                raise ValueError("Insufficient stock")
            
            # Check if item already in order
            order_item = next(
                (item for item in order.items if item.stock_item_id == stock_item_id), 
                None
            )
            
            if order_item:
                # Update existing item
                order_item.quantity += quantity
            else:
                # Add new item
                order_item = OrderItem(
                    order_id=order_id,
                    stock_item_id=stock_item_id,
                    quantity=quantity,
                    unit_cost=stock_item.cost,
                    unit_price=stock_item.list_price
                )
                db.session.add(order_item)
            
            # Update order total
            OrderService._update_order_totals(order)
            db.session.commit()
            
            return order
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to add item to cart: {str(e)}")
    
    @staticmethod
    def update_cart_item_quantity(
        order_id: int, 
        item_id: int, 
        new_quantity: int
    ) -> Order:
        """Update the quantity of an item in the cart."""
        try:
            order = Order.query.get(order_id)
            if not order:
                raise ValueError("Order not found")
                
            if order.status != 'draft':
                raise ValueError("Can only update items in a draft order")
                
            order_item = next(
                (item for item in order.items if item.id == item_id), 
                None
            )
            
            if not order_item:
                raise ValueError("Item not found in order")
                
            if new_quantity <= 0:
                return OrderService.remove_item_from_cart(order_id, item_id)
                
            stock_item = order_item.stock_item
            if stock_item.quantity < new_quantity:
                raise ValueError("Insufficient stock")
                
            order_item.quantity = new_quantity
            OrderService._update_order_totals(order)
            db.session.commit()
            
            return order
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to update cart item: {str(e)}")
    
    @staticmethod
    def remove_item_from_cart(order_id: int, item_id: int) -> Order:
        """Remove an item from the cart."""
        try:
            order = Order.query.get(order_id)
            if not order:
                raise ValueError("Order not found")
                
            if order.status != 'draft':
                raise ValueError("Can only remove items from a draft order")
                
            order_item = next(
                (item for item in order.items if item.id == item_id), 
                None
            )
            
            if not order_item:
                raise ValueError("Item not found in order")
                
            db.session.delete(order_item)
            OrderService._update_order_totals(order)
            db.session.commit()
            
            return order
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to remove item from cart: {str(e)}")
    
    @staticmethod
    def place_order(order_id: int) -> Order:
        """Place an order (convert from draft to placed)."""
        try:
            order = Order.query.get(order_id)
            if not order:
                raise ValueError("Order not found")
                
            if order.status != 'draft':
                raise ValueError("Only draft orders can be placed")
                
            # Check stock availability
            for item in order.items:
                stock_item = item.stock_item
                if stock_item.quantity < item.quantity:
                    raise ValueError(f"Insufficient stock for item: {stock_item.name}")
            
            # Update inventory
            for item in order.items:
                InventoryService.update_inventory(
                    item.stock_item_id, 
                    -item.quantity  # Deduct from inventory
                )
            
            # Update order status
            order.status = 'submitted'
            order.submitted_at = datetime.utcnow()
            db.session.commit()
            
            return order
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to place order: {str(e)}")
    
    @staticmethod
    def cancel_order(order_id: int) -> Order:
        """Cancel an order and return items to inventory."""
        try:
            order = Order.query.get(order_id)
            if not order:
                raise ValueError("Order not found")
                
            if order.status not in ['submitted', 'processing']:
                raise ValueError("Only submitted or processing orders can be cancelled")
            
            # Return items to inventory
            for item in order.items:
                try:
                    InventoryService.update_inventory(
                        item.stock_item_id,
                        item.quantity  # Add back to inventory
                    )
                except Exception as e:
                    # Log the error but continue with other items
                    print(f"Error returning item {item.id} to inventory: {str(e)}")
            
            # Update order status
            order.status = 'cancelled'
            order.cancelled_at = datetime.utcnow()
            db.session.commit()
            
            return order
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to cancel order: {str(e)}")
    
    @staticmethod
    def list_orders(
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Order]:
        """List orders with optional filtering."""
        query = Order.query
        
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
            
        if status is not None:
            query = query.filter_by(status=status)
            
        return query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def _update_order_totals(order: Order) -> None:
        """Update the order totals based on its items."""
        order.total_amount = sum(
            item.quantity * item.unit_price 
            for item in order.items
        )
        order.updated_at = datetime.utcnow()
    
    @staticmethod
    def get_order_summary(order_id: int) -> Dict[str, Any]:
        """Get a summary of the order with item details."""
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")
            
        items = []
        for item in order.items:
            items.append({
                'id': item.id,
                'stock_item_id': item.stock_item_id,
                'name': item.stock_item.name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.quantity * item.unit_price)
            })
            
        return {
            'id': order.id,
            'status': order.status,
            'total_amount': float(order.total_amount),
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat(),
            'items': items
        }
