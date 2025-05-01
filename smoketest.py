import requests


def run_smoketest():
    base_url = "http://localhost:5000/api"
    username = "test"
    password = "test"


    goal_biceps = {
        "target": "biceps",
        "goal_value": 40,
        "goal_progress": 35,
        "completed": False,
        "progress_notes": "[]"
    }

    goal_pecs = {
        "target": "pectorals",
        "goal_value": 200,
        "goal_progress": 225,
        "completed": True,
        "progress_ntoes": "[]"
    }

    health_response = requests.get(f"{base_url}/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "success"

    delete_user_response = requests.delete(f"{base_url}/reset-users")
    assert delete_user_response.status_code == 200
    assert delete_user_response.json()["status"] == "success"
    print("Reset users successful")

    delete_goal_response = requests.delete(f"{base_url}/reset-goals")
    assert delete_goal_response.status_code == 200
    assert delete_goal_response.json()["status"] == "success"
    print("Reset goal successful")

    create_user_response = requests.put(f"{base_url}/create-user", json={
        "username": username,
        "password": password
    })
    assert create_user_response.status_code == 201
    assert create_user_response.json()["status"] == "success"
    print("User creation successful")

    session = requests.Session()

    # Log in
    login_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": password
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["status"] == "success"
    print("Login successful")

    create_goal_resp = session.post(f"{base_url}/create-goal", json=goal_biceps)
    assert create_goal_resp.status_code == 201
    assert create_goal_resp.json()["status"] == "success"
    print("Boxer creation successful")

    # Change password
    change_password_resp = session.post(f"{base_url}/change-password", json={
        "new_password": "new_password"
    })
    assert change_password_resp.status_code == 200
    assert change_password_resp.json()["status"] == "success"
    print("Password change successful")

    # Log in with new password
    login_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": "new_password"
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["status"] == "success"
    print("Login with new password successful")

    create_boxer_resp = session.post(f"{base_url}/create-goal", json=goal_pecs)
    assert create_boxer_resp.status_code == 201
    assert create_boxer_resp.json()["status"] == "success"
    print("goal creation successful")

    # Log out
    logout_resp = session.post(f"{base_url}/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["status"] == "success"
    print("Logout successful")

    create_boxer_logged_out_resp = session.post(f"{base_url}/create-goal", json=goal_pecs)
    # This should fail because we are logged out
    assert create_boxer_logged_out_resp.status_code == 401
    assert create_boxer_logged_out_resp.json()["status"] == "error"
    print("goal creation failed as expected")

if __name__ == "__main__":
    run_smoketest()
