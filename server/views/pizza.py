from flask import Blueprint, jsonify
from models import Pizza

pizza_bp = Blueprint('pizza_bp', __name__)

@pizza_bp.route('/pizzas', methods=['GET'])
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
