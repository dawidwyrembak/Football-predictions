import pandas as pd
import requests
import io


def result_to_points(home, result):
    if result == 'H':
        return 3 if home else 0
    elif result == 'A':
        return 0 if home else 3
    elif result == 'D':
        return 1
    elif result == 0:
        return 0


def number_of_played_games(data_table, mode):
    teams = {team: [1] for team in data_table.HomeTeam.unique()}

    if mode == 1:
        for i, row in data_table.iterrows():
            teams[row.HomeTeam].append(
                teams[row.HomeTeam][-1] + 1)
            teams[row.AwayTeam].append(
                teams[row.AwayTeam][-1] + 1)

        data_table['NumberMatchesPlayedHome'] = 0
        data_table['NumberMatchesPlayedAway'] = 0

        for i, row in data_table.iterrows():
            data_table.at[i, 'NumberMatchesPlayedHome'] = teams[row.HomeTeam].pop(0)
            data_table.at[i, 'NumberMatchesPlayedAway'] = teams[row.AwayTeam].pop(0)

    return data_table


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

    if mode == 1:
        data_frame['HomeGoalsScored_Season'] = 0
        data_frame['HomeGoalsConceded_Season'] = 0
        data_frame['AwayGoalsScored_Season'] = 0
        data_frame['AwayGoalsConceded_Season'] = 0

        for i, row in data_frame.iterrows():
            data_frame.at[i, 'HomeGoalsScored_Season'] = teams_scoring_goals[row.HomeTeam].pop(1)
            data_frame.at[i, 'AwayGoalsScored_Season'] = teams_scoring_goals[row.AwayTeam].pop(1)
            data_frame.at[i, 'HomeGoalsConceded_Season'] = teams_conceding_goals[row.HomeTeam].pop(1)
            data_frame.at[i, 'AwayGoalsConceded_Season'] = teams_conceding_goals[row.AwayTeam].pop(1)

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

    if mode == 1:
        data_table['HomeShotsScored_Season'] = 0
        data_table['HomeShotsConceded_Season'] = 0
        data_table['AwayShotsScored_Season'] = 0
        data_table['AwayShotsConceded_Season'] = 0

        for i, row in data_table.iterrows():
            data_table.at[i, 'HomeShotsScored_Season'] = teams_scoring_shoots[row.HomeTeam].pop(1)
            data_table.at[i, 'AwayShotsScored_Season'] = teams_scoring_shoots[row.AwayTeam].pop(1)
            data_table.at[i, 'HomeShotsConceded_Season'] = teams_conceded_shoots[row.HomeTeam].pop(1)
            data_table.at[i, 'AwayShotsConceded_Season'] = teams_conceded_shoots[row.AwayTeam].pop(1)

    return data_table


def accumulate_points(data_table, mode):
    teams = {team: [0] for team in data_table.HomeTeam.unique()}

    if mode == 1:
        for i, row in data_table.iterrows():
            teams[row.HomeTeam].append(teams[row.HomeTeam][-1] +
                                       result_to_points(home=True, result=row.FTR))
            teams[row.AwayTeam].append(teams[row.AwayTeam][-1] +
                                       result_to_points(home=False, result=row.FTR))

    if mode == 1:
        data_table['HomePoints_Season'] = 0
        data_table['AwayPoints_Season'] = 0

        for i, row in data_table.iterrows():
            data_table.at[i, 'HomePoints_Season'] = teams[row.HomeTeam].pop(1)
            data_table.at[i, 'AwayPoints_Season'] = teams[row.AwayTeam].pop(1)

    return data_table


def disconnect_home_away(data_table):
    home = data_table.drop(['AwayTeam', 'NumberMatchesPlayedAway',
                            'AwayGoalsScored_Season', 'AwayGoalsConceded_Season',
                            'AwayPoints_Season'], axis=1)
    away = data_table.drop(['HomeTeam', 'NumberMatchesPlayedHome',
                            'HomeGoalsScored_Season', 'HomeGoalsConceded_Season',
                            'HomePoints_Season'], axis=1)

    home = home.rename(
        columns={'HomeTeam': 'Team', 'NumberMatchesPlayedHome': 'NumberOfMatches',
                 'HomeGoalsScored_Season': 'GoalsScored', 'HomeGoalsConceded_Season': 'GoalsConceded',
                 'HomePoints_Season': 'Points'})

    away = away.rename(
        columns={'AwayTeam': 'Team', 'NumberMatchesPlayedAway': 'NumberOfMatches',
                 'AwayGoalsScored_Season': 'GoalsScored', 'AwayGoalsConceded_Season': 'GoalsConceded',
                 'AwayPoints_Season': 'Points'})

    data_table = pd.concat([home, away], ignore_index=True)

    return data_table


def preprocess_season(data_table, mode):
    data_table = number_of_played_games(data_table, mode)
    data_table = accumulate_goals(data_table, mode)
    data_table = accumulate_points(data_table, mode)
    data_table = disconnect_home_away(data_table)

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


def preprocessing_data_table(league):
    season_20_21 = pd.DataFrame()

    if league == 1:
        testfile = requests.get("https://www.football-data.co.uk/mmz4281/2021/E0.csv").content
        season_20_21 = pd.read_csv(io.StringIO(testfile.decode('utf-8')))
        season_20_21.fillna(0)

    elif league == 2:
        testfile = requests.get("https://www.football-data.co.uk/mmz4281/2021/I1.csv").content
        season_20_21 = pd.read_csv(io.StringIO(testfile.decode('utf-8')), sep=",", index_col=None)
        season_20_21.fillna(0, inplace=True)

    elif league == 3:
        testfile = requests.get("https://www.football-data.co.uk/mmz4281/2021/SP1.csv").content
        season_20_21 = pd.read_csv(io.StringIO(testfile.decode('utf-8')))
        season_20_21.fillna(0, inplace=True)

    season_20_21 = season_20_21[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HS', 'AS']]

    season_20_21 = preprocess_season(data_table=season_20_21, mode=1)

    season_20_21['GoalsDiff'] = season_20_21['GoalsScored'] - season_20_21['GoalsConceded']

    season_20_21 = rename_teams(season_20_21)

    season_20_21 = season_20_21[["Team", "NumberOfMatches", "Points", "GoalsScored", "GoalsConceded", "GoalsDiff"]]\
        .groupby("Team")\
        .max()\
        .sort_values(["Points", "GoalsDiff", "GoalsScored"], ascending=(False, False, False))

    season_20_21 = season_20_21.reset_index()
    season_20_21['Place'] = season_20_21.index + 1

    return season_20_21[["Place", "Team", "NumberOfMatches", "Points", "GoalsScored", "GoalsConceded"]]
