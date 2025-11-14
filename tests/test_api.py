from fastapi.testclient import TestClient
from src.app import app
from urllib.parse import quote

client = TestClient(app)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # basic check: known activity present
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser+pytest@mergington.edu"

    # Ensure the test email is not present to start with
    res = client.get("/activities")
    assert res.status_code == 200
    participants = res.json()[activity]["participants"]
    if email in participants:
        # remove if leftover from previous run
        client.delete(f"/activities/{activity}/unregister?email={email}")

    # Sign up (encode email so '+' is preserved)
    encoded = quote(email, safe="")
    signup_res = client.post(f"/activities/{activity}/signup?email={encoded}")
    assert signup_res.status_code == 200
    assert "Signed up" in signup_res.json().get("message", "")

    # Verify participant appears
    res_after = client.get("/activities")
    participants_after = res_after.json()[activity]["participants"]
    assert email in participants_after

    # Unregister
    del_res = client.delete(f"/activities/{activity}/unregister?email={encoded}")
    assert del_res.status_code == 200
    assert "Unregistered" in del_res.json().get("message", "")

    # Verify participant removed
    res_final = client.get("/activities")
    participants_final = res_final.json()[activity]["participants"]
    assert email not in participants_final
