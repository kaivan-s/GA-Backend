from app import create_app


def test_healthz():
    app = create_app()
    client = app.test_client()
    assert client.get("/healthz").status_code == 200


def test_readyz():
    app = create_app()
    client = app.test_client()
    assert client.get("/readyz").status_code == 200
