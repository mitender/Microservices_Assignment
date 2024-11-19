from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Use the service name (container name) for MongoDB URI
app.config["MONGO_URI"] = "mongodb://mongodb-inventory:27017/inventory_db"  # Update port to 27018
mongo = PyMongo(app)

@app.route('/inventory/<int:product_id>', methods=['GET'])
def get_inventory(product_id):
    logger.info("Fetching inventory for product_id: %s", product_id)
    inventory = mongo.db.inventory.find_one({"product_id": product_id})
    if inventory:
        return jsonify({"product_id": inventory["product_id"], "stock": inventory["stock"]})
    return jsonify({"error": "Product not found"}), 404

@app.route('/inventory', methods=['POST'])
def add_inventory():
    logger.info("Fetching inventory for product_id: %s", request.json)
    data = request.json
    new_inventory = {
        "product_id": data['product_id'],
        "stock": data['stock']
    }
    # Insert the new inventory document
    result = mongo.db.inventory.insert_one(new_inventory)
    
    if result.inserted_id:
        logger.info("Inventory added successfully with ID: %s", str(result.inserted_id))
        return jsonify({"message": "Inventory added", "id": str(result.inserted_id)}), 201
    else:
        logger.error("Failed to add inventory")
        return jsonify({"error": "Failed to add inventory"}), 500

@app.route('/all-inventory', methods=['GET'])
def get_all_inventory():
    # Fetch all inventory items
    inventory_items = list(mongo.db.inventory.find())
    
    for item in inventory_items:
        item["_id"] = str(item["_id"])  # Convert ObjectId to string
        
    return jsonify(inventory_items)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
