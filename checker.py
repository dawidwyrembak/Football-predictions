import pandas as pd
import requests
import io
import matplotlib.pyplot as plt
import numpy as np


def check_accuracy():
    season_19_20 = pd.read_csv('main/static/main/premier_league/E0_19_20.csv', sep=",", index_col=None)

    testfile = requests.get("https://www.football-data.co.uk/mmz4281/2021/E0.csv").content
    season_20_21 = pd.read_csv(io.StringIO(testfile.decode('utf-8')))
    season_20_21.fillna(0)

    season_19_20 = season_19_20[['FTR', 'B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA']]
    season_20_21 = season_20_21[['FTR', 'B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA']]

    data_table = [season_19_20, season_20_21]
    data_table = pd.concat(data_table, ignore_index=True)
    data_table = data_table.reset_index(drop=True)

    k = 0
    for i, row in data_table.iterrows():
        if row.B365H < row.B365D and row.B365H < row.B365A and row.FTR == 'H':
            k = k + 1
        elif row.B365D < row.B365H and row.B365D < row.B365A and row.FTR == 'D':
            k = k + 1
        elif row.B365A < row.B365H and row.B365A < row.B365D and row.FTR == 'A':
            k = k + 1

    print("B365: ", (k / data_table.shape[0]))

    k = 0
    for i, row in data_table.iterrows():
        if row.BWH < row.BWD and row.BWH < row.BWA and row.FTR == 'H':
            k = k + 1
        elif row.BWD < row.BWH and row.BWD < row.BWA and row.FTR == 'D':
            k = k + 1
        elif row.BWA < row.BWH and row.BWA < row.BWD and row.FTR == 'A':
            k = k + 1

    print("BW: ", (k / data_table.shape[0]))


def sigmoid(z):
    return 1.0 / (1 + np.exp(-z))


def relu(x):
    return np.maximum(0, x)


def softmax(x):
    return np.exp(x) / np.sum(np.exp(x))


def leaky_relu(x):
    return np.maximum(0.1 * x, x)


def elu(x):
    a = []
    for i in x:
        if i >= 0:
            a.append(i)
        else:
            a.append(1 * (np.exp(i) - 1))
    return a


def tanh(x):
    return (np.exp(x) - np.exp(-x)) / (np.exp(x) + np.exp(-x))


def draw_plots():
    x = np.arange(-5, 5, 0.1)

    plt.plot(x, leaky_relu(x), label='')
    plt.grid(alpha=.4, linestyle='--')
    plt.savefig('leaky_relu.png')
    # plt.savefig('relu.png')

draw_plots()
