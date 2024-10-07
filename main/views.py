from django.shortcuts import render
from prediction import *

games_pl = []
games_sa = []
games_ll = []
results = []

data_pl = pd.DataFrame()
data_sa = pd.DataFrame()
data_ll = pd.DataFrame()
train_flag = False
league = 0
algorithm = 0
all_games = []
p = 0


def start(request):
    global data_pl, data_sa, data_ll, train_flag
    train_flag = False
    data_pl = preprocessing_data(1)
    data_sa = preprocessing_data(2)
    data_ll = preprocessing_data(3)
    data_pl = data_pl.loc[data_pl['Time'].notnull()].reset_index(drop=True)
    data_sa = data_sa.loc[data_sa['Time'].notnull()].reset_index(drop=True)
    data_ll = data_ll.loc[data_ll['Time'].notnull()].reset_index(drop=True)
    return render(request, 'main/start.html')


def home(request):
    global league, all_games, algorithm, data_pl, data_sa, data_ll, train_flag
    league = 0
    algorithm = 0
    train_flag = False

    if data_pl.empty:
        return start(request)

    if len(games_pl) == 0:
        pl_games = data_pl

        for _, row in pl_games.iterrows():
            games_pl.append({
                "Date": row.Date.strftime('%d/%m/%y'),
                "Time": row.Time,
                "LogoHome": "static/main/england_logo/" + row.HomeTeam.replace(" ", "_") + ".png",
                "HomeTeam": row.HomeTeam,
                "LogoAway": "static/main/england_logo/" + row.AwayTeam.replace(" ", "_") + ".png",
                "AwayTeam": row.AwayTeam,
                "HGS": row.HGS_Season,
                "HGC": row.HGC_Season,
                "HP": row.HP_Season,
                "HF": row.HomeForm,
                "AGS": row.AGS_Season,
                "AGC": row.AGC_Season,
                "AP": row.AP_Season,
                "AF": row.AwayForm,
                "OddH": row.HomeWinOdds,
                "OddD": row.DrawOdds,
                "OddA": row.AwayWinOdds
            })

    if len(games_sa) == 0:
        sa_games = data_sa
        for i, row in sa_games.iterrows():
            games_sa.append({
                "Date": row.Date.strftime('%d/%m/%y'),
                "Time": row.Time,
                "LogoHome": "static/main/italy_logo/" + row.HomeTeam.replace(" ", "_") + ".png",
                "HomeTeam": row.HomeTeam,
                "LogoAway": "static/main/italy_logo/" + row.AwayTeam.replace(" ", "_") + ".png",
                "AwayTeam": row.AwayTeam,
                "HGS": row.HGS_Season,
                "HGC": row.HGC_Season,
                "HP": row.HP_Season,
                "HF": row.HomeForm,
                "AGS": row.AGS_Season,
                "AGC": row.AGC_Season,
                "AP": row.AP_Season,
                "AF": row.AwayForm,
                "OddH": row.HomeWinOdds,
                "OddD": row.DrawOdds,
                "OddA": row.AwayWinOdds
            })

    if len(games_ll) == 0:
        ll_games = data_ll
        for _, row in ll_games.iterrows():
            games_ll.append({
                "Date": row.Date.strftime('%d/%m/%y'),
                "Time": row.Time,
                "LogoHome": "static/main/spain_logo/" + row.HomeTeam.replace(" ", "_") + ".png",
                "HomeTeam": row.HomeTeam,
                "LogoAway": "static/main/spain_logo/" + row.AwayTeam.replace(" ", "_") + ".png",
                "AwayTeam": row.AwayTeam,
                "HGS": row.HGS_Season,
                "HGC": row.HGC_Season,
                "HP": row.HP_Season,
                "HF": row.HomeForm,
                "AGS": row.AGS_Season,
                "AGC": row.AGC_Season,
                "AP": row.AP_Season,
                "AF": row.AwayForm,
                "OddH": row.HomeWinOdds,
                "OddD": row.DrawOdds,
                "OddA": row.AwayWinOdds
            })

    all_games = [games_pl, games_sa, games_ll]

    return render(request, 'main/home.html')


def premier_league(request):
    global league, train_flag, algorithm

    if len(all_games) == 0:
        return start(request)
    league = 1
    algorithm = 0
    train_flag = False
    context = {
        'games': all_games[league - 1],
        'alert_flag': False
    }

    return render(request, 'main/home.html', context)


def serie_a(request):
    global league, train_flag, algorithm
    if len(all_games) == 0:
        return start(request)
    league = 2
    algorithm = 0
    train_flag = False
    context = {
        'games': all_games[league - 1],
        'alert_flag': False
    }

    return render(request, 'main/home.html', context)


def la_liga(request):
    global league, train_flag, algorithm

    if len(all_games) == 0:
        return start(request)
    league = 3
    algorithm = 0
    train_flag = False
    context = {
        'games': all_games[league - 1],
        'alert_flag': False
    }

    return render(request, 'main/home.html', context)


def neural_network(request):
    global algorithm, train_flag
    algorithm = 1
    train_flag = False
    context = {
        'games': all_games[league - 1],
        'alert_flag': False,
        'algorithm_flag': True,
        'algorithm': 'Train: Neural Network'
    }
    return render(request, 'main/home.html', context)


def regression(request):
    global algorithm, train_flag
    if len(all_games) == 0:
        return start(request)
    algorithm = 3
    train_flag = False
    context = {
        'games': all_games[league - 1],
        'alert_flag': False,
        'algorithm_flag': True,
        'algorithm': 'Train: Softmax Regression'
    }
    return render(request, 'main/home.html', context)


def random_forest(request):
    global algorithm, train_flag
    if len(all_games) == 0:
        return start(request)
    algorithm = 2
    train_flag = False
    context = {
        'games': all_games[league - 1],
        'alert_flag': False,
        'algorithm_flag': True,
        'algorithm': 'Train: Random Forest'
    }
    return render(request, 'main/home.html', context)


def training(request):
    global p, algorithm, train_flag
    if len(all_games) == 0:
        return start(request)

    if league == 0:
        context = {
            'alert_flag': True,
            'message': "You can't train a model before selecting a league!"
        }
    elif algorithm == 0:
        context = {'games': all_games[league - 1],
                   'alert_flag': True,
                   'message': "You can't train a model before selecting an algorithm!"
                   }
    else:
        p = Prediction(algorithm, league)

        p.train_model()

        train_flag = True
        if algorithm == 3:
            context = {
                'games': all_games[league - 1],
                'alert_flag': False,
                'algorithm_flag': True,
                'algorithm': 'Train: Softmax Regression'
            }
        elif algorithm == 2:
            context = {
                'games': all_games[league - 1],
                'alert_flag': False,
                'algorithm_flag': True,
                'algorithm': 'Train: Random Forest'
            }
        else:
            context = {
                'games': all_games[league - 1],
                'alert_flag': False,
                'algorithm_flag': True,
                'algorithm': 'Train: Neural Network'
            }
    return render(request, 'main/home.html', context)


def predicting(request):
    global p, all_games, train_flag
    if len(all_games) == 0:
        return start(request)
    if train_flag:
        rr = p.predict()
        if len(results) == 0:
            for i, row in rr.iterrows():
                results.append({
                    "WynikH": format(row.Bet_home_win, ".2f"),
                    "WynikD": format(row.Bet_draw, ".2f"),
                    "WynikA": format(row.Bet_away_win, ".2f")
                })

        for item in all_games[league - 1]:
            item.update(results.pop(0))

        if algorithm == 3:
            context = {
                'results': results,
                'games': all_games[league - 1],
                'alert_flag': False,
                'algorithm_flag': True,
                'algorithm': 'Train: Softmax Regression'
            }
        elif algorithm == 2:
            context = {
                'results': results,
                'games': all_games[league - 1],
                'alert_flag': False,
                'algorithm_flag': True,
                'algorithm': 'Train: Random Forest'
            }
        else:
            context = {
                'results': results,
                'games': all_games[league - 1],
                'alert_flag': False,
                'algorithm_flag': True,
                'algorithm': 'Train: Neural Network'
            }
    else:
        if league == 0:
            context = {
                'alert_flag': True,
                'message': "You haven't trained model yet!"
            }
        else:
            context = {'games': all_games[league - 1],
                       'alert_flag': True,
                       'message': "You haven't trained model yet!"
                       }

    return render(request, 'main/home.html', context)


def visualisation(request):
    return render(request, 'main/visualisation.html')


def table(request):
    return render(request, 'main/table.html')