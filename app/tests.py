import os
import json
import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import User, Produce, Order, OrderItem
from .database import db
from .routes import main  
from . import create_app

TEST_DATABASE_URI = os.getenv("TEST_DATABASE_URI", "postgresql://user:password@localhost:5432/test_db")

@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def add_user(client):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password",
        "role": "consumer"
    }
    client.post('/register', json=user_data)
    response = client.post('/login', json={
        "email": "test@example.com",
        "password": "password"
    })
    return response.json['access_token']

def test_register(client):
    response = client.post('/register', json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password",
        "role": "consumer"
    })
    assert response.status_code == 201
    assert response.json['message'] == "User registered successfully"

def test_register_duplicate(client):
    client.post('/register', json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password",
        "role": "consumer"
    })
    response = client.post('/register', json={
        "username": "testuser2",
        "email": "test@example.com",
        "password": "password",
        "role": "consumer"
    })
    assert response.status_code == 400
    assert response.json['message'] == "User already exists"

def test_login(client):
    client.post('/register', json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password",
        "role": "consumer"
    })
    response = client.post('/login', json={
        "email": "test@example.com",
        "password": "password"
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_invalid_credentials(client):
    client.post('/register', json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password",
        "role": "consumer"
    })
    response = client.post('/login', json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json['message'] == "Invalid credentials"

def test_add_produce(client, add_user):
    access_token = add_user
    produce_data = {
        "name": "Tomato",
        "price": 1.5,
        "quantity": 100
    }
    response = client.post('/produce', 
                           headers={"Authorization": f"Bearer {access_token}"}, 
                           json=produce_data)
    assert response.status_code == 201
    assert response.json['message'] == "Produce added successfully"

def test_add_produce_unauthenticated(client):
    produce_data = {
        "name": "Tomato",
        "price": 1.5,
        "quantity": 100
    }
    response = client.post('/produce', json=produce_data)
    assert response.status_code == 401  

def test_create_order(client, add_user):
    access_token = add_user
    produce_data = {
        "name": "Tomato",
        "price": 1.5,
        "quantity": 100
    }
    client.post('/produce', 
                headers={"Authorization": f"Bearer {access_token}"}, 
                json=produce_data)
    
    order_data = {
        "produce_id": 1,  
        "quantity": 10
    }
    response = client.post('/orders', 
                           headers={"Authorization": f"Bearer {access_token}"}, 
                           json=order_data)
    assert response.status_code == 201
    assert response.json['message'] == "Order created successfully"

def test_create_order_insufficient_quantity(client, add_user):
    access_token = add_user
    produce_data = {
        "name": "Tomato",
        "price": 1.5,
        "quantity": 5
    }
    client.post('/produce', 
                headers={"Authorization": f"Bearer {access_token}"}, 
                json=produce_data)
    
    order_data = {
        "produce_id": 1,  
        "quantity": 10
    }
    response = client.post('/orders', 
                           headers={"Authorization": f"Bearer {access_token}"}, 
                           json=order_data)
    assert response.status_code == 400
    assert response.json['message'] == "Insufficient quantity available"

def test_get_order(client, add_user):
    access_token = add_user
    produce_data = {
        "name": "Tomato",
        "price": 1.5,
        "quantity": 100
    }
    client.post('/produce', 
                headers={"Authorization": f"Bearer {access_token}"}, 
                json=produce_data)

    order_data = {
        "produce_id": 1,  
        "quantity": 10
    }
    order_response = client.post('/orders', 
                                  headers={"Authorization": f"Bearer {access_token}"}, 
                                  json=order_data)

    order_id = order_response.json['order_id']
    response = client.get(f'/orders/{order_id}', 
                          headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json['order_id'] == order_id
    assert response.json['consumer_id'] == 1  
