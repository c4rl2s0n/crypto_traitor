from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision

from src.data.models import Price
from src.data.timeseries import InfluxDB


class TimeSeriesRepository(object):

    def __init__(self, db: InfluxDB):
        self.db = db

    def add_price(self, price: Price):
        point = (
            Point("coin_price")
            .tag("coin", price.coin_id)
            .tag("symbol", price.coin_symbol)
            .field("value", price.value)
            .time(price.time, WritePrecision.MS)
        )

        self.db.write_api.write(bucket="prices", org=self.db.org, record=point)
