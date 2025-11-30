from src.app import create_app
from src.pipeline import run_pipeline

def test_recommend_endpoint_returns_n():
    run_pipeline()

    app = create_app()
    client = app.test_client()

    r = client.get("/recommend?item_id=1&n=3")
    assert r.status_code == 200
    assert "recommendations" in r.json
    assert len(r.json["recommendations"]) == 3
