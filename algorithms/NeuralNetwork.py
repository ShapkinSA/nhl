import keras.utils
from sklearn.preprocessing import MinMaxScaler, MaxAbsScaler, StandardScaler
from tensorflow.keras.models import Sequential
import numpy as np
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from tensorflow.python.keras import regularizers

from logs.CustomLogger import CustomLogger
from sklearn.metrics import accuracy_score

class NeuralNetwork:


    def createObjByArgs(args):
        return NeuralNetwork(args[0]["test_size"], args[0]["scale"], args[0]["epohs"], args[0]["batch_size"], args[0]["loss_function"], args[0]["optimizator"], ['accuracy'], args[0]["suffle"],
                             args[1])

    def __init__(self, test_size, need_scale, epochs, batch_size, type_loss_function, optimizer, metrics, shuffle, calculator):
        self.test_size = float(test_size)
        self.need_scale = eval(need_scale)
        self.epochs = int(epochs)
        self.batch_size = int(batch_size)
        self.type_loss_function = type_loss_function
        self.optimizer = optimizer
        self.metrics = metrics
        self.shuffle = eval(shuffle)
        self.calculator = calculator
        self.date_time_string_format = "%Y-%m-%d %H:%M:%S"
        self.logger = CustomLogger().getLogger(type(self).__name__)

        #Запонимаем ключевые данные для прогноза
        self.calculator.afterInit()

        #Обучаем модель
        self.fitNetwork()

        #Информация о встроенном предикате
        # self.predictor_algorithm.showPredicateInfo()


    def fitNetwork(self):

        # Данные для обучения модели
        x_data, y_data = self.calculator.read_network_data_from_file()

        # Размер первого слоя
        size_window = len(x_data[0])

        # Размер первого слоя
        self.EmptyArray = np.zeros((1, len(x_data[0])))

        #Количество возможных исходов
        number = np.unique(y_data).size


        # Потребность в масштабировании данных
        if (self.need_scale):
            x_data, y_data = self.scale_data(x_data, y_data)

        X_train, X_val, Y_train, Y_val = self.form_data(x_data, y_data)


        #Преобразование ответов
        Y_train = keras.utils.to_categorical(Y_train,number)
        Y_val = keras.utils.to_categorical(Y_val,number)

        y_data = keras.utils.to_categorical(y_data,number)

        # Модель персептрона
        self.model = Sequential()
        # self.model.add(Dense(size_window, activation='sigmoid', input_shape=[size_window],  kernel_regularizer=regularizers.L1L2(l1=1e-3, l2=1e-3)))
        # self.model.add(Dense(size_window,    activation='relu', input_shape=[size_window], kernel_regularizer=regularizers.L1L2(l1=0, l2=1e-2)  ))

        self.model.add(Dense(size_window,    activation='relu', input_shape=[size_window],  kernel_regularizer=regularizers.L1L2(l1=0, l2=1e-3 )))
        self.model.add(Dense(size_window//2, activation='relu', input_shape=[size_window],  kernel_regularizer=regularizers.L1L2(l1=0, l2=1e-3 )))
        self.model.add(Dense(size_window//4, activation='relu', input_shape=[size_window],  kernel_regularizer=regularizers.L1L2(l1=0, l2=1e-3 )))
        self.model.add(Dense(size_window//6, activation='relu', input_shape=[size_window],  kernel_regularizer=regularizers.L1L2(l1=0, l2=1e-3 )))
        self.model.add(Dense(size_window//8, activation='relu', input_shape=[size_window],  kernel_regularizer=regularizers.L1L2(l1=0, l2=1e-3 )))


        # self.model.add(Dense(size_window//4, activation='tanh'))
        # self.model.add(Dense(size_window, activation='sigmoid'))
        # self.model.add(Dense(size_output, input_shape=[size_window]))
        # self.model.add(Dense(size_output, activation='sigmoid'))
        # self.model.add(Dense(size_output, activation='sigmoid'))
        self.model.add(Dense(number, activation='softmax'))
        self.model.summary()
        self.show_results(X_train, X_val, Y_train,Y_val)


    #Формирует тестовую и валидационную выборку.
    def form_data(self,x_data, y_data):
        return train_test_split(x_data, y_data, test_size=self.test_size, shuffle=self.shuffle)

    #Масштабирует входные данные
    def scale_data(self,x_data,y_data):
        # self.scaler = MinMaxScaler()
        # self.scaler = MaxAbsScaler()
        self.scaler = StandardScaler()

        x_data = self.scaler.fit_transform(x_data)
        return x_data,y_data

    #Демонстрация результатов работоспособности модели
    def show_results(self, X_train, X_val, Y_train,Y_val):

        self.model.compile(loss=self.type_loss_function, optimizer=self.optimizer, metrics=self.metrics)

        history = self.model.fit(X_train, Y_train, validation_data=(X_val, Y_val), epochs=self.epochs, batch_size=self.batch_size, verbose=2)

        # Проверка модели на обучающей выборке
        y_train = self.model.predict(X_train)
        y_val = self.model.predict(X_val)

        # Изменение размерности вектора
        Y_train_1 = np.argmax(Y_train, axis=1)
        y_train_1 = np.argmax(y_train, axis=1)

        Y_val_1 = np.argmax(Y_val, axis=1)
        y_val_1 = np.argmax(y_val, axis=1)

        self.logger.info("Точность модели на обучающей выборке = {}".format(accuracy_score(Y_train_1, y_train_1)))
        self.logger.info("Точность модели на валидационной выборке = {}".format(accuracy_score(Y_val_1, y_val_1)))


    #Предсказывание по обученной модели
    def predict_match(self, matchToPredict):

        match = matchToPredict.getMatch()

        #Получение статитики для данной игры
        X_val = self.calculator.getStatisticsForOneMatch(match)

        if(X_val is None):
            return None

        #Масштабирование признаков
        X_val_scale = self.scaler.transform(X_val)

        self.pred_prob = self.model.predict(X_val_scale)

        #Определение предсказания на основании коэффициентов и вероятностей игры
        pred = self.predictor_algorithm.predictByProbabilityAndCoefficients(match, self.pred_prob)

        return pred



    def show_prediction(self,prediction,dCoef1,dCoefX,dCoef2):
        #Предстказание
        prob = int(prediction)

        if (prob==0):
            return "Прогноз : П1",dCoef1, "Вероятности всех прогнозов П1:" + "{:.3f}".format(round(self.pred_prob[0,0], 3))+" Н:"+"{:.3f}".format(round(self.pred_prob[0,1], 3))+" П2:"+"{:.3f}".format(round(self.pred_prob[0,2], 3))
        elif (prob==1):
            return "Прогноз : Н", dCoefX, "Вероятности всех прогнозов П1:" + "{:.3f}".format(round(self.pred_prob[0,0], 3))+" Н:"+"{:.3f}".format(round(self.pred_prob[0,1], 3))+" П2:"+"{:.3f}".format(round(self.pred_prob[0,2], 3))
        else:
            return "Прогноз : П2",dCoef2, "Вероятности всех прогнозов П1:" + "{:.3f}".format(round(self.pred_prob[0,0], 3))+" Н:"+"{:.3f}".format(round(self.pred_prob[0,1], 3))+" П2:"+"{:.3f}".format(round(self.pred_prob[0,2], 3))


