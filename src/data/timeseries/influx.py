from influxdb_client import InfluxDBClient


class InfluxDB(object):
    """
    TimeSeries Database to store market values
    """
    def __init__(self, url: str, token: str, org: str):
        self.url = url
        self.token = token
        self.org = org
        self.client = InfluxDBClient(
            url=url,
            token=token,
            org=org
        )
        self.write_api = self.client.write_api()

    def close(self):
        self.client.close()
