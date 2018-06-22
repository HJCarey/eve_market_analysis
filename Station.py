import pandas as pd

class Station:
    """
    Holds information about each station, including
    official name, shorthand name, id, and region id
    """
    def __init__(self, sde_client, station_name):
        self.sde_client = sde_client
        self.station_name = station_name
        self.station_name_shorthand = self.generate_shorthand()
        self.station_id = self.find_station_id()
        self.region_id = self.find_region_id()

    def find_station_id(self):
        return self.sde_client.Station.getStations(
            stationName=f"{{values: ['%s']}}"%self.station_name).result()[0]['stationID']
    
    def find_region_id(self):
        return self.sde_client.Station.getStations(
            stationName=f"{{values: ['%s']}}"%self.station_name).result()[0]['regionID']
    
    def generate_shorthand():
        return self.station_name.split()[0]
    
    def get_station_name(self):
        return self.station_name
    
    def get_station_id(self):
        return self.station_id
    
    def get_region_id(self):
        return self.region_id
    
    def get_station_shorthand(self):
        return self.station_name_shorthand