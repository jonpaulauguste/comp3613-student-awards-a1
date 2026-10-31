# COMP 3613 Assignment 2: Test Plans

Project: **Student Awards**. Workflows under test:

1. Log Volunteer Hours (student)
2. Approve Volunteer Hours (admin), including Reject (the admin screen has both buttons)
3. Redeem Award (student)

Rules the tests check:

- A session needs a description (1 to 255 characters), hours above 0 and at most 24, and a date that is not in the future.
- New sessions are `pending`. Only an admin can approve or reject, and only once (a second review gives 409).
- Approving gives 1 point per hour, rounded half up, minimum 1. Rejecting gives no points.
- A redemption needs enough points (400) and stock above 0 (409). Points, stock and the claim are saved together.
- An award that has claims cannot be deleted (409).
- Not logged in gives 401. Wrong role gives 403.

How to run:

| Tests | Command |
|---|---|
| Unit | `python manage.py test unit` |
| Integration | `python manage.py test integration` |
| Both | `python manage.py test` |
| API (Postman) | import `postman/student-awards.postman_collection.json` and use the Collection Runner, or `newman run` |

---

## 1. UAT Plan

UAT steps follow the wireframes in `docs/wireframes/`. Students are `bob / bobpass`. The admin is `admin / adminpass`.

- **Pre-conditions:** what state the app must already be in and which user is logged in.
- **Test Steps:** exactly what the user does on the screen.
- **Test Criteria:** what the user should see if the steps worked.

| Test Case | Pre-conditions | Test Steps | Test Criteria | Success |
|---|---|---|---|---|
| **UAT-01 Test Login** | ☐ Student account bob / bobpass exists<br>☐ App is open on the Sign in page | ☐ Enter Username `bob`<br>☐ Enter Password `bobpass`<br>☐ Click **Sign in** | ☐ The student home page opens<br>☐ Page shows **Log Volunteer Hours**, **Your Volunteer Sessions** and **Current Points** | |
| **UAT-02 Test Login with wrong password** | None | ☐ Enter Username `bob`<br>☐ Enter Password `wrong`<br>☐ Click **Sign in** | ☐ Page stays on Sign in<br>☐ Message "Incorrect username or password" is shown | |
| **UAT-03 Test Log Volunteer Hours** | ☐ Must be logged in as a student | ☐ Enter Description `Library Tutoring`<br>☐ Enter Hours `3`<br>☐ Enter a Date from yesterday<br>☐ Click **Submit for Approval** | ☐ Message "Volunteer hours submitted for approval." is shown<br>☐ Session appears under **Your Volunteer Sessions** with status Pending<br>☐ Current Points do not change | |
| **UAT-04 Test Log Hours with future date** | ☐ Must be logged in as a student | ☐ Enter Description `Beach Cleanup`<br>☐ Enter Hours `2`<br>☐ Enter tomorrow's date<br>☐ Click **Submit for Approval** | ☐ Message "Session date cannot be in the future." is shown<br>☐ No new session is listed | |
| **UAT-05 Test Log Hours with 0 hours** | ☐ Must be logged in as a student | ☐ Enter Description `Beach Cleanup`<br>☐ Enter Hours `0`<br>☐ Enter yesterday's date<br>☐ Click **Submit for Approval** | ☐ Browser does not accept 0 (minimum is 0.5)<br>☐ No new session is listed | |
| **UAT-06 Test Approve Volunteer Hours** | ☐ Must be logged in as an admin<br>☐ A pending 3 hour session from bob exists | ☐ Open the admin page<br>☐ Find bob's session under **Pending Volunteer Approvals**<br>☐ Click **Approve + Award Points** | ☐ Message "Volunteer session approved and points awarded." is shown<br>☐ Row leaves the pending list<br>☐ When bob logs in, his Current Points are 3 higher | |
| **UAT-07 Test Reject Volunteer Hours** | ☐ Must be logged in as an admin<br>☐ A pending session from bob exists | ☐ Open the admin page<br>☐ Click **Reject** on bob's session | ☐ Message "Volunteer session rejected. No points were awarded." is shown<br>☐ Row leaves the pending list<br>☐ Bob's points do not change | |
| **UAT-08 Test Student cannot open admin page** | ☐ Must be logged in as a student | ☐ Type the address `/admin` in the browser | ☐ A Forbidden page is shown<br>☐ No approvals are visible | |
| **UAT-09 Test Redeem Award** | ☐ Must be logged in as a student with at least 15 points<br>☐ A reward costing 15 points with stock above 0 exists | ☐ Click **Rewards Catalogue**<br>☐ Click **Claim** on the reward | ☐ Message "Your redemption request was submitted." is shown<br>☐ Current Points go down by 15<br>☐ Stock goes down by 1<br>☐ Claim is listed under **Your Redemption Claims** as Submitted | |
| **UAT-10 Test Redeem with not enough points** | ☐ Must be logged in as a student with fewer points than the reward costs | ☐ Click **Rewards Catalogue**<br>☐ Look at the reward | ☐ **Claim** button is disabled<br>☐ Text "You need N more point(s)." is shown | |
| **UAT-11 Test Page without login** | ☐ User is logged out | ☐ Type the address `/app` in the browser | ☐ Session Expired page is shown<br>☐ Page has a link back to login | |

### UAT Report

Complete this on the deployed app (use the same steps as the plan above).

| Tester Name | Tester Position | Date of Test (DD/MM/YYYY) |
|---|---|---|
| | | |

| Test Case | Pre-conditions | Test Steps | Test Criteria | Success (indicate with a ✓) |
|---|---|---|---|---|
| **UAT-01 Test Login** | ☐ Student account bob / bobpass exists<br>☐ App is open on the Sign in page | ☐ Enter Username `bob`<br>☐ Enter Password `bobpass`<br>☐ Click **Sign in** | ☐ The student home page opens<br>☐ Page shows **Log Volunteer Hours**, **Your Volunteer Sessions** and **Current Points** | Pass ☐ &nbsp; Fail ☐ |
| **UAT-02 Test Login with wrong password** | None | ☐ Enter Username `bob`<br>☐ Enter Password `wrong`<br>☐ Click **Sign in** | ☐ Page stays on Sign in<br>☐ Message "Incorrect username or password" is shown | Pass ☐ &nbsp; Fail ☐ |
| **UAT-03 Test Log Volunteer Hours** | ☐ Must be logged in as a student | ☐ Enter Description `Library Tutoring`<br>☐ Enter Hours `3`<br>☐ Enter a Date from yesterday<br>☐ Click **Submit for Approval** | ☐ Message "Volunteer hours submitted for approval." is shown<br>☐ Session appears under **Your Volunteer Sessions** with status Pending<br>☐ Current Points do not change | Pass ☐ &nbsp; Fail ☐ |
| **UAT-04 Test Log Hours with future date** | ☐ Must be logged in as a student | ☐ Enter Description `Beach Cleanup`<br>☐ Enter Hours `2`<br>☐ Enter tomorrow's date<br>☐ Click **Submit for Approval** | ☐ Message "Session date cannot be in the future." is shown<br>☐ No new session is listed | Pass ☐ &nbsp; Fail ☐ |
| **UAT-05 Test Log Hours with 0 hours** | ☐ Must be logged in as a student | ☐ Enter Description `Beach Cleanup`<br>☐ Enter Hours `0`<br>☐ Enter yesterday's date<br>☐ Click **Submit for Approval** | ☐ Browser does not accept 0 (minimum is 0.5)<br>☐ No new session is listed | Pass ☐ &nbsp; Fail ☐ |
| **UAT-06 Test Approve Volunteer Hours** | ☐ Must be logged in as an admin<br>☐ A pending 3 hour session from bob exists | ☐ Open the admin page<br>☐ Find bob's session under **Pending Volunteer Approvals**<br>☐ Click **Approve + Award Points** | ☐ Message "Volunteer session approved and points awarded." is shown<br>☐ Row leaves the pending list<br>☐ When bob logs in, his Current Points are 3 higher | Pass ☐ &nbsp; Fail ☐ |
| **UAT-07 Test Reject Volunteer Hours** | ☐ Must be logged in as an admin<br>☐ A pending session from bob exists | ☐ Open the admin page<br>☐ Click **Reject** on bob's session | ☐ Message "Volunteer session rejected. No points were awarded." is shown<br>☐ Row leaves the pending list<br>☐ Bob's points do not change | Pass ☐ &nbsp; Fail ☐ |
| **UAT-08 Test Student cannot open admin page** | ☐ Must be logged in as a student | ☐ Type the address `/admin` in the browser | ☐ A Forbidden page is shown<br>☐ No approvals are visible | Pass ☐ &nbsp; Fail ☐ |
| **UAT-09 Test Redeem Award** | ☐ Must be logged in as a student with at least 15 points<br>☐ A reward costing 15 points with stock above 0 exists | ☐ Click **Rewards Catalogue**<br>☐ Click **Claim** on the reward | ☐ Message "Your redemption request was submitted." is shown<br>☐ Current Points go down by 15<br>☐ Stock goes down by 1<br>☐ Claim is listed under **Your Redemption Claims** as Submitted | Pass ☐ &nbsp; Fail ☐ |
| **UAT-10 Test Redeem with not enough points** | ☐ Must be logged in as a student with fewer points than the reward costs | ☐ Click **Rewards Catalogue**<br>☐ Look at the reward | ☐ **Claim** button is disabled<br>☐ Text "You need N more point(s)." is shown | Pass ☐ &nbsp; Fail ☐ |
| **UAT-11 Test Page without login** | ☐ User is logged out | ☐ Type the address `/app` in the browser | ☐ Session Expired page is shown<br>☐ Page has a link back to login | Pass ☐ &nbsp; Fail ☐ |

| General Comments | Accepted \| Rejected | Signature |
|---|---|---|
| | | |

---

## 2. Unit Test Plan

Unit tests mock every dependency, so no database is used. Files are in `tests/unit/`.

### test_models.py

| Unit Test | Input | Expected Output |
|---|---|---|
| test_new_user | "bob", "bob@example.com", "bobpass" | username == "bob" and total_points == 0 |
| test_new_volunteer_session | student 1, "Beach Cleanup", 3 hours, today | description == "Beach Cleanup" and status == "pending" |
| test_new_award | "Hoodie", "Warm", 100 points, stock 3 | name, points_required and stock_quantity are stored |
| test_new_redemption_claim | student 1, award 2 | status == "submitted" and claim_date is today |

### test_security.py

| Unit Test | Input | Expected Output |
|---|---|---|
| test_password_hash | "mypass" | hashed != "mypass" |
| test_check_password | "mypass" and "wrongpass" against the hash of "mypass" | True for "mypass", False for "wrongpass" |
| test_access_token | {"sub": "9", "role": "admin"} | Decoded token has sub "9", role "admin" and an expiry |

### test_auth_service.py

| Unit Test | Input | Expected Output |
|---|---|---|
| test_authenticate_user | "bob", "bobpass" (user found) | A token is returned |
| test_authenticate_wrong_password | "bob", "wrongpass" | None |
| test_authenticate_unknown_user | "ghost", "bobpass" (no user found) | None |
| test_register_user | "carl", "carl@example.com", "secret1" | New user has role regular_user and a hashed password |
| test_register_duplicate_username | "bob" (already exists) | ConflictError, nothing saved |
| test_register_duplicate_email | "newbie", "bob@example.com" (email exists) | ConflictError, nothing saved |
| test_register_short_password | "carl", "carl@example.com", "123" | InvalidInputError |

### test_volunteer_session_service.py (Workflows 1 and 2)

| Unit Test | Input | Expected Output |
|---|---|---|
| test_points_for_half_hour | 0.5 hours | 1 point |
| test_points_for_whole_hours | 1 hour, 3 hours | 1 point, 3 points |
| test_points_round_half_up | 1.5 hours, 2.5 hours | 2 points, 3 points |
| test_log_hours | student 7, "Library Tutoring", 2 hours, yesterday | Repository create is called once with these values |
| test_log_hours_trims_description | "  Tutoring  " | Saved as "Tutoring" |
| test_log_hours_empty_description | "   " | InvalidInputError, nothing saved |
| test_log_hours_zero_hours | 0 hours | InvalidInputError, nothing saved |
| test_log_hours_over_24_hours | 24.5 hours | InvalidInputError, nothing saved |
| test_log_hours_future_date | tomorrow's date | InvalidInputError, nothing saved |
| test_approve_session | pending session of 2.5 hours | Status becomes approved and 3 points are added once |
| test_approve_session_missing | session id 999 (not found) | NotFoundError |
| test_approve_session_already_approved | session already approved | ConflictError, no points added |
| test_approve_session_already_rejected | session already rejected | ConflictError, no points added |
| test_approve_session_points_fail | adding points raises an error | Error is raised and the status stays pending (not saved) |
| test_reject_session | pending session | Status becomes rejected and no points are added |
| test_reject_session_already_approved | session already approved | ConflictError |
| test_review_session_bad_decision | decision "maybe" | InvalidInputError |
| test_student_views_own_session | student 7, session owned by 7 | The session is returned |
| test_student_cannot_view_other_session | student 8, session owned by 7 | PermissionDeniedError |
| test_admin_views_any_session | admin, session owned by 7 | The session is returned |
| test_list_sessions_for_admin | admin, status "pending" | Repository is asked for pending sessions |
| test_list_sessions_for_student | student 7, status "approved", one pending and one approved session | Only the approved session is returned |
| test_list_sessions_bad_status | student 7, status "denied" | InvalidInputError |

### test_reward_redemption_service.py (Workflow 3)

| Unit Test | Input | Expected Output |
|---|---|---|
| test_redeem_award | student with 100 points, award costing 40 with stock 5 | 40 points deducted, stock becomes 4, claim is submitted |
| test_redeem_award_exact_points | student with 40 points, award costing 40 | Redemption works |
| test_redeem_award_not_enough_points | student with 10 points, award costing 40 | InvalidInputError, nothing changed |
| test_redeem_award_out_of_stock | student with 500 points, award with stock 0 | ConflictError, nothing changed |
| test_redeem_award_missing_award | award id 99 (not found) | NotFoundError |
| test_redeem_award_missing_student | student id 99 (not found) | NotFoundError |
| test_catalog_eligibility | student with 50 points; awards costing 15, 60, and 10 with stock 0 | Eligible, "You need 10 more point(s).", "Out of stock." |
| test_list_claims_for_student | a student | Only that student's claims are requested |
| test_list_claims_for_admin | an admin | All claims are requested |

### test_award_service.py

| Unit Test | Input | Expected Output |
|---|---|---|
| test_create_award | "  Hoodie ", " Warm ", 100 points, stock 3 | Saved with trimmed name "Hoodie" and description "Warm" |
| test_create_award_blank_name | name "   " | InvalidInputError, nothing saved |
| test_create_award_zero_points | points_required 0 | InvalidInputError, nothing saved |
| test_create_award_negative_stock | stock_quantity -1 | InvalidInputError, nothing saved |
| test_update_award | award 4, stock_quantity 10 | Stock is 10, name and points are unchanged |
| test_update_award_missing | award id 99 (not found) | NotFoundError |
| test_delete_award | award 4 with 0 claims | Award is deleted |
| test_delete_award_with_claims | award 4 with 2 claims | ConflictError, award kept |

---

## 3. Integration Test Plan

Integration tests use a real in-memory SQLite database that is empty at the start of every test. Files are in `tests/integration/`.

### test_user_repository.py

| Test | Dependencies | Description |
|---|---|---|
| test_create_user | UserRepository, database | A saved user gets an id and can be read back |
| test_get_user_by_username | UserRepository, database | Finds the user by username |
| test_get_user_by_email | UserRepository, database | Finds the user by email |
| test_get_unknown_user | UserRepository, database | Returns None |
| test_add_points | UserRepository, database | Total points go up and are saved |
| test_deduct_points | UserRepository, database | Total points go down and are saved |
| test_deduct_too_many_points | UserRepository, database | Error is raised and points are unchanged |
| test_points_must_be_positive | UserRepository, database | Error for 0 or negative points |
| test_add_points_unknown_user | UserRepository, database | Error for a user that does not exist |
| test_add_points_without_commit | UserRepository, database | Change is not saved until the caller commits |

### test_volunteer_sessions.py (Workflows 1 and 2)

| Test | Dependencies | Description |
|---|---|---|
| test_log_hours | VolunteerSessionService, repositories, database | Logged hours are saved as pending |
| test_approve_session_awards_points | VolunteerSessionService, repositories, database | Approval sets status approved and adds points to the student |
| test_approve_half_hour_session | VolunteerSessionService, repositories, database | 0.5 hours gives 1 point |
| test_approve_session_twice | VolunteerSessionService, repositories, database | Second approval fails and points are added only once |
| test_reject_session | VolunteerSessionService, repositories, database | Status becomes rejected and points stay the same |
| test_reject_session_after_approval | VolunteerSessionService, repositories, database | Fails and points are kept |
| test_get_pending_sessions | VolunteerSessionService, repositories, database | Only pending sessions are listed |
| test_student_sees_only_own_sessions | VolunteerSessionService, repositories, database | Other students' sessions are not listed |

### test_redemptions.py (Workflow 3 and awards)

| Test | Dependencies | Description |
|---|---|---|
| test_redeem_award | RewardRedemptionService, repositories, database | Points, stock and claim all change |
| test_redeem_award_not_enough_points | RewardRedemptionService, repositories, database | Fails and points, stock and claims are unchanged |
| test_redeem_award_out_of_stock | RewardRedemptionService, repositories, database | Fails and points are unchanged |
| test_redeem_last_item_twice | RewardRedemptionService, repositories, database | Second student cannot redeem the last item |
| test_redeem_missing_award | RewardRedemptionService, repositories, database | Fails with not found |
| test_pending_hours_do_not_count | VolunteerSessionService, RewardRedemptionService, database | Pending hours give no points, so redeeming fails |
| test_log_approve_and_redeem | All services, database | Full flow: log, approve, redeem |
| test_create_and_update_award | AwardService, repositories, database | Award is created and then changed |
| test_list_awards_cheapest_first | AwardRepository, database | Awards are sorted by points required |
| test_delete_award | AwardService, repositories, database | Award is removed |
| test_delete_award_with_claims | AwardService, repositories, database | Fails and award is kept |

### test_api_auth.py (login and authorization through the API)

| Test | Dependencies | Description |
|---|---|---|
| test_register_and_login | FastAPI app, database | Register gives 201, login gives a token, the token opens `/api/users/me` |
| test_register_duplicate_username | FastAPI app, database | 409 |
| test_register_invalid_body | FastAPI app | 422 |
| test_login_wrong_password | FastAPI app, database | 401 |
| test_no_token | FastAPI app | 401 as JSON |
| test_bad_token | FastAPI app | 401 |
| test_cookie_token | FastAPI app, database | The access_token cookie also works |
| test_student_cannot_list_users | FastAPI app, database | 403 |
| test_admin_can_list_users | FastAPI app, database | 200 with all users |
| test_student_cannot_approve_hours | FastAPI app, database | 403 |
| test_student_cannot_create_award | FastAPI app, database | 403 |
| test_admin_cannot_log_hours | FastAPI app, database | 403 |
| test_admin_cannot_redeem_award | FastAPI app, database | 403 |
| test_other_user_cannot_see_session | FastAPI app, database | 403 |

### test_api_workflows.py (the three workflows through the API)

| Test | Dependencies | Description |
|---|---|---|
| test_log_hours | FastAPI app, database | 201 and status pending |
| test_log_hours_zero_hours | FastAPI app | 422 |
| test_log_hours_missing_date | FastAPI app | 422 |
| test_log_hours_future_date | FastAPI app, database | 400 |
| test_log_hours_blank_description | FastAPI app, database | 400 |
| test_students_only_see_their_own_sessions | FastAPI app, database | List has only the student's sessions |
| test_missing_session | FastAPI app, database | 404 |
| test_approve_hours | FastAPI app, database | 200, status approved, points added |
| test_admin_lists_pending_sessions | FastAPI app, database | `?status=pending` lists only pending |
| test_approve_half_hour | FastAPI app, database | 0.5 hours gives 1 point |
| test_approve_twice | FastAPI app, database | 409 and points added once |
| test_reject_hours | FastAPI app, database | 200, status rejected, no points |
| test_review_with_invalid_status | FastAPI app, database | 422 |
| test_review_missing_session | FastAPI app, database | 404 |
| test_redeem_award | FastAPI app, database | 201, points down, stock down, claim listed |
| test_redeem_award_not_enough_points | FastAPI app, database | 400 and stock unchanged |
| test_redeem_award_out_of_stock | FastAPI app, database | 409 and points unchanged |
| test_redeem_missing_award | FastAPI app, database | 404 |
| test_admin_sees_all_claims | FastAPI app, database | Admin list has every claim |
| test_admin_manages_awards | FastAPI app, database | Create 201, update 200, list, delete 204, then 404 |
| test_create_award_invalid_values | FastAPI app | 422 |
| test_delete_award_with_claims | FastAPI app, database | 409 |

### test_web_pages.py (the screens in the wireframes)

| Test | Dependencies | Description |
|---|---|---|
| test_student_login | FastAPI app, templates, database | Student lands on `/app` |
| test_admin_login | FastAPI app, templates, database | Admin lands on `/admin` |
| test_bad_login | FastAPI app, templates, database | Stays on login with an error message |
| test_pages_need_login | FastAPI app, templates | `/app`, `/app/rewards` and `/admin` give 401 and the Session Expired page |
| test_student_cannot_open_admin_page | FastAPI app, templates, database | 403 Forbidden page |
| test_logout | FastAPI app, database | After logout the pages give 401 |
| test_register_page | FastAPI app, templates, database | New account can then log in |
| test_log_hours_form | FastAPI app, templates, database | Success message and a Pending row |
| test_log_hours_form_future_date | FastAPI app, templates, database | Error message about the date |
| test_admin_approve_and_reject_buttons | FastAPI app, templates, database | Both buttons work and points are awarded only for approval |
| test_rewards_page_claim | FastAPI app, templates, database | Claim works, points and stock change, a too expensive award is refused |

---

## 4. API Test Plan (Postman)

Collection: `postman/student-awards.postman_collection.json`. Environments: `local.postman_environment.json` (http://localhost:5000) and `render.postman_environment.json` (the Render URL). Every request has test scripts. Run the folders in order.

| Description | Method | URL | Request Headers, Body | Response Body, Status |
|---|---|---|---|---|
| Health check | GET | /health | none | 200 `{"ok": true}` |
| Register student | POST | /api/auth/register | username, email, password | 201 user, role regular_user, 0 points, no password |
| Register duplicate username | POST | /api/auth/register | same username | 409 |
| Register invalid email | POST | /api/auth/register | bad email | 422 |
| Login student | POST | /api/auth/login | username, password | 200 access_token |
| Login admin | POST | /api/auth/login | admin login | 200 access_token |
| Login wrong password | POST | /api/auth/login | wrong password | 401 |
| Get current user | GET | /api/users/me | Bearer token | 200 user |
| Get current user without token | GET | /api/users/me | none | 401 JSON |
| Get current user with bad token | GET | /api/users/me | bad Bearer token | 401 |
| Student lists users | GET | /api/users | student token | 403 |
| Admin lists users | GET | /api/users | admin token | 200 list |
| Student logs volunteer hours | POST | /api/volunteer-sessions | description, hours_logged 20, date | 201 pending session |
| Log hours with 0 hours | POST | /api/volunteer-sessions | hours_logged 0 | 422 |
| Log hours with future date | POST | /api/volunteer-sessions | future date | 400 |
| Admin cannot log hours | POST | /api/volunteer-sessions | admin token | 403 |
| Student lists own sessions | GET | /api/volunteer-sessions | student token | 200 list |
| Student gets session by id | GET | /api/volunteer-sessions/{{sessionId}} | student token | 200 session |
| Student cannot approve | PATCH | /api/volunteer-sessions/{{sessionId}} | status approved | 403 |
| Admin lists pending sessions | GET | /api/volunteer-sessions?status=pending | admin token | 200 list |
| Admin approves session | PATCH | /api/volunteer-sessions/{{sessionId}} | status approved | 200 approved |
| Approve same session again | PATCH | /api/volunteer-sessions/{{sessionId}} | status approved | 409 |
| Invalid review status | PATCH | /api/volunteer-sessions/{{sessionId}} | status maybe | 422 |
| Student points after approval | GET | /api/users/me | student token | 200 total_points 20 |
| Student logs a second session | POST | /api/volunteer-sessions | 4 hours | 201 |
| Admin rejects second session | PATCH | /api/volunteer-sessions/{{rejectSessionId}} | status rejected | 200 rejected |
| Points unchanged after rejection | GET | /api/users/me | student token | 200 total_points 20 |
| Get missing session | GET | /api/volunteer-sessions/99999999 | admin token | 404 |
| Admin creates award | POST | /api/awards | name, 15 points, stock 1 | 201 |
| Admin creates expensive award | POST | /api/awards | 100000 points | 201 |
| Create award with invalid values | POST | /api/awards | 0 points, stock -1 | 422 |
| Student cannot create award | POST | /api/awards | student token | 403 |
| Admin updates award description | PATCH | /api/awards/{{awardId}} | description | 200 |
| Student lists awards | GET | /api/awards | student token | 200 list |
| Student gets award by id | GET | /api/awards/{{awardId}} | student token | 200 |
| Student redeems award | POST | /api/redemptions | award_id | 201 submitted |
| Points deducted after redemption | GET | /api/users/me | student token | 200 total_points 5 |
| Award stock decremented | GET | /api/awards/{{awardId}} | student token | 200 stock 0 |
| Redeem out of stock award | POST | /api/redemptions | award_id | 409 |
| Redeem with not enough points | POST | /api/redemptions | expensive award_id | 400 |
| Points unchanged after failed redemptions | GET | /api/users/me | student token | 200 total_points 5 |
| Redeem missing award | POST | /api/redemptions | award_id 99999999 | 404 |
| Admin cannot redeem | POST | /api/redemptions | admin token | 403 |
| Student lists own claims | GET | /api/redemptions | student token | 200 one claim |
| Admin lists all claims | GET | /api/redemptions | admin token | 200 list |
| Delete award with claims | DELETE | /api/awards/{{awardId}} | admin token | 409 |
| Admin deletes unused award | DELETE | /api/awards/{{expensiveAwardId}} | admin token | 204 |
| Deleted award returns 404 | GET | /api/awards/{{expensiveAwardId}} | student token | 404 |
