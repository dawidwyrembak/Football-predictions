from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout
from preprocess import *
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

#gpu = tf.config.experimental.list_physical_devices('GPU')[0]
#tf.config.experimental.set_memory_growth(gpu, True)

pd.set_option('display.max_columns', None)


class Prediction:
    def __init__(self, alghoritm, league):

        tf.random.set_seed(1234)
        self.alghoritm = alghoritm
        self.league = league
        self.train_columns = [
            'HGS_Season', 'HGC_Season',
            'AGS_Season', 'AGC_Season',
            'HSS_Season', 'HSC_Season',
            'ASS_Season', 'ASC_Season',
            'HP_Season', 'AP_Season',
            'HP_All', 'AP_All',
            'HomeTable', 'AwayTable',
            'HGS_5', 'HGC_5',
            'AGS_5', 'AGC_5',
            'HSS_5', 'HSC_5',
            'ASS_5', 'ASC_5',
            'HP_5', 'AP_5',
            'GDiff_Season', 'GDiff_5',
            'PDiff_Season', 'PDiff_5',
            'Winner']

        self.data_table = pd.read_csv("main/static/main/data"
                                      + str(league) + ".csv", sep=",", index_col=None)
        self.model = self.create_model()

    def create_model(self):
        if self.alghoritm == 1:
            if self.league == 1:
                model = Sequential()
                model.add(Dense(64, activation=tf.nn.relu, input_shape=(28,)))
                model.add(Dense(64, activation=tf.nn.relu))
                model.add(Dense(32, activation=tf.nn.relu))
                model.add(Dropout(0.2))
                model.add(Dense(32, activation=tf.nn.relu, kernel_regularizer=tf.keras.regularizers.l2(l=0.1)))
                model.add(Dense(3, activation=tf.nn.softmax))

                model.compile(loss='categorical_crossentropy', #optimizer=keras.optimizers.Adam(lr=0.01),
                              metrics=['accuracy'])

                model.summary()
            if self.league == 2:
                model = Sequential()
                model.add(Dense(64, activation=tf.nn.relu, input_shape=(28,)))
                model.add(Dense(64, activation=tf.nn.relu))
                model.add(Dense(32, activation=tf.nn.relu))
                model.add(Dropout(0.3))
                model.add(Dense(32, activation=tf.nn.relu, kernel_regularizer=tf.keras.regularizers.l2(l=0.1)))
                model.add(Dense(3, activation=tf.nn.softmax))

                model.compile(loss='categorical_crossentropy', #optimizer=keras.optimizers.Adam(lr=0.01),
                              metrics=['accuracy'])

                model.summary()
            if self.league == 3:
                model = Sequential()
                model.add(Dense(128, activation=tf.nn.relu, input_shape=(28,)))
                model.add(Dense(128, activation=tf.nn.relu))
                model.add(Dense(64, activation=tf.nn.relu))
                model.add(Dropout(0.2))
                model.add(Dense(32, activation=tf.nn.relu, kernel_regularizer=tf.keras.regularizers.l2(l=0.1)))
                model.add(Dense(3, activation=tf.nn.softmax))

                model.compile(loss='categorical_crossentropy', #optimizer=keras.optimizers.Adam(lr=0.01),
                              metrics=['accuracy'])

                model.summary()
        elif self.alghoritm == 2:
            model = RandomForestClassifier(max_depth=4, max_leaf_nodes=10, min_samples_leaf=2, n_estimators=50)

        elif self.alghoritm == 3:
            model = LogisticRegression(multi_class="multinomial", max_iter=10000)

        self.model = model
        return self.model

    def train_model(self):
        self.upcoming_games = self.data_table.loc[self.data_table['Time'].notnull()].reset_index(drop=True)

        self.data_table = self.data_table[self.data_table['Time'].isnull()]
        self.data_table = self.data_table[self.train_columns]

        """
        correlations = self.data_table.corr()

        figure = plt.figure(figsize=(10, 10))
        subplot = figure.add_subplot(111)
        subplot.grid(False)

        figure.colorbar(subplot.matshow(correlations, interpolation="nearest", cmap=cm.get_cmap('jet', 20), vmin=-1, vmax=1))
        ticks = np.arange(len(self.data_table.columns))
        subplot.set_xticks(ticks)
        subplot.set_yticks(ticks)
        subplot.set_xticklabels(self.data_table.columns)
        subplot.set_yticklabels(self.data_table.columns)
        subplot.tick_params(axis='both', which='major', labelsize=12)
        subplot.set_xticklabels(subplot.xaxis.get_majorticklabels(), rotation=90)
        plt.savefig('main/static/correlations.png')
        """

        X = self.data_table.drop(['Winner'], axis=1)
        y = self.data_table['Winner']

        X_train = X.loc[:1139]
        X_test = X.loc[1140:]
        y_train = y.loc[:1139]
        y_test = y.loc[1140:]

        """
        params = {
            'n_estimators': [i for i in range(50, 250, 50)],
            "min_samples_leaf": [i for i in range(1, 3, 1)],
            "max_leaf_nodes": [i for i in range(10, 40, 10)],
            "max_depth": [4,5,6],
            "min_samples_split": [1,2, 3]
        }
        grid_cv = GridSearchCV(self.model, param_grid=params, cv=10, n_jobs=-1)
        grid_cv.fit(X_train, y_train)

        print(grid_cv.best_params_)
        print(grid_cv.best_score_)
        """

        if self.alghoritm == 1:
            y_train = to_categorical(y_train, 3)
            y_test = to_categorical(y_test, 3)

            self.model.fit(X_train, y_train, epochs=20, shuffle=False, batch_size=32, validation_data=(X_test, y_test))

            """
            history = self.model.fit(X_train, y_train, epochs=20, shuffle=False, batch_size=32, validation_data=(X_test, y_test))

            fig, ax = plt.subplots()
            ax.plot(range(1, 21), history.history['accuracy'], label='Dokładność trenowania')
            ax.plot(range(1, 21), history.history['val_accuracy'], label='Dokładność walidacji')
            ax.legend(loc='best')
            ax.set(xlabel='epochs', ylabel='accuracy')
            plt.savefig('main/static/train_validation.png')
            """

        elif self.alghoritm == 2:
            self.model.fit(X_train, y_train)
            score = self.model.score(X_train, y_train)
            print("Dokładność trenowania: ", score)
            score = self.model.score(X_test, y_test)
            print("Dokładność walidacji: ", score)
            """
            from sklearn.tree import export_graphviz

            tree_small = self.model.estimators_[5]

            feature_list = list(X_train.columns)
            export_graphviz(tree_small, out_file='small_tree.dot', feature_names=feature_list, rounded=True,
                            precision=1)
            """
        elif self.alghoritm == 3:
            self.model.fit(X_train, y_train)
            score = self.model.score(X_train, y_train)
            print("Dokładność trenowania: ", score)
            score = self.model.score(X_test, y_test)
            print("Dokładność walidacji: ", score)

    #   self.upcoming_games.to_csv(r'main/static/upcoming_games.csv', index=False, header=True)

    def predict(self):
        X_pred = self.upcoming_games[self.train_columns].drop(['Winner'], axis=1)
        X_pred = np.asarray(X_pred).astype(np.float32)

        if self.alghoritm == 1:
            self.upcoming_games['Bet_home_win'] = 1 / self.model.predict(X_pred)[:, 1]
            self.upcoming_games['Bet_draw'] = 1 / self.model.predict(X_pred)[:, 0]
            self.upcoming_games['Bet_away_win'] = 1 / self.model.predict(X_pred)[:, 2]
        elif self.alghoritm == 2:
            self.upcoming_games['Bet_home_win'] = 1 / self.model.predict_proba(X_pred)[:, 1]
            self.upcoming_games['Bet_draw'] = 1 / self.model.predict_proba(X_pred)[:, 0]
            self.upcoming_games['Bet_away_win'] = 1 / self.model.predict_proba(X_pred)[:, 2]
        elif self.alghoritm == 3:
            self.upcoming_games['Bet_home_win'] = 1 / self.model.predict_proba(X_pred)[:, 1]
            self.upcoming_games['Bet_draw'] = 1 / self.model.predict_proba(X_pred)[:, 0]
            self.upcoming_games['Bet_away_win'] = 1 / self.model.predict_proba(X_pred)[:, 2]

        print(self.upcoming_games[['HomeTeam',
                                   'AwayTeam',
                                   'Bet_home_win',
                                   'Bet_draw',
                                   'Bet_away_win']])
        return self.upcoming_games


"""
if __name__ == "__main__":
    # d = Prediction(0, load = True, save = False)
    # d.predict()

    d = Prediction(1, 3)
    d.train_model()
    d.predict()
"""