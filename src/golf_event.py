import pandas as pd, random, datetime
from betfair_api import Betfair
pd.set_option('display.max_rows', None)

class GetData:

    def __init__(self):
        '''Test Data before website and Betfair provides this data.'''
        # self.runners = pd.read_csv("../data/in/golf_players.csv")
        self.entrants = pd.read_csv("../data/in/entrants.csv")

    def create_betfair_object(self):
        self.betfair = Betfair()

class Golf(GetData):

    def __init__(self, even_draw, fair_draw):
        GetData.__init__(self)
        GetData.create_betfair_object(self)

        '''Other Variables'''
        self.even_draw = even_draw  # Use all players to assign players with uneven players.
        self.fair_draw = fair_draw  # Use odds ranking to create fair pots.

    def list_all_events_found(self, datetime_p):
        self.betfair.list_all_events_found(datetime_p)

    def get_runner_data(self, event_name, datetime_p):
        self.runners = self.betfair.get_runners_df("Golf", event_name, datetime_p)

    def add_pot(self):
        '''Add Pot number to Player Dataframe based on number entrants'''
        pot = 1
        for i in range(len(self.entrants), len(self.runners), len(self.entrants)):
            print(i)
            print(len(self.entrants))
            self.runners.loc[i - len(self.entrants):i-1, ["Pot"]] = pot
            pot+=1
        if self.even_draw == True:
            self.runners.dropna(inplace=True)
        if self.even_draw == False:
            modulo = len(self.runners) % len(self.entrants)
            if modulo > 0:
                last_rank = self.runners['Rank'].iloc[-1]
                add_rows = pd.DataFrame([{"runnerName":"None Asigned", "Rank":last_rank+i, "Pot":None} for i in range(1, len(self.entrants)+1-modulo)])
                self.runners = pd.concat([self.runners, add_rows], ignore_index=True)
            self.runners.loc[self.runners["Pot"].isna(), "Pot"] = pot
        self.runners["Pot"] = self.runners["Pot"].astype(int)
        print(self.runners)

    def run_draw(self):
        self.add_pot()
        if self.fair_draw == False:
            rank_range = self.runners.loc[:, "Rank"].tolist()
        for pot in self.runners["Pot"].unique():
            print(f"Drawing Pot {pot}")
            self.entrants[f"Pot_{pot}"] = ""  # Create empty pot col to store player name.
            if self.fair_draw == True:
                rank_range = self.runners.loc[self.runners["Pot"] == pot, "Rank"].tolist()
            print(rank_range)
            for i in self.entrants.index:
                random_index = random.randrange(0, len(rank_range), 1)
                player_drawn = self.runners.loc[self.runners["Rank"] == rank_range[random_index], "runnerName"].values[0]
                print(f"{player_drawn}")
                self.entrants.loc[i, f"Pot_{pot}"] = player_drawn
                rank_range.pop(random_index)

        self.entrants.to_csv("../data/out/draw_output.csv", index=False)

if __name__ == '__main__':
    golf = Golf(even_draw=True, fair_draw=True)

    '''datetime variable for length time to check.'''
    datetime_in_a_week = (datetime.datetime.utcnow() + datetime.timedelta(weeks=2)).strftime("%Y-%m-%dT%TZ")

    '''Use this to get event name for event'''
    # golf.list_all_events_found(datetime_in_a_week)

    golf.get_runner_data("Open Championship 2024", datetime_in_a_week)
    golf.run_draw()
