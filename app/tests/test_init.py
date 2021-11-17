class TestAppInit:
    def test_app_init__api_doc(self, client):
        resp = client.get("/api_doc/swagger")
        assert resp.status_code == 200

        resp = client.get("/api_doc/openapi.json")
        assert resp.status_code == 200

        resp = client.get("/api_doc/redoc")
        assert resp.status_code == 200
