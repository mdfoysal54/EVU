def test_security_me_endpoint_exists(client):
    response = client.get("/api/v1/security/me")

    assert response.status_code != 404


def test_security_check_endpoint_exists(client):
    response = client.post(
        "/api/v1/security/check",
        json={
            "permission": "CHAT"
        },
    )

    assert response.status_code != 404