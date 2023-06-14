from typing import Dict, Any, List, Union

import numpy as np

from datetime import datetime, timedelta


def get_latest_hrrr_time(current_time_: datetime, time_buffer: Union[float, timedelta] = 0.0) -> datetime:
    """
    Given the current time, find the latest High Resolution Rapid Refresh (HRRR) model forecast time.
    HRRR model forecasts are made every 6 hours at 00:00, 06:00, 12:00, and 18:00.

    Parameters:
    current_time_ (datetime): The current time.
    time_buffer (Union[float, timedelta]): The number of minutes to add to the HRRR processing time.
                                           Can be a float (in minutes) or a timedelta object.
                                           Defaults to 0.0.

    Returns:
    forecast_time (datetime): The latest HRRR model forecast time.

    Example usage:
    >>> from datetime import datetime
    >>> current_time__ = datetime.now()
    >>> latest_hrrr_time = get_latest_hrrr_time(current_time__, 30.0)
    """

    # Convert time_buffer to timedelta if it's a float (assumed to be minutes)
    if isinstance(time_buffer, float):
        time_buffer = timedelta(minutes=time_buffer)

    # Adjust the current time by subtracting the time buffer
    adjusted_time = current_time_ - time_buffer

    # Determine the latest HRRR forecast time based on the adjusted time
    if adjusted_time.hour < 6:
        forecast_time = adjusted_time.replace(hour=0, minute=0, second=0, microsecond=0)
    elif adjusted_time.hour < 12:
        forecast_time = adjusted_time.replace(hour=6, minute=0, second=0, microsecond=0)
    elif adjusted_time.hour < 18:
        forecast_time = adjusted_time.replace(hour=12, minute=0, second=0, microsecond=0)
    else:
        forecast_time = adjusted_time.replace(hour=18, minute=0, second=0, microsecond=0)

    return forecast_time


def contours_to_json(contours: List[np.ndarray], levels: List) -> Dict[str, Any]:
    """
    Convert a list of contour polygons to GeoJSON format.

    Parameters:
    contours (List[np.ndarray]): A list of contour polygons generated from ContourGenerator.
    levels (np.ndarray): The corresponding levels for each contour.

    Returns:
    geojson (dict): A dictionary representing the contour polygons in GeoJSON format.

    Example usage:
    >>> import numpy as np_
    >>> from contourpy import ContourGenerator
    >>> x = np_.linspace(-1, 1, 100)
    >>> y = np_.linspace(-1, 1, 100)
    >>> X, Y = np_.meshgrid(x, y)
    >>> Z = np_.sqrt(X**2 + Y**2)
    >>> generator = ContourGenerator(X, Y, Z)
    >>> contours_ = generator.filled(np_.array([0.5, 0.75]))
    >>> geojson_ = contours_to_json(contours_)
    """
    geojson = {"type": "FeatureCollection", "features": []}

    assert len(contours) == len(levels)

    # Iterate over contour polygons
    for i, contour in enumerate(contours):
        # Close the loop if necessary
        if not np.array_equal(contour[0], contour[-1]):
            contour = np.concatenate([contour, contour[0].reshape(1, -1)])

        geojson["features"].append({
            "type": "Feature",
            "id": str(i),  # Assign a unique id to the feature
            "geometry": {
                "type": "Polygon",
                "coordinates": [contour.tolist()]  # Convert numpy array to list
            },
            "properties": {"level": str(levels[i])}  # Add the corresponding level
        })
    return geojson
