"""Dataclass model for the new Airplanes.live aircraft JSON record.

This version models the flattened format from the JSON you provided. It
includes convenience helpers and a haversine-based distance calculator.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class AircraftResp:
    # identity
    hex: str
    type: str = ""
    flight: Optional[str] = None

    # registration / type / description
    r: str = ""
    t: str = ""
    desc: Optional[str] = None

    # altitudes / speeds
    alt_baro: Optional[float] = None
    alt_geom: Optional[float] = None
    gs: Optional[float] = None

    # navigation
    track: Optional[float] = None
    baro_rate: Optional[float] = None
    nav_qnh: Optional[float] = None
    nav_altitude_mcp: Optional[float] = None
    nav_heading: Optional[float] = None

    # position (flattened)
    lat: Optional[float] = None
    lon: Optional[float] = None
    nic: Optional[int] = None
    rc: Optional[int] = None
    seen_pos: Optional[float] = None

    # other
    squawk: Optional[str] = None
    emergency: Optional[str] = None
    category: Optional[str] = None
    sil: Optional[int] = None
    sil_type: Optional[str] = None
    gva: Optional[int] = None
    sda: Optional[int] = None
    alert: Optional[int] = None
    spi: Optional[int] = None

    mlat: Optional[List[Any]] = None
    tisb: Optional[List[Any]] = None
    messages: Optional[int] = None
    seen: Optional[float] = None
    rssi: Optional[float] = None

    # derived / convenience fields in this payload
    dst: Optional[float] = None  # distance to observer (km or nm depending on API)
    dir: Optional[float] = None

    # metadata
    version: Optional[int] = None
    nic_baro: Optional[int] = None
    nac_p: Optional[int] = None
    nac_v: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AircraftResp":
        return cls(
            hex=data.get("hex",""),
            type=data.get("type",""),
            flight=data.get("flight",""),
            r=data.get("r",""),
            t=data.get("t",""),
            desc=data.get("desc"),
            alt_baro=data.get("alt_baro"),
            alt_geom=data.get("alt_geom"),
            gs=data.get("gs"),
            track=data.get("track"),
            baro_rate=data.get("baro_rate"),
            nav_qnh=data.get("nav_qnh"),
            nav_altitude_mcp=data.get("nav_altitude_mcp"),
            nav_heading=data.get("nav_heading"),
            lat=data.get("lat"),
            lon=data.get("lon"),
            nic=data.get("nic"),
            rc=data.get("rc"),
            seen_pos=data.get("seen_pos"),
            squawk=(data.get("squawk") or None),
            emergency=data.get("emergency"),
            category=data.get("category"),
            sil=data.get("sil"),
            sil_type=data.get("sil_type"),
            gva=data.get("gva"),
            sda=data.get("sda"),
            alert=data.get("alert"),
            spi=data.get("spi"),
            mlat=data.get("mlat"),
            tisb=data.get("tisb"),
            messages=data.get("messages"),
            seen=data.get("seen"),
            rssi=data.get("rssi"),
            dst=data.get("dst"),
            dir=data.get("dir"),
            version=data.get("version"),
            nic_baro=data.get("nic_baro"),
            nac_p=data.get("nac_p"),
            nac_v=data.get("nac_v"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hex": self.hex,
            "type": self.type,
            "flight": self.flight,
            "r": self.r,
            "t": self.t,
            "desc": self.desc,
            "alt_baro": self.alt_baro,
            "alt_geom": self.alt_geom,
            "gs": self.gs,
            "track": self.track,
            "baro_rate": self.baro_rate,
            "nav_qnh": self.nav_qnh,
            "nav_altitude_mcp": self.nav_altitude_mcp,
            "nav_heading": self.nav_heading,
            "lat": self.lat,
            "lon": self.lon,
            "nic": self.nic,
            "rc": self.rc,
            "seen_pos": self.seen_pos,
            "squawk": self.squawk,
            "emergency": self.emergency,
            "category": self.category,
            "sil": self.sil,
            "sil_type": self.sil_type,
            "gva": self.gva,
            "sda": self.sda,
            "alert": self.alert,
            "spi": self.spi,
            "mlat": self.mlat,
            "tisb": self.tisb,
            "messages": self.messages,
            "seen": self.seen,
            "rssi": self.rssi,
            "dst": self.dst,
            "dir": self.dir,
            "version": self.version,
            "nic_baro": self.nic_baro,
            "nac_p": self.nac_p,
            "nac_v": self.nac_v,
        }

    # convenience helpers
    def position(self) -> Optional[Tuple[float, float]]:
        if self.lat is None or self.lon is None:
            return None
        return (self.lat, self.lon)

    def altitude_meters(self) -> Optional[float]:
        if self.alt_baro is None:
            return None
        return float(self.alt_baro) * 0.3048

    def is_on_ground(self, threshold_feet: float = 50.0) -> bool:
        if self.alt_baro is None:
            return False
        try:
            return float(self.alt_baro) <= float(threshold_feet)
        except Exception:
            return False

    def distance_to(self, lat: float, lon: float, unit: str = "km") -> Optional[float]:
        """Compute great-circle distance from this aircraft to (lat, lon).

        Default unit is kilometers (this payload's `dst` field looked like km).
        Set unit to "nm" for nautical miles.
        """
        pos = self.position()
        if pos is None:
            return None
        lat1, lon1 = pos
        import math

        def _deg2rad(d: float) -> float:
            return d * (math.pi / 180.0)

        r_km = 6371.0088
        phi1 = _deg2rad(lat1)
        phi2 = _deg2rad(lat)
        dphi = _deg2rad(lat - lat1)
        dlambda = _deg2rad(lon - lon1)

        a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1 - a)))
        dist_km = r_km * c
        if unit == "km":
            return dist_km
        return dist_km / 1.852
