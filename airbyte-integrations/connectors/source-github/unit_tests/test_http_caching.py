import time
from unittest.mock import MagicMock

import pytest
import responses
from source_github.source import SourceGithub

@pytest.mark.usefixtures("mitmproxy_cache")
def test_http_caching():
    """Test that HTTP requests are cached when using mitmproxy."""
    config = {
        "credentials": {"access_token": "test_token"},
        "repository": "airbytehq/airbyte",
    }
    source = SourceGithub()
    source.check_connection(MagicMock(), config)

    # First request should hit the API
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://api.github.com/rate_limit",
            json={"resources": {"core": {"remaining": 5000, "reset": int(time.time()) + 3600}}},
            status=200,
        )
        source.check_connection(MagicMock(), config)
        assert len(rsps.calls) == 1

    # Second request should be served from cache
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://api.github.com/rate_limit",
            json={"resources": {"core": {"remaining": 5000, "reset": int(time.time()) + 3600}}},
            status=200,
        )
        source.check_connection(MagicMock(), config)
        assert len(rsps.calls) == 0  # No calls to mock since request was cached
