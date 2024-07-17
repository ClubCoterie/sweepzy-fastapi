import numpy as np
import pandas as pd
import sqlite3
import time
import requests
import urllib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class GolfTourney:

    def __init__(self, tourney_id, tourney_name):
        #Init empty DF
        self.tourney_id = tourney_id
        self.tourney_name = tourney_name
        self.lb_cols = ["POS", "PLAYER", "SCORE", "R1", "R2", "R3", "R4", "TOT", "tourney_id", "tourney_name"]
        self.stats_cols = ["POS", "PLAYER",	"YDS/DRV", "DRV ACC", "GIR", "PP GIR", "EAGLE", "BIRDIE", "PARS", "BOGEY", "DBL+", "SCORE", "tourney_id", "tourney_name"]
        self.url = f"https://www.espn.com/golf/leaderboard?tournamentId={self.tourney_id}"
        self.conn = self.get_sql_conn()
        self.cur = self.conn.cursor()

    def get_sql_conn(self):
        try:
            conn = sqlite3.connect('../sweepzy.db')
            return conn
        except sqlite3.Error as e:
            print(e)

    def update_table(self, df, table_name, df_cols):
        '''Create Table if not exists with min code.'''
        df.iloc[0:0].to_sql(name=table_name, con=self.conn, if_exists="append", index=False)

        sql_delete = f'''DELETE FROM {table_name} WHERE tourney_id = {self.tourney_id}'''

        sql_insert = f'''INSERT INTO {table_name}({", ".join(df_cols)})
                          VALUES({"?,"*(len(df_cols)-1)}?)'''

        self.cur.execute(sql_delete)
        self.conn.commit()
        for row in df.itertuples(index=False):
            print(row)
            self.cur.execute(sql_insert, row)
        self.conn.commit()

    def get_leaderboard(self):
        df = pd.read_html(self.url)[0]
        # Occasionally the first table contains information about a playoff
        # Checks length of table to confirm its a leaderboard and not a playoff
        if len(df.columns) <= 8: df = pd.read_html(self.url)[1]
        if df.columns[0] != 'POS': del df[df.columns[0]]
        df["tourney_id"] = self.tourney_id
        df["tourney_name"] = self.tourney_name
        df = df[self.lb_cols]
        return df

    def get_tournament_stats(self):
        '''Gives you a table of most birdies etc for fun prizes.'''
        driver = webdriver.Chrome()
        driver.get(self.url)
        time.sleep(1)
        '''Accept cookies if appears'''
        try:
            driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
            time.sleep(1)
        except NoSuchElementException:
            pass
        '''Click Player Stats Button'''
        driver.find_element(By.XPATH,
                            '//*[@id="fittPageContainer"]/div[3]/div/div/section[2]/div/div/div/div[1]/div/button[2]').click()
        time.sleep(1)
        '''Find Table element'''
        table_elem = driver.find_element(By.XPATH,
                                         '//*[@id="fittPageContainer"]/div[3]/div/div/section[2]/div/div/div/div[2]/div[4]/div/div/div[2]/table')
        '''Read as html'''
        table_html = table_elem.get_attribute("outerHTML")

        '''parse so can be read into a DF'''
        soup = BeautifulSoup(table_html, 'html.parser')
        df = pd.read_html(str(soup))[0]

        df["tourney_id"] = self.tourney_id
        df["tourney_name"] = self.tourney_name
        df = df[self.stats_cols]
        df.columns = df.columns.str.replace(r"[+]", "_PLUS", regex=True)
        df.columns = df.columns.str.replace(r"[ /]", "_", regex=True)
        self.stats_cols = df.columns.tolist()
        return df



if __name__ == '__main__':
    tourney_id = "401580359"
    tourney_name = "Genesis Scottish Open"
    tournament = GolfTourney(tourney_id, tourney_name)

    l_df = tournament.get_leaderboard()
    stat_df = tournament.get_tournament_stats()

    tournament.update_table(l_df, "golf_leaderboard", tournament.lb_cols)
    tournament.update_table(stat_df, "golf_stats", tournament.stats_cols)

    # l_df.to_csv(f"../data/out/{tourney_id}_leaderboard.csv", index=False)
    # stat_df.to_csv(f"../data/out/{tourney_id}_players_stats.csv", index=False)
