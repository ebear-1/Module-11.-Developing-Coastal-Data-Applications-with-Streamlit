import pandas as pd
import xarray as xr
from datetime import datetime
from wavespectra.input.ndbc import from_ndbc

OPENDAP_BASE = "https://dods.ndbc.noaa.gov/thredds/dodsC/data/swden"

REALTIME_TAG = "9999"
REALTIME_LOOKBACK_DAYS = 45
DEFAULT_DIRECTIONAL_RESOLUTION_DEG = 10.0
DEFAULT_TIME_TOLERANCE = "1h"


def to_utc_timestamp(value: datetime | pd.Timestamp | str) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        return ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def choose_year_tag(requested_time_utc: datetime | pd.Timestamp | str) -> str:
    requested = to_utc_timestamp(requested_time_utc)
    now = pd.Timestamp.now(tz="UTC")
    
    if requested >= now - pd.Timedelta(days=REALTIME_LOOKBACK_DAYS):
        return REALTIME_TAG
    return f"{requested.year}"


def open_directional_dataset(
    station_id: str,
    requested_time_utc: datetime | pd.Timestamp | str,
    directional: bool = True,
    dd: float = DEFAULT_DIRECTIONAL_RESOLUTION_DEG,
    tolerance: str = DEFAULT_TIME_TOLERANCE,
):
    """Open nearest requested time from NDBC dataset. Returns (spec, info_dict)."""
    year_tag = choose_year_tag(requested_time_utc)
    filename = f"{station_id}w{year_tag}.nc"
    url = f"{OPENDAP_BASE}/{station_id}/{filename}"
    
    requested_utc = to_utc_timestamp(requested_time_utc)
    requested_key = requested_utc.tz_localize(None)
    tolerance_td = pd.Timedelta(tolerance)
    
    try:
        ds = xr.open_dataset(url, engine="netcdf4")
        ds_one = ds.sel(time=[requested_key], method="nearest", tolerance=tolerance_td)
        spec = from_ndbc(ds_one, directional=directional, dd=dd)
        used_time = pd.to_datetime(ds_one.time.values[0], utc=True)
    except Exception as exc:
        raise RuntimeError(f"Failed to retrieve {url}: {exc}") from exc
    
    delta_minutes = abs((used_time - requested_utc).total_seconds()) / 60.0
    info = {
        "requested_time": requested_utc,
        "used_time": used_time,
        "delta_minutes": delta_minutes,
    }
    return spec, info
