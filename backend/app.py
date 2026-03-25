from flask import Flask, request, jsonify, make_response
from sqlalchemy import create_engine


db = SQLAlchemy(app)
def create_app():
    app = Flask(__name__)
    engine = create_engine('sqlite:///example.db')
    Base = declarative_base()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # --- In-Memory Mock Database for CRUD Examples ---
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"}
    ]

    # --- 1. Basic Response & JSON Response ---
    @app.route('/')
    def index():
        print("Hello World from Flask in OpenW!")
        # jsonify returns a flask.Response object with application/json mimetype
        return jsonify({"message": "Hello World from Flask in OpenW!"})

    # --- 2. Query Parameters (GET request.args) ---
    @app.route('/search')
    def search():
        # Example URL: /search?q=flask&limit=10
        query = request.args.get('q', default='', type=str)
        limit = request.args.get('limit', default=5, type=int)
        return jsonify({"search_query": query, "limit": limit})

    # --- 3. Form Data (POST request.form) ---
    @app.route('/submit-form', methods=['POST'])
    def submit_form():
        # Expected Content-Type: application/x-www-form-urlencoded
        username = request.form.get('username')
        password = request.form.get('password')
        return jsonify({"message": "Form received", "username": username})

    # --- 4. Custom HTTP Status Codes & Response Headers ---
    @app.route('/custom-response')
    def custom_response():
        # Returning a tuple: (response_data, status_code, headers_dict)
        return jsonify({"error": "Unauthorized access"}), 401, {'X-Custom-Header': 'Flask-App'}

    # ==========================================
    # --- 5. CRUD Operations (RESTful API) ---
    # ==========================================

    # CREATE (POST)
    @app.route('/users', methods=['POST'])
    def create_user():
        # Get JSON data from the request body
        data = request.get_json()
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({"error": "Bad Request", "message": "Name and email are required"}), 400
        
        new_id = max((u['id'] for u in users), default=0) + 1 if users else 1
        new_user = {
            "id": new_id,
            "name": data['name'],
            "email": data['email']
        }
        users.append(new_user)
        # 201 Created is the appropriate status code
        return jsonify(new_user), 201

    # READ ALL (GET)
    @app.route('/users', methods=['GET'])
    def get_users():
        return jsonify(users), 200

    # READ ONE (GET)
    @app.route('/users/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        # <int:user_id> automatically converts the URL parameter to an integer
        user = next((u for u in users if u['id'] == user_id), None)
        if user is None:
            return jsonify({"error": "Not Found", "message": f"User {user_id} not found"}), 404
        return jsonify(user), 200

    # UPDATE (PUT)
    @app.route('/users/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        user = next((u for u in users if u['id'] == user_id), None)
        if user is None:
            return jsonify({"error": "Not Found", "message": f"User {user_id} not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Bad Request", "message": "No data provided"}), 400

        # Update fields if provided
        user['name'] = data.get('name', user['name'])
        user['email'] = data.get('email', user['email'])
        
        return jsonify(user), 200

    # DELETE (DELETE)
    @app.route('/users/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        user = next((u for u in users if u['id'] == user_id), None)
        if user is None:
            return jsonify({"error": "Not Found", "message": f"User {user_id} not found"}), 404

        # Remove user from list
        users.remove(user)
        
        return jsonify({"message": f"User {user_id} successfully deleted"}), 200

    return app