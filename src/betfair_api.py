from dotenv import load_dotenv
import urllib.error, urllib.request
import betfairlightweight
from betfairlightweight import filters
import pandas as pd
import numpy as np
import os
import datetime
import json

class Betfair:

    def __init__(self):
        self.login()

    def login(self):
        with open('../credentials.json') as f:
            cred = json.load(f)
        self.trading = betfairlightweight.APIClient(username=cred['username'],
                                               password=cred['password'],
                                               app_key=cred['app_key'])
        self.trading.login_interactive()

    def get_event_type_id(self, sport):
        sport_filter = betfairlightweight.filters.market_filter(text_query=sport)
        sport_event_type = self.trading.betting.list_event_types(filter=sport_filter)
        self.event_type_id = sport_event_type[0].event_type.id

    def get_event_id(self, datetime_p, event_name):
        event_filter = betfairlightweight.filters.market_filter(
            event_type_ids=[self.event_type_id],
            market_start_time={
                'to': datetime_p
            })

        events = self.trading.betting.list_events(
            filter=event_filter
        )

        events_df = pd.DataFrame({
        'Event Name': [event_object.event.name for event_object in events],
        'Event ID': [event_object.event.id for event_object in events],
        'Open Date': [event_object.event.open_date for event_object in events]
        })

        self.event_id = events_df.loc[events_df["Event Name"].str.contains(event_name), "Event ID"].values[0]
        self.startdate = events_df.loc[events_df["Event Name"].str.contains(event_name), "Open Date"].values[0]

    def get_market_id(self, market_name):
        market_catalogue_filter = betfairlightweight.filters.market_filter(event_ids=[self.event_id])

        market_catalogues = self.trading.betting.list_market_catalogue(
            filter=market_catalogue_filter,
            max_results='10',
            sort='FIRST_TO_START'
        )

        # Create a DataFrame for each market catalogue
        markets_df = pd.DataFrame({
            'Market Name': [market_cat_object.market_name for market_cat_object in market_catalogues],
            'Market ID': [market_cat_object.market_id for market_cat_object in market_catalogues],
            'Total Matched': [market_cat_object.total_matched for market_cat_object in market_catalogues],
        })

        self.market_id = markets_df.loc[markets_df["Market Name"].str.contains(market_name), "Market ID"].values[0]
        print(self.market_id)

    def process_runner_books(self, runner_books):
        best_back_prices = [runner_book.ex.available_to_back[0]['price']
                            if runner_book.ex.available_to_back
                            else 1000
                            for runner_book
                            in runner_books]

        selection_ids = [runner_book.selection_id for runner_book in runner_books]
        statuses = [runner_book.status for runner_book in runner_books]

        df = pd.DataFrame({
            'Selection ID': selection_ids,
            'Best Back Price': best_back_prices,
            'Status': statuses
        })
        return df

    def get_runners_and_prices(self):
        price_filter = betfairlightweight.filters.price_projection(
            price_data=['EX_BEST_OFFERS']
        )

        # Request market books
        market_books = self.trading.betting.list_market_book(
            market_ids=[self.market_id],
            price_projection=price_filter
        )

        # Grab the first market book from the returned list as we only requested one market
        market_book = market_books[0]

        runners_df = self.process_runner_books(market_book.runners)

        print(runners_df)

    def callAping(self, jsonrpc_req):
        url = "https://api.betfair.com/exchange/betting/json-rpc/v1"
        load_dotenv(dotenv_path="../.env")
        headers = {'X-Application': os.getenv('API_KEY'), 'X-Authentication': os.getenv('SSOID'), 'content-type': 'application/json'}
        try:
            req = urllib.request.Request(url, jsonrpc_req.encode('utf-8'), headers)
            response = urllib.request.urlopen(req)
            jsonResponse = response.read()
            return jsonResponse.decode('utf-8')
        except urllib.error.URLError as e:
            print(e.reason)
            print('Oops no service available at ' + str(url))
            exit()

    def get_runner_names(self):
        '''Betfair light version doesnt have runner names so we neeed to make full call from raw API and join to runner df'''
        now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        market_catalogue_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue", "params": {"filter":{"eventIds":["' + self.event_id + '"],' \
                                                                                                                                                             '"marketStartTime":{"from":"' + now + '"}},"sort":"FIRST_TO_START","maxResults":"10","marketProjection":["RUNNER_DESCRIPTION"]}}'
        '''Line above has 2 lines so dont break.'''
        market_catalogue_response = self.callAping(market_catalogue_req)
        market_catalouge_loads = json.loads(market_catalogue_response)
        market_catalouge_results = market_catalouge_loads['result']
        runners_list = market_catalouge_results[0]['runners']
        print(runners_list)
        df = pd.DataFrame(runners_list, columns=['selectionId', 'runnerName'])
        print(df)

if __name__ == '__main__':
    betfair = Betfair()
    betfair.get_event_type_id("Golf")
    datetime_in_a_week = (datetime.datetime.utcnow() + datetime.timedelta(weeks=2)).strftime("%Y-%m-%dT%TZ")
    betfair.get_event_id(datetime_in_a_week, "Open Championship 2024")
    betfair.get_market_id("Winner")
    # betfair.get_runners_and_prices()
    betfair.get_runner_names()


