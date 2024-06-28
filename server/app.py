#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Restaurants(Resource):
    def get(self):
        restaurants = [n.to_dict() for n in Restaurant.query.all()]
        for restaurant in restaurants:
            restaurant.pop('restaurant_pizzas', None)
        return make_response(jsonify(restaurants), 200)

api.add_resource(Restaurants, "/restaurants")

class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404
        response_dict = restaurant.to_dict()
        return response_dict, 200
    
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404

        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204

api.add_resource(RestaurantByID, "/restaurants/<int:id>")

class Pizzas(Resource):
    def get(self):
        response_dict_list = [n.to_dict() for n in Pizza.query.all()]
        return make_response(jsonify(response_dict_list), 200)
    
api.add_resource(Pizzas, "/pizzas")

class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            price = int(data.get('price'))
            
            # Create and validate RestaurantPizza instance
            restaurant_pizza = RestaurantPizza(
                pizza_id=data.get('pizza_id'),
                restaurant_id=data.get('restaurant_id'),
                price=price,
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            
            restaurant = Restaurant.query.get(data.get('restaurant_id'))
            pizza = Pizza.query.get(data.get('pizza_id'))

            response_dict = {
                "id": restaurant_pizza.id,
                "price": restaurant_pizza.price,
                "pizza_id": restaurant_pizza.pizza_id,
                "restaurant_id": restaurant_pizza.restaurant_id,
                "pizza": pizza.to_dict(),
                "restaurant": restaurant.to_dict(),
            }
            
            return make_response(jsonify(response_dict), 201)
        
        except AssertionError as e:
            return jsonify({'errors': str(e)}), 400
        except Exception as e:
            return {"error": "An error occurred"}, 500

api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
