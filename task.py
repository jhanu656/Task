from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------------- In-memory "DB" ----------------
users = []

# ---------------- Helper Functions ----------------
def get_next_id(data):
    return max([item["id"] for item in data], default=0) + 1

# ---------------- Users ----------------

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    data["id"] = get_next_id(users)
    users.append(data)
    return jsonify(data), 201


# ---------------- App Runner ----------------

if __name__ == "__main__":
    app.run(debug=True)




