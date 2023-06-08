from datetime import datetime, timedelta
from herbie import Herbie, Herbie_latest, FastHerbie

# https://mesowest.utah.edu/html/hrrr/zarr_documentation/html/zarr_variables.html


def get_latest_hrrr_time():
    current_time = datetime.utcnow()

    if current_time.hour < 6:
        forecast_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    elif current_time.hour < 12:
        forecast_time = current_time.replace(hour=6, minute=0, second=0, microsecond=0)
    elif current_time.hour < 18:
        forecast_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)
    else:
        forecast_time = current_time.replace(hour=18, minute=0, second=0, microsecond=0)

    return forecast_time.strftime('%Y-%m-%d %H:%M:%S')

H = Herbie(get_latest_hrrr_time())
near_surface_smoke_data = H.xarray('MASSDEN')
near_surface_smoke_data = near_surface_smoke_data.mdens.to_pandas()
near_surface_smoke_data.to_parquet('weather_data/hrrr/near_surface_smoke.parquet')