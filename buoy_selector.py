import pandas as pd
import pydeck as pdk
from typing import Any, Optional
import streamlit as st

def build_map(df: pd.DataFrame):
    layer = pdk.Layer(
        "ScatterplotLayer",  # Use scatter plot visualization
        data=df,  # Data source (DataFrame with buoy locations)
        id="buoys",  # Layer identifier for selection/interaction
        get_position="[longitude, latitude]",  # Map coordinates from DataFrame columns
        get_radius=70000,  # Base radius of each point in meters
        pickable=True,  # Enable mouse interaction/selection
        auto_highlight=True,  # Highlight point on hover
        stroked=True,  # Draw border/outline on points
        filled=True,  # Fill points with color
        radius_min_pixels=8,  # Minimum point size in pixels when zoomed out
        radius_max_pixels=18,  # Maximum point size in pixels when zoomed in
        get_fill_color=[25, 118, 210, 180],  # RGBA color: blue with transparency
        get_line_color=[0, 0, 0, 255],  # RGBA color: black outline
        line_width_min_pixels=1,  # Outline thickness in pixels
    )

    deck = pdk.Deck(
        map_style=None,  # Map style: None, "light", "dark", "satellite", "street"
        initial_view_state=pdk.ViewState(  # Set initial map camera position
            latitude=31.5,  # Center latitude (Gulf of Mexico region)
            longitude=-90.0,  # Center longitude (Gulf of Mexico region)
            zoom=2.2,  # Zoom level (2.2 = wide view of US)
            pitch=0,  # Rotation angle (0 = top-down view)
        ),
        layers=[layer],  # Add the scatter plot layer to the map
        tooltip={"text": "{station_id}\n{region}"},  # Show label and region on hover
    )

    return st.pydeck_chart(  # Display the map in Streamlit
        deck,  # The pydeck Deck object to render
        on_select="rerun",  # Rerun the app when a buoy is selected
        selection_mode="single-object",  # Allow selecting only one buoy at a time
        key="buoy_map",  # Unique identifier for this widget
        height=500,  # Chart height in pixels
    )

def extract_selected_station_id(event: Any) -> Optional[str]:
    # Extract station_id from pydeck map selection event (safely handles different data structures)
    if event is None:
        return None

    # Get selection object (try attribute access first, fallback to dict)
    selection = getattr(event, "selection", None)
    if selection is None and isinstance(event, dict):
        selection = event.get("selection", event)
    if selection is None:
        return None

    # Get objects from selection (try attribute access first, fallback to dict)
    objects = getattr(selection, "objects", None)
    if objects is None and isinstance(selection, dict):
        objects = selection.get("objects")
    if not objects:
        return None

    # Extract buoy layer objects from the selection
    buoy_objects = objects.get("buoys") if isinstance(objects, dict) else None
    if not buoy_objects:
        return None

    # Get the first selected buoy
    first = buoy_objects[0]
    # Return station_id if buoy is a dict, otherwise None
    if isinstance(first, dict):
        return first.get("station_id")
    return None