import pandas as pd, random, sqlite3, cachetools
from betfair_api import Betfair
pd.set_option('display.max_rows', None)

betfair_cache = cachetools.TTLCache(maxsize=20, ttl=20000)

class Draw:

    def __init__(self, event_id, even_draw=True, fair_draw=True):
        self.even_draw = even_draw
        self.fair_draw = fair_draw
        self.conn = self.get_sql_conn()
        self.cur = self.conn.cursor()
        self.event = self.get_event(event_id)

        '''Will get this from James later..'''
        self.entrants = pd.read_csv("../../data/in/entrants.csv")
        self.runners = self.get_runners()

    def get_sql_conn(self):
        try:
            conn = sqlite3.connect('../../sweepzy.db')
            return conn
        except sqlite3.Error as e:
            print(e)

    def get_event(self, event_id):
        sql_query = f'''SELECT * FROM all_events WHERE id = {event_id}'''
        self.cur.execute(sql_query)
        records = self.cur.fetchone()
        # print(records)
        return records

    def get_runners(self):

        # print(self.event[1])
        if self.event[1] in betfair_cache:
            return betfair_cache[self.event[1]]

        print("Making BF Call...")
        b = Betfair(self.event[4])
        b.assign_event_id(self.event[1])
        df = b.get_runners_df()
        # print(df)
        return df

    def add_pot(self):
        '''Add Pot number to Runners Dataframe based on number entrants'''
        pot = 1
        for i in range(len(self.entrants), len(self.runners), len(self.entrants)):
            # print(i)
            # print(len(self.entrants))
            self.runners.loc[i - len(self.entrants):i-1, ["Pot"]] = pot
            pot+=1
        if self.even_draw == True:
            '''Remove any runners that would be leftover...'''
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

        rank_range = self.runners.loc[:, "Rank"].tolist()
        for pot in self.runners["Pot"].unique():
            print(f"Drawing Pot {pot}")
            self.entrants[f"Pot_{pot}"] = ""  # Create empty pot col to store player name.
            '''Re-Assign range of possible runners to selected pot if fair draw is True.'''
            if self.fair_draw == True:
                rank_range = self.runners.loc[self.runners["Pot"] == pot, "Rank"].tolist()
            # print(rank_range)
            '''Assign runner at random to each entrant.'''
            for i in self.entrants.index:
                random_index = random.randrange(0, len(rank_range), 1)
                player_drawn = self.runners.loc[self.runners["Rank"] == rank_range[random_index], "runnerName"].values[0]
                # print(f"{player_drawn}")
                self.entrants.loc[i, f"Pot_{pot}"] = player_drawn
                rank_range.pop(random_index)

        # self.entrants.to_csv("../../data/out/draw_output.csv", index=False)
        return self.entrants


if __name__ == '__main__':
    d = Draw(event_id=2)
    d.run_draw()

