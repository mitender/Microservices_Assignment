from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import requests
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB URI for connecting to the MongoDB container
app.config["MONGO_URI"] = "mongodb://mongodb-order:27017/orders_db"  # Update if necessary for your MongoDB service name
mongo = PyMongo(app)

@app.route('/orders', methods=['POST'])
def create_order():
    print("Inside create_order function")

    # Get order data from the request
    data = request.get_json()

    # Check if the required fields are present in the request
    if not data.get('product_id') or not data.get('quantity'):
        return jsonify({"error": "Missing required fields: product_id or quantity"}), 400

    # Call Inventory Service to check stock availability
    inventory_check = check_inventory(data['product_id'], data['quantity'])
    
    if not inventory_check.get('available', False):
        return jsonify({"error": "Product is out of stock"}), 400

    # Insert order into MongoDB
    new_order = {
        "product_id": data['product_id'],
        "quantity": data['quantity']
    }

    try:
        # Attempt to insert the order into MongoDB
        order_id = mongo.db.orders.insert_one(new_order).inserted_id
        return jsonify({"message": "Order created successfully", "order_id": str(order_id)}), 201
    except Exception as e:
        # Handle errors while inserting the order into MongoDB
        print(f"Error inserting order into MongoDB: {e}")
        return jsonify({"error": "Failed to create order in the database"}), 500


@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        # Retrieve all orders from MongoDB
        orders = mongo.db.orders.find()
        return jsonify([{"id": str(order["_id"]), "product_id": order["product_id"], "quantity": order["quantity"]} for order in orders])
    except Exception as e:
        # Handle any errors when retrieving orders from MongoDB
        print(f"Error retrieving orders: {e}")
        return jsonify({"error": "Failed to retrieve orders"}), 500


def check_inventory(product_id, quantity):
    """
    This function calls the inventory service to check if a product is available in stock.
    """
    try:
        # Call the Inventory Service using the service name (should resolve to the correct pod in Kubernetes)
        response = requests.get(f'http://inventory-service:5000/inventory/{product_id}')
        if response.status_code == 200:
            inventory = response.json()
            return {"available": inventory["stock"] >= quantity}
        else:
            print(f"Error: Inventory service returned status code {response.status_code}")
            return {"available": False}
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request to the inventory service
        print(f"Error connecting to Inventory Service: {e}")
        return {"available": False}


if __name__ == '__main__':
    app.run(debug=True, port=5001)
