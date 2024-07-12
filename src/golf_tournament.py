import numpy as np
import pandas as pd
import time
import requests
import urllib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class GolfTourney:

    def __init__(self, tourney_id):
        #Init empty DF
        self.tourney_id = tourney_id
        self.url = f"https://www.espn.com/golf/leaderboard?tournamentId={self.tourney_id}"

    def get_leaderboard(self):
        df = pd.read_html(self.url)[0]
        # Occasionally the first table contains information about a playoff
        # Checks length of table to confirm its a leaderboard and not a playoff
        if len(df.columns) <= 8: df = pd.read_html(self.url)[1]
        if df.columns[0] != 'POS': del df[df.columns[0]]
        df["tourney_id"] = self.tourney_id
        return df

    def get_tournament_stats(self):
        '''Gives you a table of most birdies etc for fun prizes.'''
        driver = webdriver.Chrome()
        driver.get(self.url)
        time.sleep(5)
        '''Accept cookies if appears'''
        try:
            driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
            time.sleep(5)
        except NoSuchElementException:
            pass
        '''Click Player Stats Button'''
        driver.find_element(By.XPATH,
                            '//*[@id="fittPageContainer"]/div[3]/div/div/section[2]/div/div/div/div[1]/div/button[2]').click()
        time.sleep(5)
        '''Find Table element'''
        table_elem = driver.find_element(By.XPATH,
                                         '//*[@id="fittPageContainer"]/div[3]/div/div/section[2]/div/div/div/div[2]/div[4]/div/div/div[2]/table')
        '''Read as html'''
        table_html = table_elem.get_attribute("outerHTML")

        '''parse so can be read into a DF'''
        soup = BeautifulSoup(table_html, 'html.parser')
        df = pd.read_html(str(soup))[0]

        df["tourney_id"] = self.tourney_id
        return df

if __name__ == '__main__':
    tourney_id = "401580359"
    golfleaderboard = GolfTourney(tourney_id)
    l_df = golfleaderboard.get_leaderboard()
    stat_df = golfleaderboard.get_tournament_stats()
    l_df.to_csv(f"../data/out/{tourney_id}_leaderboard.csv", index=False)
    l_df.to_csv(f"../data/out/{tourney_id}_players_stats.csv", index=False)
