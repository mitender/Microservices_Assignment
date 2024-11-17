from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import requests

app = Flask(__name__)

# Use the service name (container name) for MongoDB URI
app.config["MONGO_URI"] = "mongodb://mongodb-order:27017/orders_db"  # 'mongodb-order' is the container name for MongoDB
mongo = PyMongo(app)

@app.route('/orders', methods=['POST'])
def create_order():
    print("inside app")
    data = request.json
    # Simulate calling Inventory Service to check stock availability
    response = check_inventory(data['product_id'], data['quantity'])
    if not response.get('available', False):
        return jsonify({"error": "Product is out of stock"}), 400

    new_order = {
        "product_id": data['product_id'],
        "quantity": data['quantity']
    }
    order_id = mongo.db.orders.insert_one(new_order).inserted_id
    return jsonify({"message": "Order created", "order_id": str(order_id)}), 201

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = mongo.db.orders.find()
    return jsonify([{"id": str(order["_id"]), "product_id": order["product_id"], "quantity": order["quantity"]} for order in orders])

def check_inventory(product_id, quantity):
    # Use the service name of inventory-service to call the Inventory API
    response = requests.get(f'http://inventory-service:5000/inventory/{product_id}')
    if response.status_code == 200:
        inventory = response.json()
        return {"available": inventory["stock"] >= quantity}
    return {"available": False}

if __name__ == '__main__':
    app.run(debug=True, port=5001)
