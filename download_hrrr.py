# https://mesowest.utah.edu/html/hrrr/zarr_documentation/html/zarr_variables.html

import os
import json
from datetime import datetime, timedelta
from herbie import Herbie

base_path = os.getcwd()
weather_base_path = os.path.join(os.path.join(base_path, 'weather_data'), 'hrrr')
current_time = datetime.utcnow()

hrrr_timebuffer = timedelta(hours=1, minutes=30)

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


# Update HRRR Data
latest_hrrr_time = get_latest_hrrr_time(current_time - hrrr_timebuffer)
H = Herbie(latest_hrrr_time.strftime('%Y-%m-%d %H:%M:%S'))
near_surface_smoke_data = H.xarray('MASSDEN')
near_surface_smoke_data = near_surface_smoke_data.mdens.to_pandas()

status['hrrr_last_updated_time_utc'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
status['hrrr_valid_time_utc'] = latest_hrrr_time.strftime('%Y-%m-%d %H:%M:%S')

near_surface_smoke_data.to_parquet(os.path.join(weather_base_path, 'near_surface_smoke.parquet'))

# Write out status
with open(status_file_path, 'w') as file:
    json.dump(status, file, indent=4)
