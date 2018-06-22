import pandas as pd
import numpy as np
import Station
import helper
import itertools
from IPython.display import display

class Query():
    def __init__(self, sde_client, mdc_client, master_station, stations, items, date):
        self.sde_client = sde_client
        self.mdc_client = mdc_client
        self.items = items
        self.master_station = master_station
        self.stations_dict = stations.copy()
        self.date = date
        # Create master dataframe
        self.master_df = self.construct_master_df()
        
    def construct_master_df(self):
        """
        Create the master dataframe with the key being the item
        of interest.
        """
        # Create the initial dataframe with the items column
        df = pd.DataFrame(list(self.items.keys()))
        df.columns = ['Items']
        
        # Add item types
        #df = self.add_item_types(df)
        
        # Retrieve the best buy and sell orders for each station
        #  and append them to the master dataframe
        df = self.add_all_sales(df)
        
        # After all sales data is added, remove the master station
        #  from the station list.
        self.stations_dict.pop(self.master_station.get_station_name(), None)
        
        # Calculate the internal spread between buys/sells
        #  Internal spread here means the difference between
        #  buys and sells within the system. 
        df = self.add_internal_spread(df)
        
        # Calculate the spread between buying/selling
        #  at each of the individual stations. This will
        #  be a cross-product between all stations listed
        df = self.add_external_spread(df)
        
        # Grab the region averages for all stations listed
        
        return df
    
    
    #def add_item_types(self, df):
        
    

    def add_all_sales(self, df):
        """
        Returns a dataframe with the best buy/sell orders for all items
        in the requested stations.
        Args:
            df: The incoming dataframe with the 'Items' column populated
        Returns:
            df: The dataframe with buy/sell prices for all given stations
        """
        
        # Loop through each station and find the best buy and sell price
        #  for each requested item in that station.
        # The loop here essentially appends a Pandas Series to the 
        #  df arg.
        for key, station in self.stations_dict.items():
            test_series = df.apply(lambda row:
                                self.get_station_sales(self.items[row['Items']],
                                                    station.get_station_id(),
                                                    station.get_region_id()), axis=1)
            # Format the column names
            buy_name = f"%s: buys"%station.get_station_shorthand()
            sell_name = f"%s: sells"%station.get_station_shorthand()
            # Create the new buy/sell columns
            df[[buy_name,sell_name]] = pd.DataFrame(test_series.values.tolist(), 
                                index=df.index)

        return df
    
    """
    def add_internal_spread(self, df):
        
        Calculates the internal spread between buys and sells in
        the same system. For instance, if you were to put a buy order
        for an item, then a sell order for that same item in the same
        system.
        Args:
            df: Incoming dataframe with items and station buys/sells
        Returns:
            dataframe: The same dataframe as input, but with the
                       internal spread columns added
        
        # Loop through all stations in the query
        for key, station in self.stations.items():
            # Quick name variable to save space
            name_string = station.get_station_shorthand()
            # Apply the spread calculation to the buy/sell columns for
            #  each station for each item
            df[f'%s: Internal Spread'%name_string] = \
                df.apply(lambda x: self.calculate_spread(x[f'%s: buys'%name_string], \
                                                    x[f'%s: sells'%name_string]), axis=1)
                
            #np.nansum([x[f'%s: sells'%name_string], -x[f'%s: buys'%name_string]])
                
        return df
    """
    
    def add_internal_spread(self, df):
        """
        Calculates the internal spread between buys and sells in
        the same system. For instance, if you were to put a buy order
        for an item, then a sell order for that same item in the same
        system.
        Args:
            df: Incoming dataframe with items and station buys/sells
        Returns:
            dataframe: The same dataframe as input, but with the
                       internal spread columns added
        """
        # Add internal spread for the master station of the query
        name_string = self.master_station.get_station_shorthand()

        df[f'%s: Internal Spread'%name_string] = \
            df.apply(lambda x: self.calculate_spread(\
            x[f'%s: buys'%name_string], \
            x[f'%s: sells'%name_string]), axis=1)
        
        return df
    
    
    def add_external_spread(self, df):
        """
        Calculates the spread between selling/buying at the master station
        vs all other stations in the query list.
        """
        # Loop through all stations in the station listing
        for key, station in self.stations_dict.items():
            df[f'%s: Buy, %s: Sell'%(self.master_station.get_station_shorthand(),
                                     station.get_station_shorthand())] = \
                df.apply(lambda x: self.calculate_spread(\
                x[f'%s: buys'%self.master_station.get_station_shorthand()], \
                x[f'%s: sells'%station.get_station_shorthand()]), axis=1)
                
            df[f'%s: Buy, %s: Sell'%(station.get_station_shorthand(),
                                     self.master_station.get_station_shorthand())] = \
                df.apply(lambda x: self.calculate_spread(\
                x[f'%s: buys'%station.get_station_shorthand()], \
                x[f'%s: sells'%self.master_station.get_station_shorthand()]), axis=1)
        
        return df
    
    """
    def add_external_spread(self, df):
        stations_combos = [item for item in itertools.combinations(self.stations.keys(), r=2)]
        
        for stations in stations_combos:
            
            station_a = self.stations[stations[0]]
            station_b = self.stations[stations[1]]
            
            df[f'%s: Buy, %s: Sell'%(station_a.get_station_shorthand(), station_b.get_station_shorthand())]  \
                = df.apply(lambda x: self.calculate_spread(x[f'%s: buys'%station_a.get_station_shorthand()],
                    x[f'%s: sells'%station_b.get_station_shorthand()]), axis=1)
        
            df[f'%s: Buy, %s: Sell'%(station_b.get_station_shorthand(), station_a.get_station_shorthand())]  \
                = df.apply(lambda x: self.calculate_spread(x[f'%s: buys'%station_b.get_station_shorthand()],
                    x[f'%s: sells'%station_a.get_station_shorthand()]), axis=1)
        return df
    """
        
        
    def get_station_sales(self, type_id, station_id, region_id):
        """
        Return the best buy and sell order price for the given item
        in the given system.
        Args:
            type_id: ID of the item being queried
            station_id: ID of the station being queried
            region_id: ID of the region the station is in
            
        Returns:
            list: [best buy price, best sell price]
        """
        # Get the item data from the Orbital Enterprises client
        book =  self.mdc_client.MarketData.book(typeID=type_id, regionID=region_id, date=str(self.date)).result()

        # df_book = pd.DataFrame(book)

        # Order are ordered with buys first, descending in price, followed by sells in ascending price
        buy = [x for x in book['orders'] if x['buy'] and x['locationID'] == station_id]
        sell = [x for x in book['orders'] if not x['buy'] and x['locationID'] == station_id]
        
        try:
            buys = buy[0]['price']
        except:
            buys = np.nan
        try:
            sells = sell[0]['price']
        except:
            sells = np.nan
            
        return buys, sells
    
    
    def calculate_spread(self, buy, sell):
        profit = sell-buy
        percentage = 100*(profit/sell)
        diff = [profit, percentage]
        
        return diff
    
    def get_master_df(self):
        return self.master_df
    
    def get_master_station(self):
        return self.master_station
    
    def get_stations(self):
        return self.stations_dict
    