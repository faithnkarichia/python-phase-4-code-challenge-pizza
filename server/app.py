#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os
from flask_cors import CORS
from flask import jsonify

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)
CORS(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# from views import *
# app.register_blueprint(restaurant_bp)
# app.register_blueprint(pizza_bp)
# app.register_blueprint(restaurant_pizza_bp)


@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    if not pizzas:
        return jsonify({"message": "No pizzas found"}), 404

    formatted_pizzas = []
    for pizza in pizzas:
        formatted_pizzas.append({
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        })

    return jsonify(formatted_pizzas), 200


@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    try:
        data = request.get_json()
        errors = []

        if not data:
            return jsonify({"errors": ["No input data provided"]}), 400

        price = data.get("price")
        try:
            price = int(price)
            if price < 1 or price > 30:
                errors.append("Price must be between 1 and 30")
        except (ValueError, TypeError):
            errors.append("Price must be an integer")

        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        if not pizza_id:
            errors.append("Pizza ID is required")
        if not restaurant_id:
            errors.append("Restaurant ID is required")

        pizza = Pizza.query.get(pizza_id) if pizza_id else None
        restaurant = Restaurant.query.get(
            restaurant_id) if restaurant_id else None

        if pizza_id and not pizza:
            errors.append("Pizza not found")
        if restaurant_id and not restaurant:
            errors.append("Restaurant not found")

        existing = RestaurantPizza.query.filter_by(
            restaurant_id=restaurant_id,
            pizza_id=pizza_id
        ).first()

        if existing:
            errors.append("This pizza is already added to this restaurant")

        if errors:
            print(errors)
            # return jsonify({"errors": errors}), 400
            return jsonify({"errors": ["validation errors"] }), 400

        try:

            new_rp = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id,
            )

            db.session.add(new_rp)
            db.session.commit()

            return jsonify({
                "id": new_rp.id,
                "pizza_id": new_rp.pizza_id,
                "price": new_rp.price,
                "restaurant_id": new_rp.restaurant_id,
                "pizza": {
                    "id": pizza.id,
                    "name": pizza.name,
                    "ingredients": pizza.ingredients
                },
                "restaurant": {
                    "id": restaurant.id,
                    "name": restaurant.name,
                    "address": restaurant.address
                }
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"errors": [str(e)]}), 500
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    if not restaurants:
        return jsonify({"message": "No restaurants found"}), 404

    formatted_restaurants = []
    for restaurant in restaurants:
        formatted_restaurants.append({
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name,

        })

    return jsonify(formatted_restaurants), 200


@app.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):

    try:
        restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
        print(restaurant)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
        formatted_restaurant = {
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name,
            "restaurant_pizzas": []
        }

        for restaurant_pizza in restaurant.pizzas:
            formatted_restaurant["restaurant_pizzas"].append({
                "id": restaurant_pizza.id,
                "pizza": {
                    "id": restaurant_pizza.pizza.id,
                    "name": restaurant_pizza.pizza.name,
                    "ingredients": restaurant_pizza.pizza.ingredients
                },
                "pizza_id": restaurant_pizza.pizza_id,
                "price": restaurant_pizza.price,
                "restaurant_id": restaurant_pizza.restaurant_id

            })
        return jsonify(formatted_restaurant), 200

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


@app.route('/restaurants/<int:restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    try:
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404

        db.session.delete(restaurant)
        db.session.commit()
        return jsonify({"message": "Restaurant deleted successfully"}), 204    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(port=5555, debug=True)
