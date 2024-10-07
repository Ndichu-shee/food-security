from flask import Blueprint, request, jsonify
from .models import User, Produce, Order, OrderItem
from .database import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return jsonify({"message": "Welcome to Kwanza Tukule API!"})

@main.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    if not username or not email or not password:
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        role=data.get("role"),
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify(message="User registered successfully"), 201

@main.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.user_id)
    return jsonify(access_token=access_token), 200

@main.route("/produce", methods=["POST"])
@jwt_required()
def add_produce():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    name = data.get("name")
    price = data.get("price")
    quantity = data.get("quantity")

    new_produce = Produce(
        name=name, price=price, quantity=quantity, farmer_id=current_user_id
    )

    db.session.add(new_produce)
    db.session.commit()

    return jsonify(message="Produce added successfully"), 201

@main.route("/produce", methods=["GET"])
@jwt_required()
def get_produce():
    produce_list = Produce.query.all()
    results = []

    for produce in produce_list:
        results.append({
            "produce_id": produce.produce_id,
            "name": produce.name,
            "price": produce.price,
            "quantity": produce.quantity,
            "farmer_id": produce.farmer_id
        })

    return jsonify(results), 200

@main.route("/orders", methods=["POST"])
@jwt_required()
def create_order():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    produce_id = data.get("produce_id")
    quantity = data.get("quantity")

    produce = Produce.query.filter_by(produce_id=produce_id).first()
    if not produce:
        return jsonify({"message": "Produce not found"}), 404

    if produce.quantity < quantity:
        return jsonify({"message": "Insufficient quantity available"}), 400

    new_order = Order(consumer_id=current_user_id, status="Pending")
    order_item = OrderItem(order_id=new_order.order_id, produce_id=produce_id, quantity=quantity)

    produce.quantity -= quantity

    db.session.add(new_order)
    db.session.add(order_item)
    db.session.commit()

    return jsonify(message="Order created successfully"), 201

@main.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    items = []
    
    for item in order_items:
        items.append({
            "order_item_id": item.order_item_id,
            "produce_id": item.produce_id,
            "quantity": item.quantity
        })

    return jsonify({
        "order_id": order.order_id,
        "consumer_id": order.consumer_id,
        "staff_id": order.staff_id,
        "order_date": order.order_date,
        "status": order.status,
        "items": items
    }), 200
