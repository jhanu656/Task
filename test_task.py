import pytest
import task as app


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        # Clear in-memory data before each test
        app.users.clear()
        app.posts.clear()
        app.comments.clear()
        app.todos.clear()
        yield client

# ---------------- Users --------------------------------
def test_create_user(client):
    # Create the first user
    res1 = client.post("/users", json={"name": "Alice", "email": "alice@example.com"})
    assert res1.status_code == 201
    user1 = res1.get_json()
    assert user1["name"] == "Alice"
    assert user1["email"] == "alice@example.com"
    assert "id" in user1  
    assert user1["id"] == app.users[0]["id"]  

    # Create the second user
    res2 = client.post("/users", json={"name": "Bob", "email": "bob@example.com"})
    assert res2.status_code == 201
    user2 = res2.get_json()
    assert user2["name"] == "Bob"
    assert user2["email"] == "bob@example.com"
    assert "id" in user2 
    assert user2["id"] == app.users[1]["id"]  

    # Verify the IDs are sequential
    assert user2["id"] == user1["id"] + 1

def test_create_user_missing_field(client):
    res = client.post("/users", json={"name": "Alice"})
    assert res.status_code == 400
    assert "Missing field" in res.get_json()["error"]

def test_duplicate_user_email(client):
    client.post("/users", json={"name": "Alice", "email": "alice@example.com"})
    res = client.post("/users", json={"name": "Alice", "email": "alice@example.com"})
    assert res.status_code == 409

def test_get_users(client):
    res = client.get("/users")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_get_users_empty(client):
    res = client.get("/users")
    assert res.status_code == 200
    assert res.get_json() == []

def test_get_user_not_found(client):
    res = client.get("/users/99")  # Assuming you add a GET /users/<id> endpoint later
    assert res.status_code == 404

# ---------------- Posts ----------------
def test_create_post(client):
    client.post("/users", json={"name": "Bob", "email": "bob@example.com"})
    res = client.post("/posts", json={"userId": 1, "title": "My First Post", "body": "Hello World!"})
    assert res.status_code == 201
    assert res.get_json()["title"] == "My First Post"

def test_create_post_invalid_user(client):
    res = client.post("/posts", json={"userId": 99, "title": "Invalid Post", "body": "No user"})
    assert res.status_code == 400
    assert res.get_json()["error"] == "Invalid userId"

def test_get_posts(client):
    res = client.get("/posts")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_update_post(client):
    client.post("/users", json={"name": "Eve", "email": "eve@example.com"})
    client.post("/posts", json={"userId": 1, "title": "Old Title", "body": "Old Body"})
    res = client.put("/posts/1", json={"title": "New Title", "body": "New Body"})
    assert res.status_code == 200
    assert res.get_json()["title"] == "New Title"

def test_update_post_not_found(client):
    res = client.put("/posts/99", json={"title": "Nonexistent Post"})
    assert res.status_code == 404

def test_delete_post(client):
    client.post("/users", json={"name": "Frank", "email": "frank@example.com"})
    client.post("/posts", json={"userId": 1, "title": "To Be Deleted", "body": "Body"})
    res = client.delete("/posts/1")
    assert res.status_code == 200
    assert res.get_json()["message"] == "Post deleted"

def test_delete_post_not_found(client):
    res = client.delete("/posts/99")
    assert res.status_code == 404

# ---------------- Comments ----------------
def test_create_comment(client):
    client.post("/users", json={"name": "Charlie", "email": "charlie@example.com"})
    client.post("/posts", json={"userId": 1, "title": "Post", "body": "Body"})
    res = client.post("/comments", json={
        "postId": 1,
        "name": "Commenter",
        "email": "commenter@example.com",
        "body": "Nice post!"
    })
    assert res.status_code == 201
    assert res.get_json()["body"] == "Nice post!"

def test_create_comment_invalid_post(client):
    res = client.post("/comments", json={
        "postId": 99,
        "name": "Commenter",
        "email": "commenter@example.com",
        "body": "Invalid post!"
    })
    assert res.status_code == 400
    assert res.get_json()["error"] == "Invalid postId"

def test_get_comments(client):
    res = client.get("/comments")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_get_comments_filtered_by_post(client):
    client.post("/users", json={"name": "Grace", "email": "grace@example.com"})
    client.post("/posts", json={"userId": 1, "title": "Post", "body": "Body"})
    client.post("/comments", json={
        "postId": 1,
        "name": "Commenter",
        "email": "commenter@example.com",
        "body": "Nice post!"
    })
    res = client.get("/comments?postId=1")
    assert res.status_code == 200
    assert len(res.get_json()) == 1

# ---------------- Todos ----------------
def test_create_todo(client):
    client.post("/users", json={"name": "Dave", "email": "dave@example.com"})
    res = client.post("/todos", json={"userId": 1, "title": "Todo 1"})
    assert res.status_code == 201
    assert res.get_json()["completed"] is False

def test_create_todo_invalid_user(client):
    res = client.post("/todos", json={"userId": 99, "title": "Invalid Todo"})
    assert res.status_code == 400
    assert res.get_json()["error"] == "Invalid userId"

def test_get_todos(client):
    res = client.get("/todos")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_delete_todo_not_found(client):
    res = client.delete("/todos/99")
    assert res.status_code == 404





