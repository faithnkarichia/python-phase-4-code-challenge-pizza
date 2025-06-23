from flask import Blueprint, jsonify, request
from models import db, Restaurant, Pizza, RestaurantPizza
restaurant_pizza_bp = Blueprint('restaurant_pizza_bp', __name__)


@restaurant_pizza_bp.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
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
    restaurant = Restaurant.query.get(restaurant_id) if restaurant_id else None

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
        return jsonify({"errors": errors}), 400

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
