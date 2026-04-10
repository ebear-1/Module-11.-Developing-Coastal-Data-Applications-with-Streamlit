import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from buoy_selector import build_map, extract_selected_station_id
from ndbc_io import open_directional_dataset
from plotting import plot_directional_spectrum
 
def combine_user_datetime(date_value, time_value, tz_name: str) -> pd.Timestamp:
     local_dt = datetime.combine(date_value, time_value)
     localized = pd.Timestamp(local_dt, tz=ZoneInfo(tz_name))
     return localized.tz_convert("UTC")

def main():
    # First step in every Streamlit app is to call st.set_page_config. It only needs to be called once per app, and it should be called as early as possible in the execution of the script.
    st.set_page_config(page_title="NDBC Directional Spectra App", layout="wide")

    # Set a title for the app
    st.title("Directional wave spectra from selected NDBC buoys 🌊")

    # Write some instructions for the user
    st.info(
        "Click a buoy on the map, choose a date and time, and the app will open the "
        "NDBC THREDDS NetCDF spectral dataset, pull only the nearest time record, and "
        "plot the directional wave spectrum."
    )

    # Include sidebar controls for date/time input and time zone selection
    with st.sidebar:
            st.header("Instructions")
            st.write("1. Use the date and time picker to choose a date and time (in your local timezone).")

            st.header("Controls")
            tz_name = st.selectbox("Time zone for your input", ["UTC", "America/New_York"], index=0)
            st.write(f"Selected time zone: {tz_name}")
            date_value = st.date_input("Date")
            time_value = st.time_input("Time")
            requested_time_utc = combine_user_datetime(date_value, time_value, tz_name)
            st.success(f"Your selected date and time in UTC is: {requested_time_utc}")

    # Divide the main page into two rows: one for results and one for diagnostics
    results_row = st.container()
    with results_row:
        res_col1, res_col2 = st.columns([1, 1])
    diagnostics_row = st.container()
    with diagnostics_row:
        diag_col1, diag_col2 = st.columns([1, 1])

    # Build the buoy DataFrame and map

    buoys = {"station_id":["41117","42036","41009"],
             "name":["St. Augustine","West Tampa","Cape Canaveral"],
             "latitude":[29.999, 28.500, 28.508],
             "longitude":[-81.079, -84.505, -80.185],
             "region":["St. Augustine","West Tampa","Cape Canaveral"]}
    
    buoy_df = pd.DataFrame(buoys)

    with res_col1:
        st.subheader("Buoy Map")
        st.write(
            "This map shows the locations of the available buoys. Click on a buoy to select it and trigger the data retrieval and plotting process."
        )
        map_event = build_map(buoy_df)
        print(map_event.items())

        # Get selection object (try attribute access first, fallback to dict)
        selection = getattr(map_event, "selection", None)
        objects = getattr(selection, "objects", None) 
        buoy_objects = objects.get("buoys") if objects else None
        print("Buoy objects from map selection event:", buoy_objects)  # Debug print to check the structure of buoy_objects
        buoy_ids = [obj.get("station_id") for obj in buoy_objects] if buoy_objects else None
        buoy_name = [obj.get("name") for obj in buoy_objects] if buoy_objects else None
        print("Selected buoy ids:", buoy_ids if buoy_ids else "No buoy objects found")  # Debug print to check station_id values

    with res_col2:
        st.subheader("Directional Spectrum Plot")
        st.write(f"Station {buoy_name[0] if buoy_name else 'Unknown'}")
        st.success(f"Requested time in UTC: {requested_time_utc}")
        spec, info = open_directional_dataset(
            station_id=buoy_ids[0] if buoy_ids else "44011",  # Use the first selected buoy id or default to "44011"
            requested_time_utc=requested_time_utc,
            directional=True,
            dd=10.0,
            tolerance="1h",
        )
        fig = plot_directional_spectrum(spec, True)
        st.pyplot(fig, clear_figure=True)


    with diag_col1:
        st.subheader("Available Buoys")
        st.table(buoy_df[["station_id", "name"]])
        st.info(f"Data retrieval info: {info}")

    with diag_col2:
        st.write(
            "If there were any issues with data retrieval (e.g., OPeNDAP timeouts), the app will display "
            "error messages here. Otherwise, it will confirm that the data was successfully retrieved and processed."
        )    


if __name__ == "__main__":
    main()