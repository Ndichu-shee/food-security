from .database import db


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)


class Produce(db.Model):
    __tablename__ = "produce"
    produce_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))


class ProcessedFood(db.Model):
    __tablename__ = "processed_food"
    processed_food_id = db.Column(db.Integer, primary_key=True)
    produce_id = db.Column(db.Integer, db.ForeignKey("produce.produce_id"))
    quantity = db.Column(db.Integer, nullable=False)


class Order(db.Model):
    __tablename__ = "orders"
    order_id = db.Column(db.Integer, primary_key=True)
    consumer_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    staff_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    order_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    status = db.Column(db.String(20), nullable=False)


class OrderItem(db.Model):
    __tablename__ = "order_items"
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"))
    produce_id = db.Column(db.Integer, db.ForeignKey("produce.produce_id"))
    processed_food_id = db.Column(
        db.Integer, db.ForeignKey("processed_food.processed_food_id")
    )
    quantity = db.Column(db.Integer, nullable=False)
