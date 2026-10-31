"""Integration tests: the pages in the wireframes (login, dashboard, admin, rewards)."""

from datetime import date, timedelta

from tests.conftest import make_award, make_session, make_user

YESTERDAY = (date.today() - timedelta(days=1)).isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()


def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password})


def test_student_login(client, student):
    response = login(client, "bob", "bobpass")
    assert response.url.path == "/app"
    assert "Log Volunteer Hours" in response.text
    assert "access_token" in client.cookies


def test_admin_login(client, admin):
    response = login(client, "admin", "adminpass")
    assert response.url.path == "/admin"
    assert "Pending Volunteer Approvals" in response.text


def test_bad_login(client, student):
    response = login(client, "bob", "wrong")
    assert response.url.path == "/login"
    assert "Incorrect username or password" in response.text


def test_pages_need_login(client):
    for url in ["/app", "/app/rewards", "/admin"]:
        response = client.get(url)
        assert response.status_code == 401
        assert "Return to Login" in response.text


def test_student_cannot_open_admin_page(client, student):
    login(client, "bob", "bobpass")
    response = client.get("/admin")
    assert response.status_code == 403
    assert "Forbidden" in response.text


def test_logout(client, student):
    login(client, "bob", "bobpass")
    client.get("/logout")
    response = client.get("/app")
    assert response.status_code == 401


def test_register_page(client):
    form = {"username": "dana", "email": "dana@example.com", "password": "secret1"}
    response = client.post("/register", data=form)
    assert response.url.path == "/login"
    assert "Registration completed" in response.text
    response = login(client, "dana", "secret1")
    assert response.url.path == "/app"


def test_log_hours_form(client, student):
    login(client, "bob", "bobpass")
    form = {"description": "Library Tutoring", "hours_logged": "3", "session_date": YESTERDAY}

    response = client.post("/app/volunteer-sessions", data=form)

    assert response.url.path == "/app"
    assert "Volunteer hours submitted for approval." in response.text
    assert "Library Tutoring" in response.text
    assert "Pending" in response.text


def test_log_hours_form_future_date(client, student):
    login(client, "bob", "bobpass")
    form = {"description": "Beach", "hours_logged": "2", "session_date": TOMORROW}
    response = client.post("/app/volunteer-sessions", data=form)
    assert "Session date cannot be in the future." in response.text


def test_admin_approve_and_reject_buttons(client, db, admin):
    alice = make_user(db, "alice")
    to_approve = make_session(db, alice, hours=3, description="Beach Cleanup")
    to_reject = make_session(db, alice, hours=2, description="Math Tutoring")
    login(client, "admin", "adminpass")

    page = client.get("/admin").text
    assert "alice" in page
    assert "Beach Cleanup" in page
    assert "Reject" in page

    response = client.post("/admin/volunteer-sessions/" + str(to_approve.id) + "/approve")
    assert "approved and points awarded" in response.text
    response = client.post("/admin/volunteer-sessions/" + str(to_reject.id) + "/reject")
    assert "rejected" in response.text
    assert "No pending volunteer sessions." in response.text

    db.refresh(alice)
    assert alice.total_points == 3


def test_rewards_page_claim(client, db):
    make_user(db, "rich", points=20, password="richpass")
    coffee = make_award(db, "Campus Coffee Voucher", points_required=15, stock_quantity=4)
    gift_card = make_award(db, "Bookstore Gift Card", points_required=100)
    login(client, "rich", "richpass")

    page = client.get("/app/rewards").text
    assert "Campus Coffee Voucher" in page
    assert "You need 80 more point(s)." in page

    response = client.post("/app/rewards/" + str(coffee.id) + "/redeem")
    assert "Your redemption request was submitted." in response.text
    assert "5 pts" in response.text
    assert "In Stock: 3" in response.text
    assert "Submitted" in response.text

    response = client.post("/app/rewards/" + str(gift_card.id) + "/redeem")
    assert "more point(s)" in response.text
