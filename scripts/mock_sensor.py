import numpy as np

from time import sleep
from typing import Optional

from timestore import timeseries, SQLTypes, _TABLE_NAME
from timestore.sql import insert, create, exists


@timeseries
class SensorData():
    value: SQLTypes.DOUBLE_PRECISION
    location: Optional[SQLTypes.TEXT]
    metadata: SQLTypes.JSONB


if __name__ == "__main__":
    if not exists(SensorData):
        create(SensorData)

    print(f"""
    Adding random mock sensor values to the database.
    To get the data for the last 5 minutes, run the following SQL query:
    
    SELECT time AS time, value FROM {getattr(SensorData, _TABLE_NAME)} 
                WHERE time > current_timestamp - interval '5' minute;
    
    """)

    while True:
        try:
            data_point = SensorData(value=np.random.rand(), location="Berkeley", metadata={"user": "guen"})
            insert(data_point)
            sleep(1)

        except KeyboardInterrupt:
            break
