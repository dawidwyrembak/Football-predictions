from selenium import webdriver
import datetime
from datetime import timedelta
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--lang=en')
chrome_options.add_argument('--headless')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def convert_date(date):
    if date[0:8] == str('Tomorrow'):
        date = datetime.date.today() + datetime.timedelta(days=1)
        date = datetime.datetime.strptime(str(date), '%Y-%m-%d') \
            .strftime('%d %b %Y')

    if date[0:5] == str('Today'):
        date = datetime.date.today()
        date = datetime.datetime.strptime(str(date), '%Y-%m-%d') \
            .strftime('%d %b %Y')

    date = datetime.datetime.strptime(date, '%d %b %Y') \
        .strftime('%d/%m/%y')

    return date


def check_teams(home_team, away_team, flag, one_game_teams):
    if home_team not in one_game_teams \
            and away_team not in one_game_teams:
        one_game_teams.append(home_team)
        one_game_teams.append(away_team)
        flag = True

    if home_team in one_game_teams and away_team not in one_game_teams:
        one_game_teams.append(away_team)

    if home_team not in one_game_teams and away_team in one_game_teams:
        one_game_teams.append(home_team)

    return flag

# don't work, becouse of website changes
def scrap_upcoming_games_correct(league):
    if league == 1:
        driver.get("https://www.oddsportal.com/soccer/england/premier-league/")
    elif league == 2:
        driver.get("https://www.oddsportal.com/soccer/italy/serie-a/")
    elif league == 3:
        driver.get("https://www.oddsportal.com/soccer/spain/laliga/")

    main_table = driver.find_element("id", "tournamentTable")
    tbody = main_table.find_element("tag", "tbody")
    rows = tbody.find_elements("tag", "tr")
    date = ""
    one_game_teams = []

    next_games = pd.DataFrame()

    for row in rows:
        flag = False
        class_name = row.get_attribute("class")

        if "center nob-border" in class_name:
            date = row.find_element("class", "datet") \
                .get_attribute("textContent")

            date = convert_date(date)
            continue

        if class_name == "dark center" or class_name == "table-dummyrow":
            pass
        else:
            try:
                time = row.find_element("class", "datet") \
                    .get_attribute("textContent")
                time = datetime.datetime.strptime(time, "%H:%M") \
                       + timedelta(hours=1)
                time = time.strftime("%H:%M")

                if datetime.datetime.strptime(date, '%d/%m/%y') \
                        <= datetime.datetime.today():
                    if datetime.datetime.strptime(time, '%H:%M').time() \
                            <= datetime.datetime.now().time():
                        continue
            except ValueError:
                continue

            teams = row.find_element("class", "table-participant") \
                .find_elements("tag", "a")[-1] \
                .get_attribute("textContent").split(" - ")

            if check_teams(teams[0], teams[1], flag, one_game_teams) is False:
                continue

            odds = row.find_elements("class", "odds-nowrp")
            home_win_odds = odds[0].get_attribute("textContent")
            draw_odds = odds[1].get_attribute("textContent")
            away_win_odds = odds[2].get_attribute("textContent")

            next_games = next_games.append({'Date': date,
                                            'Time': time,
                                            'HomeTeam': teams[0],
                                            'AwayTeam': teams[1],
                                            'HomeWinOdds': home_win_odds,
                                            'DrawOdds': draw_odds,
                                            'AwayWinOdds': away_win_odds},
                                           ignore_index=True)
    return next_games


#mockup
def scrap_upcoming_games(league):
    if league == 1:
        return pd.DataFrame({'Date': ["23/05/2021", "23/05/2021"],
                                'Time': ["16:00", "16:00"],
                                'HomeTeam': ["West Ham", "Wolves"],
                                'AwayTeam': ["Southampton", "Manchester Utd"],
                                'HomeWinOdds': ["1.36", "2.55"],
                                'DrawOdds': ["2.22", "2.89"],
                                'AwayWinOdds': ["7.21", "3.11"],
                                })
    elif league == 2:
        return pd.DataFrame({'Date': ["23/05/2021", "23/05/2021"],
                                'Time': ["16:00", "16:00"],
                                'HomeTeam':["AC Milan", "Cagliari"],
                                'AwayTeam': ["Lazio", "Torino"],
                                'HomeWinOdds': ["1.36", "2.55"],
                                'DrawOdds': ["2.22", "2.89"],
                                'AwayWinOdds': ["7.21", "3.11"],
                                })
    
    elif league == 3:
        return pd.DataFrame({'Date': ["23/05/2021", "23/05/2021"],
                                'Time': ["16:00", "16:00"],
                                'HomeTeam': ["Sevilla", "Ath Bilbao"],
                                'AwayTeam': ["Getafe", "Real Madrid"],
                                'HomeWinOdds': ["1.36", "2.55"],
                                'DrawOdds': ["2.22", "2.89"],
                                'AwayWinOdds': ["7.21", "3.11"],
                                })