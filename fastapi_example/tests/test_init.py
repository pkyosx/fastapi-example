class TestAppInit:
    def test_app_init__api_doc(self, client):
        resp = client.get("/api_doc/swagger")
        assert resp.status_code == 200

        resp = client.get("/api_doc/openapi.json")
        assert resp.status_code == 200

        resp = client.get("/api_doc/redoc")
        assert resp.status_code == 200

    def test_app_init__healthcheck(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_app_init__metrics(self, client):
        resp = client.get("/metrics")
        assert resp.status_code == 200
