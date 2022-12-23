from src.entrypoints.web.api.v1 import url


def test_api_info(api):
    result = api.simulate_get(url('/api-info'))
    assert result.status_code == 200
