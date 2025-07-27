from flask import Blueprint, jsonify, request
from app.storefront.services.order import OrderService

orders = Blueprint('orders', __name__)

@orders.route('/api/orders', methods=['GET'])
def get_orders():
    status = request.args.get('status')
    user_id = request.args.get('user_id', type=int)
    orders = OrderService.list_orders(user_id=user_id, status=status)
    result = []
    for order in orders:
        summary = OrderService.get_order_summary(order.id)
        result.append(summary)
    return jsonify(result)

@orders.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        summary = OrderService.get_order_summary(order_id)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 404 
