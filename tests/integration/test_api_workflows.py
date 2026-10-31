"""Integration tests: the three workflows through the API (HTTP, real database)."""

from datetime import date, timedelta

from tests.conftest import auth_header, make_award, make_session, make_user

YESTERDAY = (date.today() - timedelta(days=1)).isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()


def get_points(client, user):
    return client.get("/api/users/me", headers=auth_header(user)).json()["total_points"]


# ---- Workflow 1: Log Volunteer Hours ----

def test_log_hours(client, student):
    body = {"description": "Library Tutoring", "hours_logged": 3, "date": YESTERDAY}

    response = client.post("/api/volunteer-sessions", json=body, headers=auth_header(student))

    assert response.status_code == 201
    assert response.json()["status"] == "pending"
    assert response.json()["student_id"] == student.id

    response = client.get("/api/volunteer-sessions", headers=auth_header(student))
    assert len(response.json()) == 1


def test_log_hours_zero_hours(client, student):
    body = {"description": "Tutoring", "hours_logged": 0, "date": YESTERDAY}
    response = client.post("/api/volunteer-sessions", json=body, headers=auth_header(student))
    assert response.status_code == 422


def test_log_hours_missing_date(client, student):
    body = {"description": "Tutoring", "hours_logged": 2}
    response = client.post("/api/volunteer-sessions", json=body, headers=auth_header(student))
    assert response.status_code == 422


def test_log_hours_future_date(client, student):
    body = {"description": "Tutoring", "hours_logged": 2, "date": TOMORROW}
    response = client.post("/api/volunteer-sessions", json=body, headers=auth_header(student))
    assert response.status_code == 400


def test_log_hours_blank_description(client, student):
    body = {"description": "   ", "hours_logged": 2, "date": YESTERDAY}
    response = client.post("/api/volunteer-sessions", json=body, headers=auth_header(student))
    assert response.status_code == 400


def test_students_only_see_their_own_sessions(client, db, student):
    alice = make_user(db, "alice")
    mine = make_session(db, student)
    make_session(db, alice)

    response = client.get("/api/volunteer-sessions", headers=auth_header(student))

    assert [row["id"] for row in response.json()] == [mine.id]


def test_missing_session(client, admin):
    response = client.get("/api/volunteer-sessions/999", headers=auth_header(admin))
    assert response.status_code == 404


# ---- Workflow 2: Approve Volunteer Hours ----

def test_approve_hours(client, db, admin, student):
    row = make_session(db, student, hours=3)
    url = "/api/volunteer-sessions/" + str(row.id)

    response = client.patch(url, json={"status": "approved"}, headers=auth_header(admin))

    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert get_points(client, student) == 3


def test_admin_lists_pending_sessions(client, db, admin, student):
    pending = make_session(db, student, status="pending")
    make_session(db, student, status="approved")

    response = client.get("/api/volunteer-sessions?status=pending", headers=auth_header(admin))

    assert [row["id"] for row in response.json()] == [pending.id]


def test_approve_half_hour(client, db, admin, student):
    row = make_session(db, student, hours=0.5)
    url = "/api/volunteer-sessions/" + str(row.id)
    response = client.patch(url, json={"status": "approved"}, headers=auth_header(admin))
    assert response.status_code == 200
    assert get_points(client, student) == 1


def test_approve_twice(client, db, admin, student):
    row = make_session(db, student, hours=4)
    url = "/api/volunteer-sessions/" + str(row.id)
    client.patch(url, json={"status": "approved"}, headers=auth_header(admin))

    response = client.patch(url, json={"status": "approved"}, headers=auth_header(admin))

    assert response.status_code == 409
    assert get_points(client, student) == 4


def test_reject_hours(client, db, admin, student):
    row = make_session(db, student, hours=5)
    url = "/api/volunteer-sessions/" + str(row.id)

    response = client.patch(url, json={"status": "rejected"}, headers=auth_header(admin))

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert get_points(client, student) == 0


def test_review_with_invalid_status(client, db, admin, student):
    row = make_session(db, student)
    url = "/api/volunteer-sessions/" + str(row.id)
    response = client.patch(url, json={"status": "pending"}, headers=auth_header(admin))
    assert response.status_code == 422


def test_review_missing_session(client, admin):
    response = client.patch(
        "/api/volunteer-sessions/999", json={"status": "approved"}, headers=auth_header(admin)
    )
    assert response.status_code == 404


# ---- Workflow 3: Redeem Award ----

def test_redeem_award(client, db, student):
    db_student = make_user(db, "rich", points=20)
    award = make_award(db, points_required=15, stock_quantity=4)

    response = client.post(
        "/api/redemptions", json={"award_id": award.id}, headers=auth_header(db_student)
    )

    assert response.status_code == 201
    assert response.json()["status"] == "submitted"
    assert response.json()["award_id"] == award.id
    assert get_points(client, db_student) == 5
    award_response = client.get("/api/awards/" + str(award.id), headers=auth_header(db_student))
    assert award_response.json()["stock_quantity"] == 3
    claims = client.get("/api/redemptions", headers=auth_header(db_student)).json()
    assert len(claims) == 1


def test_redeem_award_not_enough_points(client, db, student):
    award = make_award(db, points_required=50, stock_quantity=3)

    response = client.post(
        "/api/redemptions", json={"award_id": award.id}, headers=auth_header(student)
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "You need 50 more point(s)."
    award_response = client.get("/api/awards/" + str(award.id), headers=auth_header(student))
    assert award_response.json()["stock_quantity"] == 3


def test_redeem_award_out_of_stock(client, db):
    rich = make_user(db, "rich", points=500)
    award = make_award(db, points_required=10, stock_quantity=0)
    response = client.post("/api/redemptions", json={"award_id": award.id}, headers=auth_header(rich))
    assert response.status_code == 409
    assert get_points(client, rich) == 500


def test_redeem_missing_award(client, student):
    response = client.post("/api/redemptions", json={"award_id": 999}, headers=auth_header(student))
    assert response.status_code == 404


def test_admin_sees_all_claims(client, db, admin):
    rich = make_user(db, "rich", points=50)
    award = make_award(db, points_required=10)
    client.post("/api/redemptions", json={"award_id": award.id}, headers=auth_header(rich))
    response = client.get("/api/redemptions", headers=auth_header(admin))
    assert len(response.json()) == 1


# ---- Award catalogue (admin) ----

def test_admin_manages_awards(client, admin, student):
    headers = auth_header(admin)
    body = {"name": "University Hoodie", "description": "Warm", "points_required": 100, "stock_quantity": 3}

    response = client.post("/api/awards", json=body, headers=headers)
    assert response.status_code == 201
    award_id = response.json()["id"]

    response = client.patch("/api/awards/" + str(award_id), json={"stock_quantity": 7}, headers=headers)
    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 7
    assert response.json()["name"] == "University Hoodie"

    response = client.get("/api/awards", headers=auth_header(student))
    assert [award["name"] for award in response.json()] == ["University Hoodie"]

    response = client.delete("/api/awards/" + str(award_id), headers=headers)
    assert response.status_code == 204

    response = client.get("/api/awards/" + str(award_id), headers=headers)
    assert response.status_code == 404


def test_create_award_invalid_values(client, admin):
    body = {"name": "Bad", "points_required": 0, "stock_quantity": -1}
    response = client.post("/api/awards", json=body, headers=auth_header(admin))
    assert response.status_code == 422


def test_delete_award_with_claims(client, db, admin):
    rich = make_user(db, "rich", points=50)
    award = make_award(db, points_required=10, stock_quantity=2)
    client.post("/api/redemptions", json={"award_id": award.id}, headers=auth_header(rich))

    response = client.delete("/api/awards/" + str(award.id), headers=auth_header(admin))

    assert response.status_code == 409
