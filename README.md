# Timestore

Library for storing time series data in a PostgreSQL database.

Requirements:

* Docker (for developing)
* PostgreSQL
* TimescaleDB (if not using Docker)

Optional (if not using Docker):

* PGWeb
* Grafana

## Installation

Clone the git repo, `cd` into the root folder and run `pip install -e .`.


## Usage example

To set up a development environment using `docker`, run:
```
# Start a postgres database with timescaledb extension
docker run --rm -d --name timescaledb -e POSTGRES_PASSWORD=ts -p 5432:5432 timescale/timescaledb

# Start a PGWeb instance
docker run -d -p 8081:8081 --link timescaledb:db -e DATABASE_URL="postgres://postgres:ts@db:5432/postgres?sslmode=disable" sosedoff/pgweb

# Start a Grafana instance
docker run -d -p 3000:3000 --link timescaledb:db grafana/grafana
```

To create a new time series table, just create a dataclass-style using the `timeseries` decorator and run `create`.
```
import numpy as np
from typing import Optional

from timestore import timeseries, SQLTypes, _TABLE_NAME
from timestore.sql import insert, create


@timeseries
class SensorData():
    value: SQLTypes.DOUBLE_PRECISION
    location: Optional[SQLTypes.TEXT]
    metadata: SQLTypes.JSONB

create(SensorData)
```

To insert a datapoint, create an instance of the class and run `insert`:
```
data_point = SensorData(value=np.random.rand(), location="Berkeley", metadata={"user": "guen"})
insert(data_point)
```

To batch insert a list of data points, create a list of instances and use `batch_insert`:
```
data_points = [SensorData(value=val, location="Berkeley", metadata={"user": "guen"}) for val in np.random.rand(1000)]
batch_insert(data_points)
```

To query, run a SQL query, e.g.
```
SELECT time AS time, value FROM sensor_data WHERE time > current_timestamp - interval '5' minute;
```

Or use the `query` function to get a list of dataclass instances back:
```
data = [SensorData(*result) for result in query(SensorData, limit=10)]
```

For an example, see the `scripts` folder.
