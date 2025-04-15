from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------------- In-memory "DB" ----------------
users = []
posts = []


# ---------------- Helper Functions ----------------
def get_next_id(data):
    return max([item["id"] for item in data], default=0) + 1

def find_by_id(data, item_id):
    return next((item for item in data if item["id"] == item_id), None)


# ---------------- Users ----------------

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)


@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ["name", "email"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Check if user with same email already exists
        if any(user["email"] == data["email"] for user in users):
            return jsonify({"error": "User with this email already exists"}), 409

        data["id"] = get_next_id(users)
        users.append(data)
        return jsonify(data), 201

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

# ---------------- Posts ----------------

@app.route("/posts", methods=["GET"])
def get_posts():
    return jsonify(posts), 200


@app.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = find_by_id(posts, post_id)
    if post:
        return jsonify(post), 200
    return jsonify({"error": "Post not found"}), 404


@app.route("/posts/user/<int:user_id>", methods=["GET"])
def get_user_posts(user_id):
    user = find_by_id(users, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user_posts = [post for post in posts if post.get("userId") == user_id]
    return jsonify(user_posts), 200


@app.route("/posts", methods=["POST"])
def create_post():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ["userId", "title", "body"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        if not find_by_id(users, data["userId"]):
            return jsonify({"error": "Invalid userId"}), 400

        # Optional: Prevent duplicate title for same user
        if any(p["userId"] == data["userId"] and p["title"] == data["title"] for p in posts):
            return jsonify({"error": "Post with this title already exists for this user"}), 409

        data["id"] = get_next_id(posts)
        posts.append(data)
        return jsonify(data), 201

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


@app.route("/posts/<int:post_id>", methods=["PUT", "PATCH"])
def update_post(post_id):
    try:
        data = request.get_json()
        post = find_by_id(posts, post_id)

        if not post:
            return jsonify({"error": "Post not found"}), 404

        if "userId" in data and not find_by_id(users, data["userId"]):
            return jsonify({"error": "Invalid userId"}), 400

        post.update(data)
        return jsonify(post), 200

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


@app.route("/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    global posts
    post = find_by_id(posts, post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    posts = [p for p in posts if p["id"] != post_id]
    return jsonify({"message": "Post deleted"}), 200


# ---------------- App Runner ----------------

if __name__ == "__main__":
    app.run(debug=True)


