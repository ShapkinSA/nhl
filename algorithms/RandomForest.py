import csv
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import numpy as np
from sklearn.model_selection import train_test_split
from logs.CustomLogger import CustomLogger

class RandomForest:

    def createObjByArgs(args):
        return RandomForest(args[0],
                            args[1],
                            args[2]["test_size"], args[2]["scale"], args[2]["n_estimators"], args[2]["max_depth"], args[2]["suffle"])

    def __init__(self, team_names, player_names, test_size, need_scale, n_estimators, max_depth, shuffle):
        self.team_names = team_names
        self.player_names = player_names
        self.test_size = float(test_size)
        self.need_scale = eval(need_scale)
        self.n_estimators = int(n_estimators)
        self.max_depth = int(max_depth)
        self.shuffle = eval(shuffle)
        self.logger = CustomLogger().getLogger(type(self).__name__)

        self.logger.info(f"Алгоритм случайного леса")
        self.logger.info(f"Количество деревьев {self.n_estimators}")
        self.logger.info(f"Максимальная глубина деревьев {self.max_depth}")
        self.logger.info(f"Размер тестовой выборки {self.test_size}")
        self.logger.info(f"Масштабирование признаков {self.need_scale}")
        self.logger.info(f"Перемешивание данных (shuffle) {self.shuffle}")


    def setCalculator(self, calculator):

        self.calculator = calculator

        # Запонимаем ключевые данные для прогноза
        self.calculator.afterInit(self.team_names, self.player_names)

        # Обучаем модель
        self.fitNetwork()

    def fitNetwork(self):

        # Данные для обучения модели
        x_data, y_data = self.read_from_file()

        # Размер первого слоя
        self.EmptyArray = np.zeros((1, len(x_data[0])))

        # Потребность в масштабировании данных
        if (self.need_scale):
            x_data, y_data = self.scale_data(x_data, y_data)

        X_train, X_val, Y_train, Y_val = self.form_data(x_data, y_data, self.shuffle)

        self.logger.info(f"Начало процесса обучения модели")

        #Модель дерева
        self.model = RandomForestClassifier(n_estimators=self.n_estimators, max_depth = self.max_depth)
        self.model.fit(X_train, Y_train.ravel())

        self.show_results(X_train, Y_train, X_val, Y_val)



    #Формирует тестовую и валидационную выборку.
    def form_data(self,x_data, y_data, shuffle):
        return train_test_split(x_data, y_data, test_size=self.test_size,shuffle=shuffle)

    #Масштабирует входные данные
    def scale_data(self,x_data,y_data):
        # self.SCALER = MinMaxScaler()
        self.SCALER = StandardScaler()
        x_data = self.SCALER.fit_transform(x_data)
        return x_data,y_data


    def read_from_file(self):
        x = []
        y = []

        # with open("network_data.csv", newline='', encoding="utf-8") as File:
        with open(self.calculator.pathToNetworkData, newline='', encoding="utf-8") as File:
            reader = csv.reader(File)

            for row in reader:
                row = list(np.float_(row))
                x_row = row[:len(row) - 1]
                y_row = row[len(row) - 1]

                x.append(x_row)
                y.append(y_row)


        return np.asarray(x).reshape((len(x), len(row) - 1)), np.asarray(y).reshape((len(y), 1))

    # Демонстрация результатов работоспособности модели
    def show_results(self, X_train, Y_train, X_val, Y_val):

        # Проверка модели на обучающей выборке
        y_train = self.model.predict(X_train)

        # Проверка модели на валидационной выборке
        ynew = self.model.predict(X_val)

        self.logger.info("Точность модели на обучающей выборке = {}".format(accuracy_score(Y_train, y_train)))
        self.logger.info("Точность модели на валидационной выборке = {}".format(accuracy_score(Y_val, ynew)))

    # Предсказывание по обученной модели
    def predict_match(self, match):
        # Получение статитики для данной игры
        X_val = self.calculator.getStatisticsForOneMatch(match)

        if ((X_val == self.EmptyArray).all()):
            return None

        # Масштабирование признаков
        X_val_scale = self.SCALER.transform(X_val)

        return self.model.predict(X_val_scale)


    def show_prediction(self,prediction,dCoef1,dCoefX,dCoef2):
        #Вероятность
        prob = float(prediction)
        pr = "Вероятность отсутствует"
        if (prob==0):
            return "Прогноз : П1",dCoef1, pr
        elif (prob==1):
            return "Прогноз : Н", dCoefX, pr
        else:
            return "Прогноз : П2",dCoef2, pr



