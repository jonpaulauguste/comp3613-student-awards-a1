"""Integration tests: API login, register and who is allowed to call what."""

from tests.conftest import auth_header, make_user


def test_register_and_login(client):
    body = {"username": "carl", "email": "carl@example.com", "password": "secret1"}

    response = client.post("/api/auth/register", json=body)
    assert response.status_code == 201
    assert response.json()["role"] == "regular_user"
    assert response.json()["total_points"] == 0
    assert "password" not in response.json()

    response = client.post("/api/auth/login", json={"username": "carl", "password": "secret1"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    token = response.json()["access_token"]

    response = client.get("/api/users/me", headers={"Authorization": "Bearer " + token})
    assert response.status_code == 200
    assert response.json()["username"] == "carl"


def test_register_duplicate_username(client, student):
    body = {"username": "bob", "email": "other@example.com", "password": "secret1"}
    response = client.post("/api/auth/register", json=body)
    assert response.status_code == 409


def test_register_invalid_body(client):
    body = {"username": "x", "email": "not-an-email", "password": "1"}
    response = client.post("/api/auth/register", json=body)
    assert response.status_code == 422


def test_login_wrong_password(client, student):
    response = client.post("/api/auth/login", json={"username": "bob", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_no_token(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/json")


def test_bad_token(client):
    response = client.get("/api/users/me", headers={"Authorization": "Bearer not.a.token"})
    assert response.status_code == 401


def test_cookie_token(client, student):
    token = auth_header(student)["Authorization"].split(" ")[1]
    client.cookies.set("access_token", token)
    response = client.get("/api/users/me")
    assert response.status_code == 200
    assert response.json()["username"] == "bob"


def test_student_cannot_list_users(client, student):
    response = client.get("/api/users", headers=auth_header(student))
    assert response.status_code == 403


def test_admin_can_list_users(client, admin, student):
    response = client.get("/api/users", headers=auth_header(admin))
    assert response.status_code == 200
    usernames = [user["username"] for user in response.json()]
    assert sorted(usernames) == ["admin", "bob"]


def test_student_cannot_approve_hours(client, student):
    response = client.patch(
        "/api/volunteer-sessions/1", json={"status": "approved"}, headers=auth_header(student)
    )
    assert response.status_code == 403


def test_student_cannot_create_award(client, student):
    body = {"name": "Free stuff", "points_required": 1, "stock_quantity": 9}
    response = client.post("/api/awards", json=body, headers=auth_header(student))
    assert response.status_code == 403


def test_admin_cannot_log_hours(client, admin):
    body = {"description": "Tutoring", "hours_logged": 1, "date": "2026-01-01"}
    response = client.post("/api/volunteer-sessions", json=body, headers=auth_header(admin))
    assert response.status_code == 403


def test_admin_cannot_redeem_award(client, admin):
    response = client.post("/api/redemptions", json={"award_id": 1}, headers=auth_header(admin))
    assert response.status_code == 403


def test_other_user_cannot_see_session(client, db, student):
    from tests.conftest import make_session

    alice = make_user(db, "alice")
    row = make_session(db, alice)
    response = client.get("/api/volunteer-sessions/" + str(row.id), headers=auth_header(student))
    assert response.status_code == 403
