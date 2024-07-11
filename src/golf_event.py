import pandas as pd, random
pd.set_option('display.max_rows', None)

class GetData:

    def __init__(self):
        '''Here I will build Betfair API to pull in data for event and sort by ranking.
        Also get data of players from website.
        For now using CSV of examples.'''
        self.golfers = pd.read_csv("../data/in/golf_players.csv")
        self.entrants = pd.read_csv("../data/in/entrants.csv")

class Golf(GetData):

    def __init__(self):
        GetData.__init__(self)

        '''Other Variables'''
        self.even_draw = True  # Use all players to assign players with uneven players.
        self.fair_draw = False  # Use odds ranking to create fair pots.

    def add_pot(self):
        '''Add Pot number to Player Dataframe based on number entrants'''
        pot = 1
        for i in range(len(self.entrants), len(self.golfers), len(self.entrants)):
            self.golfers.loc[i - len(self.entrants):i-1, ["Pot"]] = pot
            pot+=1
        if self.even_draw == True:
            self.golfers.dropna(inplace=True)
        if self.even_draw == False:
            modulo = len(self.golfers) % len(self.entrants)
            if modulo > 0:
                last_rank = self.golfers['Rank'].iloc[-1]
                add_rows = pd.DataFrame([{"Players":"None Asigned", "Rank":last_rank+i, "Pot":None} for i in range(1, len(self.entrants)+1-modulo)])
                self.golfers = pd.concat([self.golfers, add_rows], ignore_index=True)
            self.golfers.loc[self.golfers["Pot"].isna(), "Pot"] = pot
        self.golfers["Pot"] = self.golfers["Pot"].astype(int)

    def run_draw(self):

        if self.fair_draw == False:
            rank_range = self.golfers.loc[:, "Rank"].tolist()
        for pot in self.golfers["Pot"].unique():
            print(f"Drawing Pot {pot}")
            self.entrants[f"Pot_{pot}"] = ""  # Create empty pot col to store player name.
            if self.fair_draw == True:
                rank_range = self.golfers.loc[self.golfers["Pot"] == pot, "Rank"].tolist()
            # print(rank_range)
            for i in self.entrants.index:
                random_index = random.randrange(0, len(rank_range), 1)
                player_drawn = self.golfers.loc[self.golfers["Rank"] == rank_range[random_index], "Players"].values[0]
                print(f"{player_drawn}")
                self.entrants.loc[i, f"Pot_{pot}"] = player_drawn
                rank_range.pop(random_index)

        self.entrants.to_csv("../data/out/draw_output.csv", index=False)

if __name__ == '__main__':
    golf = Golf()
    golf.add_pot()
    golf.run_draw()
