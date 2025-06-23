from flask import Blueprint, jsonify, request
from models import db, Restaurant, Pizza, RestaurantPizza


restaurant_bp = Blueprint('restaurant_bp', __name__)


@restaurant_bp.route('/restaurants', methods=['GET'])
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


@restaurant_bp.route('/restaurants/<int:restaurant_id>', methods=['GET'])
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
            "restaurant_pizza": []
        }

        for restaurant_pizza in restaurant.pizzas:
            formatted_restaurant["restaurant_pizza"].append({
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
    

@restaurant_bp.route('/restaurants/<int:restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    try:
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404

        db.session.delete(restaurant)
        db.session.commit()
        return jsonify({"message": "Restaurant deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

