import pandas as pd

class Station:
    def __init__(self, sde_client, station_name, station_name_shorthand):
        self.sde_client = sde_client
        self.station_name = station_name
        self.station_name_shorthand = station_name_shorthand
        self.station_id = self.find_station_id()
        self.region_id = self.find_region_id()

    def find_station_id(self):
        return self.sde_client.Station.getStations(
            stationName=f"{{values: ['%s']}}"%self.station_name).result()[0]['stationID']
    
    def find_region_id(self):
        return self.sde_client.Station.getStations(
            stationName=f"{{values: ['%s']}}"%self.station_name).result()[0]['regionID']
    
    def get_station_name(self):
        return self.station_name
    
    def get_station_id(self):
        return self.station_id
    
    def get_region_id(self):
        return self.region_id
    
    def get_station_shorthand(self):
        return self.station_name_shorthand