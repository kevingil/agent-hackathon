# from flask import Blueprint, jsonify, request
# # from app.user.models import User

# users = Blueprint('users', __name__)

# @users.route('/', methods=['GET'])
# def get_users():
#     users = User.query.all()
#     return jsonify([{
#         'id': user.id,
#         'name': user.name,
#         'email': user.email
#     } for user in users])

# @users.route('/', methods=['POST'])
# def create_user():
#     data = request.get_json()
#     user = User(
#         name=data['name'],
#         email=data['email']
#     )
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({
#         'id': user.id,
#         'name': user.name,
#         'email': user.email
#     }), 201

# @users.route('/<int:user_id>', methods=['GET'])
# def get_user(user_id):
#     user = User.query.get_or_404(user_id)
#     return jsonify({
#         'id': user.id,
#         'name': user.name,
#         'email': user.email
#     })
