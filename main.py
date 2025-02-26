from flask import Flask, jsonify, request, abort
from flasgger import Swagger
from psycopg2 import OperationalError
from sqlalchemy import text
from werkzeug.exceptions import ServiceUnavailable, InternalServerError
from db import Session, engine, BlogPost
import logging

# Create a logger instance
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
swagger = Swagger(app)  # Initialize Swagger


@app.route("/healthcheck", methods=["GET"])
def perform_healthcheck():
    """
    Healthcheck endpoint
    ---
    responses:
      200:
        description: Server and database are running smoothly
      503:
        description: Service unavailable
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError:
        raise ServiceUnavailable()
    except Exception as e:
        print("========== app.get_health_check ==========")
        print(e)
        raise InternalServerError()
    return jsonify({"status": "ok", "message": "Server and database are running smoothly"}), 200


@app.route("/items", methods=["GET"])
def get_items():
    """
    Get all items
    ---
    responses:
      200:
        description: A list of items
      500:
        description: Internal server error
    """
    logger.debug("Fetching all items")
    try:
        session = Session()
        items = session.query(BlogPost).all()
        session.close()
        logger.debug(f"Retrieved items: {items}")
        return jsonify([item.to_dict() for item in items]), 200
    except Exception as e:
        logger.error(f"Error fetching items {e}", exc_info=True)
        abort(500)


@app.route("/items/<uuid:item_id>", methods=["GET"])
def get_item(item_id):
    """
    Get a single item by ID
    ---
    parameters:
      - name: item_id
        in: path
        type: string
        required: true
        description: The UUID of the item to retrieve
    responses:
      200:
        description: The item details
      404:
        description: Item not found
      500:
        description: Internal server error
    """
    logger.debug(f"Fetching item with id: {item_id}")
    try:
        session = Session()
        item = session.query(BlogPost).get(item_id)
        session.close()
        if item is None:
            logger.warning(f"Item with id {item_id} not found")
            return jsonify({"error": "Item not found"}), 404
        logger.debug(f"Retrieved item: {item}")
        return jsonify(item.to_dict()), 200
    except Exception as e:
        logger.error(f"Error fetching item {e}", exc_info=True)
        abort(500)


@app.route("/items", methods=["POST"])
def create_item():
    """
    Create a new item
    ---
    parameters:
      - name: item
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      201:
        description: Item created successfully
      500:
        description: Internal server error
    """
    new_item = request.json
    logger.debug(f"Creating new item: {new_item}")
    try:
        item = BlogPost(title=new_item["name"],
                        description=new_item["description"])
        item.save()  # Assuming save method is defined in BlogPost model
        logger.info("Item created successfully")
        return jsonify({"message": "Item created successfully"}), 201
    except Exception as e:
        logger.error(f"Error creating item {e}", exc_info=True)
        abort(500)


@app.route("/items/<uuid:item_id>", methods=["PUT"])
def update_item(item_id):
    """
    Update an existing item
    ---
    parameters:
      - name: item_id
        in: path
        type: string
        required: true
        description: The UUID of the item to update
      - name: item
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      200:
        description: Item updated successfully
      404:
        description: Item not found
      500:
        description: Internal server error
    """
    updated_item = request.json
    logger.debug(f"Updating item with id {item_id}: {updated_item}")
    try:
        session = Session()
        item = session.query(BlogPost).get(item_id)
        session.close()
        if item is None:
            logger.warning(f"Item with id {item_id} not found for update")
            return jsonify({"error": "Item not found"}), 404
        item.title = updated_item["name"]
        item.description = updated_item["description"]
        item.save()  # Assuming save method is defined in BlogPost model
        logger.info("Item updated successfully")
        return jsonify({"message": "Item updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating item {e}", exc_info=True)
        abort(500)


@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """
    Delete an item by ID
    ---
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        description: The ID of the item to delete
    responses:
      200:
        description: Item deleted successfully
      404:
        description: Item not found
      500:
        description: Internal server error
    """
    logger.debug(f"Deleting item with id: {item_id}")
    try:
        session = Session()
        item = session.query(BlogPost).get(item_id)
        session.close()
        if item is None:
            logger.warning(f"Item with id {item_id} not found for deletion")
            return jsonify({"error": "Item not found"}), 404
        item.delete()  # Assuming delete method is defined in BlogPost model
        logger.info("Item deleted successfully")
        return jsonify({"message": "Item deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting item {e}", exc_info=True)
        abort(500)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
