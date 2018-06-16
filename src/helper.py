import pandas as pd
import numpy as np
import datetime
from bravado.client import SwaggerClient
from bravado.exception import HTTPError

def get_type_id(sde_client, item):
    return sde_client.Inventory.getTypes(typeName=f"{{values: ['%s']}}"%item).result()[0]['typeID']


def get_type_id_list(sde_client, items):
    items_list = [get_type_id(sde_client, x) for x in items]
    return pd.Series(items_list)


def get_stations_region_id(sde_client, item):
    return sde_client.Station.getStations(stationName=f"{{values: ['%s']}}"%item).result()[0]['regionID']


def get_region_id(sde_client, region):
    return sde_client.Map.getRegions(regionName=f"{{values: ['%s']}}"%region).result()[0]['regionID']


def get_station_id(sde_client, station):
    return sde_client.Station.getStations(stationName=f"{{values: ['%s']}}"%station).result()[0]['stationID']


def get_item_history(mdc_client, type_id, region_id, lookback_date):
    date_range = pd.date_range(datetime.date.today() - datetime.timedelta(days=lookback_date), datetime.date.today())
    market_history = []
    for next in date_range:
        try:
            print(".", end="")
            next_data = mdc_client.MarketData.history(typeID=type_id, regionID=region_id, date=str(next)).result()
            market_history.append(next_data)
        except HTTPError:
            pass
        
    return market_history


def get_item_book(mdc_client, type_id, station_id, region_id, date):
    # Get the item data from the 
    book =  mdc_client.MarketData.book(typeID=type_id, regionID=region_id, date=str(date)).result()
    
    df_book = pd.DataFrame(book)
    
    # Order are ordered with buys first, descending in price, followed by sells in ascending price
    buy = [x for x in book['orders'] if x['buy'] and x['locationID'] == station_id]
    sell = [x for x in book['orders'] if not x['buy'] and x['locationID'] == station_id]
    
    spread = compute_spread(buy, sell)
    
    return spread, buy[0]['price'], sell[0]['price']



# Compute the spread between the buy and sell orders
def compute_spread(buy, sell):
    if len(buy) == 0 or len(sell) == 0:
        return None
    return sell[0]['price'] - buy[0]['price']