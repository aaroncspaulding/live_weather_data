# https://mesowest.utah.edu/html/hrrr/zarr_documentation/html/zarr_variables.html

import json
import os
from datetime import datetime, timedelta

import contourpy
import numpy as np
from scipy.ndimage import gaussian_filter
from herbie import Herbie
from simplification.cutil import simplify_coords_vw_idx

from weather_access_code import contours_to_json
from weather_access_code import get_latest_hrrr_time

base_path = os.getcwd()
weather_base_path = os.path.join(os.path.join(base_path, 'weather_data'), 'hrrr')
current_time = datetime.utcnow()

hrrr_time_buffer = timedelta(hours=1, minutes=30)
latest_hrrr_time = get_latest_hrrr_time(current_time, hrrr_time_buffer)

status_file_path = os.path.join(base_path, 'status.json')
if os.path.exists(status_file_path):
    with open(status_file_path, 'r') as file:
        status = json.load(file)
else:
    status = {
        'hrrr_last_updated_time_utc': None,
        'hrrr_valid_time_utc': None,
    }

hrrr_variables = {':MASSDEN:': ('mdens',
                                'near_surface_smoke',
                                1e-9,
                                np.array([0, 1, 2, 4, 6, 8, 12, 16, 20, 25, 30, 40, 60, 100, 200]))}

latitudes, longitudes = None, None
for fxx in range(0, 49):
    H = Herbie(latest_hrrr_time.strftime('%Y-%m-%d %H:%M:%S'),
               model='hrrr',
               product='sfc',
               fxx=fxx)

    if latitudes is None or longitudes is None:
        latitudes = H.xarray('TMP:2 m above')['latitude'].to_pandas()
        longitudes = H.xarray('TMP:2 m above')['longitude'].to_pandas()

    for key in hrrr_variables.keys():
        hrrr_name, description, scaling_factor, levels = hrrr_variables.get(key)

        filename = f'{description}{str(fxx).rjust(3, "0")}.geojson'
        path = os.path.join(weather_base_path, filename)
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

        data_array = H.xarray(key)[hrrr_name].to_pandas()
        data_smooth = gaussian_filter(data_array, sigma := 1)
        data_smooth_clipped = np.clip(data_smooth / scaling_factor, levels[0], levels[-1])

        longitudes_padded = np.pad(longitudes, 1, mode='edge')
        latitudes_padded = np.pad(latitudes, 1, mode='edge')
        all_contours, all_levels = [], []
        for level in levels[1:]:
            data_smooth_clipped_padded = np.pad(data_smooth_clipped, 1, mode='constant', constant_values=level)
            contour_generator = contourpy.contour_generator(longitudes_padded, latitudes_padded,
                                                            data_smooth_clipped_padded)
            contours = contour_generator.lines(level)

            simplified_contours = []
            for polygon in contours:
                indices = list(simplify_coords_vw_idx(polygon, epsilon=0.01))
                indices.append(indices[0])
                simplified_contours.append(polygon[indices])
            all_contours.extend(simplified_contours)
            all_levels.extend([level for _ in range(len(contours))])

        geojson = contours_to_json(all_contours, all_levels)

        with open(path, 'w') as f:
            json.dump(geojson, f)

status['hrrr_last_updated_time_utc'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
status['hrrr_valid_time_utc'] = latest_hrrr_time.strftime('%Y-%m-%d %H:%M:%S')

# Write out status
with open(status_file_path, 'w') as file:
    json.dump(status, file, indent=4)
