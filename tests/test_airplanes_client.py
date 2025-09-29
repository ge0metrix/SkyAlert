import unittest
from unittest.mock import Mock, patch
import httpx
from AirplanesLive_Client import AirplanesClient

class DummyResponse:
    def __init__(self, status_code=None, json_data=None, raise_exc=None):
        self._json = json_data
        self._raise_exc = raise_exc

    def raise_for_status(self):
        if self._raise_exc:
            raise self._raise_exc

    def json(self):
        return self._json


class TestAirplanesClient(unittest.TestCase):
    def test_get_icao_success(self):
        client = AirplanesClient(rate_limit_seconds=0, max_retries=1)
        resp = Mock()
        resp.raise_for_status = Mock()
        resp.json = Mock(return_value={"icao": "45211e"})
        client.client = Mock(get=Mock(return_value=resp))

        result = client.get_icao("45211e")
        self.assertEqual(result, {"icao": "45211e"})

    def test_retry_on_http_5xx_then_success(self):
        client = AirplanesClient(rate_limit_seconds=0, max_retries=3)

        # First response will raise an HTTPStatusError with status_code 500
        req = httpx.Request("GET", "https://api.airplanes.live/v2/icao/whatever")
        resp_obj = httpx.Response(500, request=req)
        http_exc = httpx.HTTPStatusError("Server error", request=req, response=resp_obj)
        resp1 = DummyResponse(status_code=500, raise_exc=http_exc)
        resp2 = DummyResponse(json_data={"ok": True})

        get_mock = Mock(side_effect=[resp1, resp2])
        client.client = Mock(get=get_mock)

        # Patch time.sleep to avoid delays from backoff in tests
        with patch("time.sleep", return_value=None):
            result = client.get_icao("whatever")

        self.assertEqual(result, {"ok": True})

    def test_request_error_retries_and_raises(self):
        client = AirplanesClient(rate_limit_seconds=0, max_retries=2)

        # make client.get raise RequestError twice so retries exhaust
        req_exc = httpx.RequestError("network")
        get_mock = Mock(side_effect=[req_exc, req_exc])
        client.client = Mock(get=get_mock)

        with patch("time.sleep", return_value=None):
            with self.assertRaises(httpx.RequestError):
                client.get_icao("x")

    def test_get_point_success(self):
        """Ensure get_point constructs the correct path and returns JSON."""
        client = AirplanesClient(rate_limit_seconds=0, max_retries=1)
        # prepare a fake JSON list of aircraft
        expected = [{"hex": "abc123"}, {"hex": "def456"}]
        resp = Mock()
        resp.raise_for_status = Mock()
        resp.json = Mock(return_value=expected)

        # capture the call args to get
        get_mock = Mock(return_value=resp)
        client.client = Mock(get=get_mock)

        lat, lon, radius = 51.5, -0.12, 50
        result = client.get_point(lat, lon, radius)

        # verify return value and that the client.get was called with the correct path
        self.assertEqual(result, expected)
        get_mock.assert_called_once()
        called_path = get_mock.call_args[0][0]
        self.assertEqual(called_path, f"/point/{lat}/{lon}/{radius}")


import time

import pytest
from unittest.mock import Mock

import httpx

from AirplanesLive_Client import AirplanesClient


@pytest.fixture
def client():
    return AirplanesClient(rate_limit_seconds=0, max_retries=2)


def make_resp(json_data=None, raise_exc=None):
    resp = Mock()
    if raise_exc:
        resp.raise_for_status = Mock(side_effect=raise_exc)
    else:
        resp.raise_for_status = Mock()
    resp.json = Mock(return_value=json_data)
    return resp


def test_get_icao_success(client):
    resp = make_resp({"icao": "45211e"})
    client.client = Mock(get=Mock(return_value=resp))

    assert client.get_icao("45211e") == {"icao": "45211e"}


def test_get_hex_calls_correct_path(client):
    resp = make_resp([{"hex": "a"}])
    get_mock = Mock(return_value=resp)
    client.client = Mock(get=get_mock)

    result = client.get_hex(["aa", "bb"])
    assert result == [{"hex": "a"}]
    called_path = get_mock.call_args[0][0]
    assert called_path == "/hex/aa,bb"


def test_get_callsign_reg_type_and_squawk(client):
    resp = make_resp([{"k": "v"}])
    get_mock = Mock(return_value=resp)
    client.client = Mock(get=get_mock)

    assert client.get_callsign("SOME123") == [{"k": "v"}]
    assert client.get_reg(["N12345"]) == [{"k": "v"}]
    assert client.get_type(["B738"]) == [{"k": "v"}]
    assert client.get_squawk("7000") == [{"k": "v"}]


def test_mil_ladd_pia_endpoints(client):
    resp = make_resp([{"x": 1}])
    get_mock = Mock(return_value=resp)
    client.client = Mock(get=get_mock)

    assert client.get_mil() == [{"x": 1}]
    assert client.get_ladd() == [{"x": 1}]
    assert client.get_pia() == [{"x": 1}]


def test_get_point_success(client):
    expected = [{"hex": "abc123"}, {"hex": "def456"}]
    resp = make_resp(expected)
    get_mock = Mock(return_value=resp)
    client.client = Mock(get=get_mock)

    lat, lon, radius = 51.5, -0.12, 50
    result = client.get_point(lat, lon, radius)

    assert result == expected
    called_path = get_mock.call_args[0][0]
    assert called_path == f"/point/{lat}/{lon}/{radius}"

def test_get_point_fail(client):
    expected = [{"hex": "abc123"}, {"hex": "def456"}]
    resp = make_resp(expected)
    get_mock = Mock(return_value=resp)
    client.client = Mock(get=get_mock)

    lat, lon, radius = 120.5, -0.12, -5
    with pytest.raises(ValueError):
        result = client.get_point(lat, lon, radius)



def test_retry_on_http_5xx_then_success(client, monkeypatch):
    # First call raises HTTPStatusError (500), second returns OK
    req = httpx.Request("GET", "https://api.airplanes.live/v2/icao/whatever")
    resp_obj = httpx.Response(500, request=req)
    http_exc = httpx.HTTPStatusError("Server error", request=req, response=resp_obj)

    resp1 = make_resp(raise_exc=http_exc)
    resp2 = make_resp({"ok": True})

    get_mock = Mock(side_effect=[resp1, resp2])
    client.client = Mock(get=get_mock)

    # avoid sleeping during backoff
    monkeypatch.setattr(time, "sleep", lambda s: None)

    assert client.get_icao("whatever") == {"ok": True}


def test_request_error_retries_and_raises(client, monkeypatch):
    # Make client.get raise RequestError twice so retries exhaust
    req_exc = httpx.RequestError("network")
    get_mock = Mock(side_effect=[req_exc, req_exc])
    client.client = Mock(get=get_mock)

    monkeypatch.setattr(time, "sleep", lambda s: None)

    with pytest.raises(httpx.RequestError):
        client.get_icao("x")
