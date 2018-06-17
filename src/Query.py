import pandas as pd
import numpy as np
import Station
import helper

class Query():
    def __init__(self, sde_client, mdc_client, items, stations, date):
        self.sde_client = sde_client
        self.mdc_client = mdc_client
        self.items = items
        self.stations = stations
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
        
        # Retrieve the best buy and sell orders for each station
        #  and append them to the master dataframe
        df = self.get_all_sales(df)
        
        # Calculate the internal spread between buys/sells
        #  Internal spread here means the difference between
        #  buys and sells within the system. 
        df = self.get_internal_spread(df)
        
        # Calculate the spread between buying/selling
        #  at each of the individual stations. This will
        #  be a cross-product between all stations listed
        
        return df
    
    
    def get_internal_spread(self, df):
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
        # Loop through all stations in the query
        for key, station in self.stations.items():
            # Quick name variable to save space
            name_string = station.get_station_shorthand()
            # Apply the spread calculation to the buy/sell columns for
            #  each station for each item
            df[f'%s: Internal Spread'%name_string] = \
                df.apply(lambda x: x[f'%s: sells'%name_string] - 
                                        x[f'%s: buys'%name_string], axis=1)
                
        return df
        
        
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

        return buy[0]['price'], sell[0]['price']
    
    
    def get_all_sales(self, df):
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
        for key, station in self.stations.items():
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
    
    def get_master_df(self):
        return self.master_df
    
    def get_stations(self):
        return self.stations