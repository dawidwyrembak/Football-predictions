import math
import statistics
from copy import deepcopy
import requests
import io
from scraping import scrap_upcoming_games
import pandas as pd


def result_to_points(home, result):
    if result == 'H':
        return 3 if home else 0
    elif result == 'A':
        return 0 if home else 3
    elif result == 'D':
        return 1
    elif result == 0:
        return 0


def result_to_wdl(home, result):
    if result == 'H':
        return 'W' if home else 'L'
    elif result == 'A':
        return 'L' if home else 'W'
    else:
        return 'D'


def accumulate_goals(data_frame, mode):
    teams_scoring_goals = {team: [0] for team in data_frame.HomeTeam.unique()}
    teams_conceding_goals = {team: [0] for team in data_frame.HomeTeam.unique()}

    if mode == 1:
        for i, row in data_frame.iterrows():
            teams_scoring_goals[row.HomeTeam].append(
                teams_scoring_goals[row.HomeTeam][-1] + row.FTHG)
            teams_conceding_goals[row.HomeTeam].append(
                teams_conceding_goals[row.HomeTeam][-1] + row.FTAG)
            teams_scoring_goals[row.AwayTeam].append(
                teams_scoring_goals[row.AwayTeam][-1] + row.FTAG)
            teams_conceding_goals[row.AwayTeam].append(
                teams_conceding_goals[row.AwayTeam][-1] + row.FTHG)

        data_frame['HGS_Season'] = 0
        data_frame['HGC_Season'] = 0
        data_frame['AGS_Season'] = 0
        data_frame['AGC_Season'] = 0

        for i, row in data_frame.iterrows():
            data_frame.at[i, 'HGS_Season'] = teams_scoring_goals[row.HomeTeam].pop(0)
            data_frame.at[i, 'AGS_Season'] = teams_scoring_goals[row.AwayTeam].pop(0)
            data_frame.at[i, 'HGC_Season'] = teams_conceding_goals[row.HomeTeam].pop(0)
            data_frame.at[i, 'AGC_Season'] = teams_conceding_goals[row.AwayTeam].pop(0)

    return data_frame


def accumulate_shots(data_table, mode):
    teams_scoring_shoots = {team: [0] for team in data_table.HomeTeam.unique()}
    teams_conceded_shoots = {team: [0] for team in data_table.HomeTeam.unique()}

    if mode == 1:
        for i, row in data_table.iterrows():
            teams_scoring_shoots[row.HomeTeam].append(
                teams_scoring_shoots[row.HomeTeam][-1] + row.HS)
            teams_conceded_shoots[row.HomeTeam].append(
                teams_conceded_shoots[row.HomeTeam][-1] + row.AS)

            teams_scoring_shoots[row.AwayTeam].append(
                teams_scoring_shoots[row.AwayTeam][-1] + row.AS)
            teams_conceded_shoots[row.AwayTeam].append(
                teams_conceded_shoots[row.AwayTeam][-1] + row.HS)

        data_table['HSS_Season'] = 0
        data_table['HSC_Season'] = 0
        data_table['ASS_Season'] = 0
        data_table['ASC_Season'] = 0

        for i, row in data_table.iterrows():
            data_table.at[i, 'HSS_Season'] = teams_scoring_shoots[row.HomeTeam].pop(0)
            data_table.at[i, 'ASS_Season'] = teams_scoring_shoots[row.AwayTeam].pop(0)
            data_table.at[i, 'HSC_Season'] = teams_conceded_shoots[row.HomeTeam].pop(0)
            data_table.at[i, 'ASC_Season'] = teams_conceded_shoots[row.AwayTeam].pop(0)

    return data_table


def accumulate_points(data_table, mode):
    teams = {team: [0] for team in data_table.HomeTeam.unique()}

    if mode == 1:
        for i, row in data_table.iterrows():
            teams[row.HomeTeam].append(teams[row.HomeTeam][-1] +
                                       result_to_points(home=True, result=row.FTR))
            teams[row.AwayTeam].append(teams[row.AwayTeam][-1] +
                                       result_to_points(home=False, result=row.FTR))
    else:
        season_k = 1
        relegated_teams = []
        promoted_teams = []

        for i, row in data_table.iterrows():
            if i == season_k * 370:
                for j in range(season_k * 370, season_k * 380):
                    relegated_teams.append(data_table.loc[j]['HomeTeam'])
                    relegated_teams.append(data_table.loc[j]['AwayTeam'])
            if i == season_k * 380:
                for j in range(season_k * 380, (season_k * 390)-1):
                    promoted_teams.append(data_table.loc[j]['HomeTeam'])
                    promoted_teams.append(data_table.loc[j]['AwayTeam'])

                temp = relegated_teams
                relegated_teams = set(relegated_teams) - set(promoted_teams)
                promoted_teams = set(promoted_teams) - set(temp)

            if i == season_k * 400:
                season_k = season_k + 1
                relegated_teams = []

            if row.HomeTeam in promoted_teams:
                teams[row.HomeTeam][-1] = \
                    math.floor(statistics.mean(teams[i][-1] for i in relegated_teams))
                promoted_teams.remove(row.HomeTeam)

            if row.AwayTeam in promoted_teams:
                teams[row.AwayTeam][-1] = \
                    math.floor(statistics.mean(teams[i][-1] for i in relegated_teams))
                promoted_teams.remove(row.AwayTeam)

            teams[row.HomeTeam].append(teams[row.HomeTeam][-1] +
                                       result_to_points(home=True, result=row.FTR))
            teams[row.AwayTeam].append(teams[row.AwayTeam][-1] +
                                       result_to_points(home=False, result=row.FTR))

            if len(promoted_teams) == 0:
                promoted_teams = []

    if mode == 1:
        data_table['HP_Season'] = 0
        data_table['AP_Season'] = 0

        for i, row in data_table.iterrows():
            data_table.at[i, 'HP_Season'] = teams[row.HomeTeam].pop(0)
            data_table.at[i, 'AP_Season'] = teams[row.AwayTeam].pop(0)
    else:
        data_table['HP_All'] = 0
        data_table['AP_All'] = 0

        for i, row in data_table.iterrows():
            data_table.at[i, 'HP_All'] = teams[row.HomeTeam].pop(0)
            data_table.at[i, 'AP_All'] = teams[row.AwayTeam].pop(0)

    return data_table


def current_place_in_table(data_table, mode):
    if mode == 1:
        teams = {team: [0] for team in data_table.HomeTeam.unique()}

        for i, row in data_table.iterrows():
            if row.Winner not in (1, 0, 2):
                continue

            teams[row.HomeTeam].append(teams[row.HomeTeam][-1] +
                                       result_to_points(home=True, result=row.FTR))
            teams[row.AwayTeam].append(teams[row.AwayTeam][-1] +
                                       result_to_points(home=False, result=row.FTR))

        # maksymalna ilość rozegranych meczów przez któryś zespół
        maximum_matches = 0
        for i, j in teams.items():
            if len(j) - 1 > maximum_matches:
                maximum_matches = len(j) - 1

        # dodajemy to, żeby dla zespołu który rozegrał najwięcej meczów były statystyki na upcoming_games
        for i, j in teams.items():
            if len(j) - 1 == maximum_matches:
                teams[i].append(teams[i][-1])

        # dodajemy 3 punkty
        for i, j in teams.items():
            while len(j) <= maximum_matches:
                teams[i].append(teams[i][-1] + 3)

        league_table = [sorted(teams, key=lambda name: teams[name][ii], reverse=True) for ii in
                        range(1, maximum_matches + 1, 1)]

        teams2 = {team: [0] for team in data_table.HomeTeam.unique()}
        for i in league_table:
            for j in teams2:
                temp = [place + 1 for place in range(len(i)) if i[place] == j]
                teams2[j].append(temp[0])

        data_table['HomeTable'] = 0
        data_table['AwayTable'] = 0

        for i, row in data_table.iterrows():
            data_table.at[i, 'HomeTable'] = math.ceil(teams2[row.HomeTeam].pop(0) / 5)
            data_table.at[i, 'AwayTable'] = math.ceil(teams2[row.AwayTeam].pop(0) / 5)

    return data_table


def form_goals_scored_5(data_table, mode):
    if mode == 1:
        teams = {team: ['0'] for team in data_table.HomeTeam.unique()}

        for i, row in data_table.iterrows():
            teams[row.HomeTeam].append(row.FTHG)
            teams[row.AwayTeam].append(row.FTAG)

        teams_2 = deepcopy(teams)
        teams_3 = deepcopy(teams)
        teams_4 = deepcopy(teams)
        teams_5 = deepcopy(teams)

        for t in teams:
            teams_2[t].insert(0, '0')

            teams_3[t].insert(0, '0')
            teams_3[t].insert(0, '0')

            teams_4[t].insert(0, '0')
            teams_4[t].insert(0, '0')
            teams_4[t].insert(0, '0')

            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')

        for i in range(1, 6):
            data_table['HomeMatchGoalsScored' + str(i)] = '0'
            data_table['AwayMatchGoalsScored' + str(i)] = '0'

        for i, row in data_table.iterrows():
            data_table.at[i, 'HomeMatchGoalsScored5'] = teams_5[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchGoalsScored4'] = teams_4[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchGoalsScored3'] = teams_3[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchGoalsScored2'] = teams_2[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchGoalsScored1'] = teams[row.HomeTeam].pop(0)

            data_table.at[i, 'AwayMatchGoalsScored5'] = teams_5[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchGoalsScored4'] = teams_4[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchGoalsScored3'] = teams_3[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchGoalsScored2'] = teams_2[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchGoalsScored1'] = teams[row.AwayTeam].pop(0)

    return data_table


def form_goals_conceded_5(data_table, mode):
    if mode == 1:
        teams = {team: ['0'] for team in data_table.HomeTeam.unique()}

        for i, row in data_table.iterrows():
            teams[row.HomeTeam].append(row.FTAG)
            teams[row.AwayTeam].append(row.FTHG)

        teams_2 = deepcopy(teams)
        teams_3 = deepcopy(teams)
        teams_4 = deepcopy(teams)
        teams_5 = deepcopy(teams)

        for t in teams:
            teams_2[t].insert(0, '0')

            teams_3[t].insert(0, '0')
            teams_3[t].insert(0, '0')

            teams_4[t].insert(0, '0')
            teams_4[t].insert(0, '0')
            teams_4[t].insert(0, '0')

            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')

        for i in range(1, 6):
            data_table['HomeMatchGoalsConceded' + str(i)] = '0'
            data_table['AwayMatchGoalsConceded' + str(i)] = '0'

        for i, row in data_table.iterrows():
            data_table.at[i, 'HomeMatchGoalsConceded5'] = teams_5[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchGoalsConceded4'] = teams_4[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchGoalsConceded3'] = teams_3[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchGoalsConceded2'] = teams_2[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchGoalsConceded1'] = teams[row.HomeTeam].pop(0)

            data_table.at[i, 'AwayMatchGoalsConceded5'] = teams_5[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchGoalsConceded4'] = teams_4[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchGoalsConceded3'] = teams_3[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchGoalsConceded2'] = teams_2[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchGoalsConceded1'] = teams[row.AwayTeam].pop(0)

    return data_table


def form_shots_scored_5(data_table, mode):
    if mode == 1:
        teams = {team: ['0'] for team in data_table.HomeTeam.unique()}

        for i, row in data_table.iterrows():
            teams[row.HomeTeam].append(row.HS)
            teams[row.AwayTeam].append(row.AS)

        teams_2 = deepcopy(teams)
        teams_3 = deepcopy(teams)
        teams_4 = deepcopy(teams)
        teams_5 = deepcopy(teams)

        for t in teams:
            teams_2[t].insert(0, '0')

            teams_3[t].insert(0, '0')
            teams_3[t].insert(0, '0')

            teams_4[t].insert(0, '0')
            teams_4[t].insert(0, '0')
            teams_4[t].insert(0, '0')

            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')

        for i in range(1, 6):
            data_table['HomeMatchShotsScored' + str(i)] = '0'
            data_table['AwayMatchShotsScored' + str(i)] = '0'

        for i, row in data_table.iterrows():
            data_table.at[i, 'HomeMatchShotsScored5'] = teams_5[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchShotsScored4'] = teams_4[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchShotsScored3'] = teams_3[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchShotsScored2'] = teams_2[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchShotsScored1'] = teams[row.HomeTeam].pop(0)

            data_table.at[i, 'AwayMatchShotsScored5'] = teams_5[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchShotsScored4'] = teams_4[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchShotsScored3'] = teams_3[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchShotsScored2'] = teams_2[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchShotsScored1'] = teams[row.AwayTeam].pop(0)

    return data_table


def form_shots_conceded_5(data_table, mode):
    if mode == 1:
        teams = {team: ['0'] for team in data_table.HomeTeam.unique()}

        for i, row in data_table.iterrows():
            teams[row.HomeTeam].append(row.AS)
            teams[row.AwayTeam].append(row.HS)

        teams_2 = deepcopy(teams)
        teams_3 = deepcopy(teams)
        teams_4 = deepcopy(teams)
        teams_5 = deepcopy(teams)

        for t in teams:
            teams_2[t].insert(0, '0')

            teams_3[t].insert(0, '0')
            teams_3[t].insert(0, '0')

            teams_4[t].insert(0, '0')
            teams_4[t].insert(0, '0')
            teams_4[t].insert(0, '0')

            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')

        for i in range(1, 6):
            data_table['HomeMatchShotsConceded' + str(i)] = '0'
            data_table['AwayMatchShotsConceded' + str(i)] = '0'

        for i, row in data_table.iterrows():
            data_table.at[i, 'HomeMatchShotsConceded5'] = teams_5[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchShotsConceded4'] = teams_4[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchShotsConceded3'] = teams_3[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchShotsConceded2'] = teams_2[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatchShotsConceded1'] = teams[row.HomeTeam].pop(0)

            data_table.at[i, 'AwayMatchShotsConceded5'] = teams_5[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchShotsConceded4'] = teams_4[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchShotsConceded3'] = teams_3[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchShotsConceded2'] = teams_2[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatchShotsConceded1'] = teams[row.AwayTeam].pop(0)

    return data_table


def form_5(data_table, mode):
    if mode == 1:
        teams = {team: ['0'] for team in data_table.HomeTeam.unique()}

        for i, row in data_table.iterrows():
            teams[row.HomeTeam].append(result_to_wdl(home=True, result=row.FTR))
            teams[row.AwayTeam].append(result_to_wdl(home=False, result=row.FTR))

        teams_2 = deepcopy(teams)
        teams_3 = deepcopy(teams)
        teams_4 = deepcopy(teams)
        teams_5 = deepcopy(teams)

        for t in teams:
            teams_2[t].insert(0, '0')

            teams_3[t].insert(0, '0')
            teams_3[t].insert(0, '0')

            teams_4[t].insert(0, '0')
            teams_4[t].insert(0, '0')
            teams_4[t].insert(0, '0')

            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')
            teams_5[t].insert(0, '0')

        for i in range(1, 6):
            data_table['HomeMatch' + str(i)] = '0'
            data_table['AwayMatch' + str(i)] = '0'

        for i, row in data_table.iterrows():
            data_table.at[i, 'HomeMatch5'] = teams_5[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatch4'] = teams_4[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatch3'] = teams_3[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatch2'] = teams_2[row.HomeTeam].pop(0)
            data_table.at[i, 'HomeMatch1'] = teams[row.HomeTeam].pop(0)

            data_table.at[i, 'AwayMatch5'] = teams_5[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatch4'] = teams_4[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatch3'] = teams_3[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatch2'] = teams_2[row.AwayTeam].pop(0)
            data_table.at[i, 'AwayMatch1'] = teams[row.AwayTeam].pop(0)

    return data_table


def points_form(data_table, mode):
    if mode == 1:
        data_table['HP_5'] = 0
        data_table['AP_5'] = 0

        for i, row in data_table.iterrows():
            home_form = 0
            away_form = 0

            for s in row.HomeForm:
                if s == 'W':
                    home_form += 3
                elif s == 'D':
                    home_form += 1
                else:
                    home_form += 0

            for s in row.AwayForm:
                if s == 'W':
                    away_form += 3
                elif s == 'D':
                    away_form += 1
                else:
                    away_form += 0

            data_table.at[i, 'HP_5'] = home_form
            data_table.at[i, 'AP_5'] = away_form

    return data_table


def preprocess_season(data_table, mode):
    data_table.loc[data_table.FTR == 'H', 'Winner'] = 1
    data_table.loc[data_table.FTR == 'D', 'Winner'] = 0
    data_table.loc[data_table.FTR == 'A', 'Winner'] = 2
    data_table = accumulate_goals(data_table, mode)
    data_table = accumulate_shots(data_table, mode)
    data_table = accumulate_points(data_table, mode)
    data_table = current_place_in_table(data_table, mode)
    data_table['GDiff_Season'] = (data_table['HGS_Season'] -
                                  data_table['HGC_Season']) - \
                                 (data_table['AGS_Season'] -
                                  data_table['AGC_Season'])

    data_table = form_goals_scored_5(data_table, mode)
    data_table = form_goals_conceded_5(data_table, mode)

    data_table = form_shots_scored_5(data_table, mode)
    data_table = form_shots_conceded_5(data_table, mode)
    if mode == 1:
        data_table['HGS_5'] = \
            pd.Series(data_table['HomeMatchGoalsScored1']).astype(int) + \
            pd.Series(data_table['HomeMatchGoalsScored2']).astype(int) + \
            pd.Series(data_table['HomeMatchGoalsScored3']).astype(int) + \
            pd.Series(data_table['HomeMatchGoalsScored4']).astype(int) + \
            pd.Series(data_table['HomeMatchGoalsScored5']).astype(int)

        data_table['AGS_5'] = \
            pd.Series(data_table['AwayMatchGoalsScored1']).astype(int) + \
            pd.Series(data_table['AwayMatchGoalsScored2']).astype(int) + \
            pd.Series(data_table['AwayMatchGoalsScored3']).astype(int) + \
            pd.Series(data_table['AwayMatchGoalsScored4']).astype(int) + \
            pd.Series(data_table['AwayMatchGoalsScored5']).astype(int)

        data_table['HGC_5'] = \
            pd.Series(data_table['HomeMatchGoalsConceded1']).astype(int) + \
            pd.Series(data_table['HomeMatchGoalsConceded2']).astype(int) + \
            pd.Series(data_table['HomeMatchGoalsConceded3']).astype(int) + \
            pd.Series(data_table['HomeMatchGoalsConceded4']).astype(int) + \
            pd.Series(data_table['HomeMatchGoalsConceded5']).astype(int)

        data_table['AGC_5'] = \
            pd.Series(data_table['AwayMatchGoalsConceded1']).astype(int) + \
            pd.Series(data_table['AwayMatchGoalsConceded2']).astype(int) + \
            pd.Series(data_table['AwayMatchGoalsConceded3']).astype(int) + \
            pd.Series(data_table['AwayMatchGoalsConceded4']).astype(int) + \
            pd.Series(data_table['AwayMatchGoalsConceded5']).astype(int)

        data_table['HSS_5'] = \
            pd.Series(data_table['HomeMatchShotsScored1']).astype(int) + \
            pd.Series(data_table['HomeMatchShotsScored2']).astype(int) + \
            pd.Series(data_table['HomeMatchShotsScored3']).astype(int) + \
            pd.Series(data_table['HomeMatchShotsScored4']).astype(int) + \
            pd.Series(data_table['HomeMatchShotsScored5']).astype(int)

        data_table['ASS_5'] = \
            pd.Series(data_table['AwayMatchShotsScored1']).astype(int) + \
            pd.Series(data_table['AwayMatchShotsScored2']).astype(int) + \
            pd.Series(data_table['AwayMatchShotsScored3']).astype(int) + \
            pd.Series(data_table['AwayMatchShotsScored4']).astype(int) + \
            pd.Series(data_table['AwayMatchShotsScored5']).astype(int)

        data_table['HSC_5'] = \
            pd.Series(data_table['HomeMatchShotsConceded1']).astype(int) + \
            pd.Series(data_table['HomeMatchShotsConceded2']).astype(int) + \
            pd.Series(data_table['HomeMatchShotsConceded3']).astype(int) + \
            pd.Series(data_table['HomeMatchShotsConceded4']).astype(int) + \
            pd.Series(data_table['HomeMatchShotsConceded5']).astype(int)

        data_table['ASC_5'] = \
            pd.Series(data_table['AwayMatchShotsConceded1']).astype(int) + \
            pd.Series(data_table['AwayMatchShotsConceded2']).astype(int) + \
            pd.Series(data_table['AwayMatchShotsConceded3']).astype(int) + \
            pd.Series(data_table['AwayMatchShotsConceded4']).astype(int) + \
            pd.Series(data_table['AwayMatchShotsConceded5']).astype(int)

    data_table = form_5(data_table, mode)

    if mode == 1:
        data_table['HomeForm'] = \
            data_table['HomeMatch1'] + \
            data_table['HomeMatch2'] + \
            data_table['HomeMatch3'] + \
            data_table['HomeMatch4'] + \
            data_table['HomeMatch5']

        data_table['AwayForm'] = \
            data_table['AwayMatch1'] + \
            data_table['AwayMatch2'] + \
            data_table['AwayMatch3'] + \
            data_table['AwayMatch4'] + \
            data_table['AwayMatch5']

    data_table = points_form(data_table, mode)

    data_table['GDiff_5'] = (data_table['HGS_5'] -
                             data_table['HGC_5']) - \
                            (data_table['AGS_5'] -
                             data_table['AGC_5'])

    data_table['PDiff_Season'] = data_table['HP_Season'] - data_table['AP_Season']

    data_table['PDiff_5'] = data_table['HP_5'] - data_table['AP_5']

    return data_table


def rename_teams(data_table):
    data_table = data_table.replace("Roma", "AS Roma")
    data_table = data_table.replace("Milan", "AC Milan")
    data_table = data_table.replace("Man United", "Manchester Utd")
    data_table = data_table.replace("Sheffield United", "Sheffield Utd")
    data_table = data_table.replace("Man City", "Manchester City")
    data_table = data_table.replace("Celta", "Celta Vigo")
    data_table = data_table.replace("Granada", "Granada CF")
    data_table = data_table.replace("Cadiz", "Cadiz CF")
    data_table = data_table.replace("Sociedad", "Real Sociedad")
    data_table = data_table.replace("Ath Madrid", "Atl. Madrid")

    return data_table


def preprocessing_data(league):
    season_16_17 = pd.DataFrame()
    season_17_18 = pd.DataFrame()
    season_18_19 = pd.DataFrame()
    season_19_20 = pd.DataFrame()
    season_20_21 = pd.DataFrame()

    if league == 1:
        season_16_17 = pd.read_csv('main/static/main/premier_league/E0_16_17.csv', sep=",", index_col=None)
        season_17_18 = pd.read_csv('main/static/main/premier_league/E0_17_18.csv', sep=",", index_col=None)
        season_18_19 = pd.read_csv('main/static/main/premier_league/E0_18_19.csv', sep=",", index_col=None)
        season_19_20 = pd.read_csv('main/static/main/premier_league/E0_19_20.csv', sep=",", index_col=None)

        testfile = requests.get("https://www.football-data.co.uk/mmz4281/2021/E0.csv").content
        season_20_21 = pd.read_csv(io.StringIO(testfile.decode('utf-8')))
        season_20_21.fillna(0)

    elif league == 2:
        season_16_17 = pd.read_csv('main/static/main/serie_a/I1_16_17.csv', sep=",", index_col=None)
        season_17_18 = pd.read_csv('main/static/main/serie_a/I1_17_18.csv', sep=",", index_col=None)
        season_18_19 = pd.read_csv('main/static/main/serie_a/I1_18_19.csv', sep=",", index_col=None)
        season_19_20 = pd.read_csv('main/static/main/serie_a/I1_19_20.csv', sep=",", index_col=None)

        testfile = requests.get("https://www.football-data.co.uk/mmz4281/2021/I1.csv").content
        season_20_21 = pd.read_csv(io.StringIO(testfile.decode('utf-8')), sep=",", index_col=None)
        season_20_21.fillna(0, inplace=True)

    elif league == 3:
        season_16_17 = pd.read_csv('main/static/main/la_liga/SP1_16_17.csv', sep=",", index_col=None)
        season_17_18 = pd.read_csv('main/static/main/la_liga/SP1_17_18.csv', sep=",", index_col=None)
        season_18_19 = pd.read_csv('main/static/main/la_liga/SP1_18_19.csv', sep=",", index_col=None)
        season_19_20 = pd.read_csv('main/static/main/la_liga/SP1_19_20.csv', sep=",", index_col=None)

        testfile = requests.get("https://www.football-data.co.uk/mmz4281/2021/SP1.csv").content
        season_20_21 = pd.read_csv(io.StringIO(testfile.decode('utf-8')))
        season_20_21.fillna(0, inplace=True)

    upcoming_games = get_upcoming_games(league)
    season_16_17 = season_16_17[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HS', 'AS']]
    season_17_18 = season_17_18[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HS', 'AS']]
    season_18_19 = season_18_19[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HS', 'AS']]
    season_19_20 = season_19_20[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HS', 'AS']]
    season_20_21 = season_20_21[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HS', 'AS']]

    upcoming_games = upcoming_games.join(pd.DataFrame(columns=['FTHG', 'FTAG', 'FTR', 'HS', 'AS']))

    upcoming_games.fillna(0, inplace=True)

    last_seasons = [
        season_16_17,
        season_17_18,
        season_18_19,
        season_19_20,
    ]

    current_season = [
        season_20_21[:-2], #change it to keep all
        upcoming_games
    ]

    for season in last_seasons:
        preprocess_season(data_table=season, mode=1)

    last_seasons = pd.concat(last_seasons, ignore_index=True)
    current_season = pd.concat(current_season, ignore_index=True)

    current_season = rename_teams(current_season)

    preprocess_season(data_table=current_season, mode=1)

    all_seasons = [last_seasons, current_season]
    all_data = pd.concat(all_seasons, ignore_index=True)

    all_data = rename_teams(all_data)

    preprocess_season(data_table=all_data, mode=2)

    all_data = all_data.reset_index(drop=True)

    all_data.to_csv("main/static/main/data" + str(league) + ".csv")

    all_data = all_data[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HS', 'AS',
                         'Winner', 'HGS_Season', 'HGC_Season', 'AGS_Season', 'AGC_Season',
                         'HSS_Season', 'HSC_Season', 'ASS_Season', 'ASC_Season', 'HP_Season',
                         'AP_Season', 'HomeTable', 'AwayTable', 'GDiff_Season', 'HGS_5', 'AGS_5',
                         'HGC_5', 'AGC_5', 'HSS_5', 'ASS_5', 'HSC_5', 'ASC_5',  'HomeForm',
                         'AwayForm', 'HP_5', 'AP_5', 'GDiff_5', 'PDiff_Season', 'PDiff_5',
                         'Time', 'HomeWinOdds', 'DrawOdds', 'AwayWinOdds', 'HP_All', 'AP_All']]
    return all_data


def get_upcoming_games(league):
    upcoming_games = scrap_upcoming_games(league)
    upcoming_games['Date'] = pd.to_datetime(upcoming_games['Date'], dayfirst=True)

    upcoming_games = upcoming_games[['Date', 'Time', 'HomeTeam', 'AwayTeam',
                                     'HomeWinOdds', 'DrawOdds', 'AwayWinOdds']].head(10)

    return upcoming_games
