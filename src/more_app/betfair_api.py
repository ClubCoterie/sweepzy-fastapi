from dotenv import load_dotenv
import urllib.error, urllib.request
import betfairlightweight
import pandas as pd
import os
import datetime
import json
pd.set_option('display.max_rows', None)

class Betfair:

    def __init__(self, sport):
        self.login()
        self.event_type_id = self.get_event_type_id(sport)

        '''For now only ever looking at winner market book so can pre define it.'''
        self.market_name = "Winner"

        '''This gets all events on betfair within n weeks which is more than enough time before they get listed.'''
        self.datetime_p = (datetime.datetime.utcnow() + datetime.timedelta(weeks=6)).strftime("%Y-%m-%dT%TZ")

    def login(self):
        with open('../../credentials.json') as f:
            cred = json.load(f)
        self.trading = betfairlightweight.APIClient(username=cred['username'],
                                               password=cred['password'],
                                               app_key=cred['app_key'])
        self.trading.login_interactive()

    def get_event_type_id(self, sport):
        sport_filter = betfairlightweight.filters.market_filter(text_query=sport)
        sport_event_type = self.trading.betting.list_event_types(filter=sport_filter)
        event_type_id = sport_event_type[0].event_type.id
        return event_type_id

    def assign_event_id(self, event_id):
        self.event_id = str(event_id)

    def list_all_events_found(self):
        event_filter = betfairlightweight.filters.market_filter(
            event_type_ids=[self.event_type_id],
            market_start_time={
                'to': self.datetime_p
            })

        events = self.trading.betting.list_events(
            filter=event_filter
        )

        events_df = pd.DataFrame({
            'Event Name': [event_object.event.name for event_object in events],
            'Event ID': [event_object.event.id for event_object in events],
            'Open Date': [event_object.event.open_date for event_object in events]
        })
        print(events_df)

    def find_event_id_by_event_name(self, event_name):
        event_filter = betfairlightweight.filters.market_filter(
            event_type_ids=[self.event_type_id],
            market_start_time={
                'to': self.datetime_p
            })

        events = self.trading.betting.list_events(
            filter=event_filter
        )

        events_df = pd.DataFrame({
        'Event Name': [event_object.event.name for event_object in events],
        'Event ID': [event_object.event.id for event_object in events],
        'Open Date': [event_object.event.open_date for event_object in events]
        })

        event_id = events_df.loc[events_df["Event Name"].str.contains(event_name), "Event ID"].values[0]
        print(event_id)

    def get_market_id(self):
        try:
            if self.event_id is not None:
                print("Event ID Assigned to object.")
        except AttributeError:
            print("You must use assign_event_id function to object first. \n"
                  "You can also call list_all_events_found or find_event_id_by_event_name to help find the event_id")

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

        market_id = markets_df.loc[markets_df["Market Name"].str.contains(self.market_name), "Market ID"].values[0]

        return market_id

    def process_runner_books(self, runner_books):
        best_back_prices = [runner_book.ex.available_to_back[0]['price']
                            if runner_book.ex.available_to_back
                            else 1000
                            for runner_book
                            in runner_books]

        selection_ids = [runner_book.selection_id for runner_book in runner_books]
        statuses = [runner_book.status for runner_book in runner_books]

        df = pd.DataFrame({
            'selectionId': selection_ids,
            'Best_Back_Price': best_back_prices,
            'Status': statuses
        })
        return df

    def get_runners_and_prices(self):
        price_filter = betfairlightweight.filters.price_projection(price_data=['EX_BEST_OFFERS'])

        # Request market books
        market_books = self.trading.betting.list_market_book(
            market_ids=[self.market_id],
            price_projection=price_filter
        )

        # Grab the first market book from the returned list as we only requested one market
        market_book = market_books[0]

        runners_df = self.process_runner_books(market_book.runners)

        return runners_df.loc[runners_df["Status"]=="ACTIVE", ["selectionId", "Best_Back_Price"]]

    def callAping(self, jsonrpc_req):
        url = "https://api.betfair.com/exchange/betting/json-rpc/v1"
        load_dotenv(dotenv_path="../../.env")
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
        '''Betfair light version doesnt have runner names so we neeed to make full call from raw API
        and join to runner df'''
        now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        market_catalogue_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue", "params": {"filter":{"eventIds":["' + self.event_id + '"],' \
                                                                                                                                                             '"marketStartTime":{"from":"' + now + '"}},"sort":"FIRST_TO_START","maxResults":"10","marketProjection":["RUNNER_DESCRIPTION"]}}'
        '''Line above has 2 lines so don't break.
        
        Using event_id and now datetime to show markets now available '''
        market_catalogue_response = self.callAping(market_catalogue_req)
        market_catalouge_loads = json.loads(market_catalogue_response)
        print(market_catalouge_loads)
        runners_list = market_catalouge_loads['result'][0]['runners']
        df = pd.DataFrame(runners_list, columns=['selectionId', 'runnerName'])

        return df

    def get_runners_df(self):
        self.market_id = self.get_market_id()
        df = self.get_runners_and_prices()
        df2 = self.get_runner_names()
        df_out = df.merge(df2, on="selectionId", how="left")
        df_out["Rank"] = df_out["Best_Back_Price"].rank(method="first").astype(int)
        df_out = df_out.loc[:, ["runnerName", "Rank"]].sort_values(by="Rank").reset_index(drop=True)
        # print(df_out)
        return df_out

if __name__ == '__main__':

    b = Betfair("golf")
    # b.list_all_events_found()
    b.assign_event_id(33236231)
    df = b.get_runners_df()
    print(df)



