import builtins
import pytest
from unittest.mock import Mock

from PlaneWatcher import PlaneWatcher
from AircraftResp import AircraftResp
from AirplanesLive_Client import AirplanesClient


def make_sample(hex_id: str, flight: str, designator: str, lat: float = 42.52, lon: float = -71.42, alt: float = 500.0):
    return {
        "hex": hex_id,
        "flight": flight,
        "t": designator,
        "desc": "Test Aircraft",
        "alt_baro": alt,
        "lat": lat,
        "lon": lon,
    }


def test_refresh_populates_aircraft(monkeypatch):
    watcher = PlaneWatcher(42.52, -71.42, 10)

    # prepare mock client to return two sample aircraft dicts
    sample1 = make_sample("ABC123", "FLT1", "A21N")
    sample2 = make_sample("DEF456", "FLT2", "H123")
    mock_client = Mock()
    mock_client.get_point = Mock(return_value=[sample1, sample2])
    watcher.client = mock_client

    watcher.refresh()

    assert len(watcher.aircraft) == 2
    assert isinstance(watcher.aircraft[0], AircraftResp)
    assert watcher.aircraft[0].hex == "ABC123"


def test_is_helicopter_and_print(monkeypatch, capsys):
    watcher = PlaneWatcher(42.52, -71.42, 10)

    # Inject aircraft types mapping: H123 is a helicopter
    watcher._PlaneWatcher__aircraft_types.aircraft_types = [
        {"Designator": "A21N", "AircraftDescription": "Airplane"},
        {"Designator": "H123", "AircraftDescription": "Helicopter"},
    ]

    # Prepare data: one airplane, one helicopter
    heli = make_sample("HELI01", "HEL1", "H123", lat=42.5205, lon=-71.419)
    plane = make_sample("PLANE1", "PLA1", "A21N", lat=42.6, lon=-71.5)

    mock_client = Mock()
    mock_client.get_point = Mock(return_value=[heli, plane])
    watcher.client = mock_client

    # Refresh to populate watcher.aircraft
    watcher.refresh()

    # Verify is_helicopter
    assert watcher.is_helicopter(watcher.aircraft[0].t) is True or watcher.is_helicopter(watcher.aircraft[1].t) is True

    # Capture printed output from print_helicopters
    watcher.print_helicopters()
    captured = capsys.readouterr()
    out = captured.out

    # Should print at least one helicopter line containing the heli hex and flight
    assert "HELI01" in out
    assert "HEL1" in out
