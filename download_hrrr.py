# https://mesowest.utah.edu/html/hrrr/zarr_documentation/html/zarr_variables.html

import os
import json
from datetime import datetime, timedelta
from herbie import Herbie

base_path = os.getcwd()
weather_base_path = os.path.join(os.path.join(base_path, 'weather_data'), 'hrrr')
current_time = datetime.utcnow()

hrrr_time_buffer = timedelta(hours=1, minutes=30)

status_file_path = os.path.join(base_path, 'status.json')
if os.path.exists(status_file_path):
    with open(status_file_path, 'r') as file:
        status = json.load(file)
else:
    status = {
        'hrrr_last_updated_time_utc': None,
        'hrrr_valid_time_utc': None,
    }


def get_latest_hrrr_time(current_time_):
    if current_time_.hour < 6:
        forecast_time = current_time_.replace(hour=0, minute=0, second=0, microsecond=0)
    elif current_time_.hour < 12:
        forecast_time = current_time_.replace(hour=6, minute=0, second=0, microsecond=0)
    elif current_time_.hour < 18:
        forecast_time = current_time_.replace(hour=12, minute=0, second=0, microsecond=0)
    else:
        forecast_time = current_time_.replace(hour=18, minute=0, second=0, microsecond=0)
    return forecast_time


hrrr_variables = {'MASSDEN': 'near_surface_smoke'}
latest_hrrr_time = get_latest_hrrr_time(current_time - hrrr_time_buffer)
for fxx in range(0, 49):
    H = Herbie(latest_hrrr_time.strftime('%Y-%m-%d %H:%M:%S'),
               model='hrrr',
               product='sfc',
               fxx=fxx)

    for grib_name in hrrr_variables.keys():
        path = f'{hrrr_variables.get(grib_name)}{str(fxx).rjust(3, "0")}.parquet'
        try:
            # TODO: Fix this to make it work on any type of field
            near_surface_smoke_data = H.xarray('MASSDEN')
            near_surface_smoke_data = near_surface_smoke_data.mdens.to_pandas()
            near_surface_smoke_data.to_parquet(os.path.join(weather_base_path, path))
        except ValueError:
            # Then we couldn't find the data
            try:
                os.remove(path)
            except FileNotFoundError:
                pass

status['hrrr_last_updated_time_utc'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
status['hrrr_valid_time_utc'] = latest_hrrr_time.strftime('%Y-%m-%d %H:%M:%S')

# Write out status
with open(status_file_path, 'w') as file:
    json.dump(status, file, indent=4)
