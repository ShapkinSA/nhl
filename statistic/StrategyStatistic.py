from logs.CustomLogger import CustomLogger
class StrategyStatistic:

    balance = 0
    balance_need = 0
    scheduler = None

    sumLive = 0
    margin = 0

    max_bet_win = 0
    max_bet_lose = 0

    win = 0
    lose = 0
    all = 0

    #Фиксируем наибольшую серию побед и поражений
    lose_streak_counter = 0
    win_streak_counter = 0

    lose_streak_counter_max = 0
    win_streak_counter_max = 0

    def __init__(self, balance, balance_need):
        self.balance = balance
        self.balance_need = balance_need
        self.isFinish = False
        self.logger = CustomLogger().getLogger(type(self).__name__)

    def onPredict(self,matchToPredict):
        #Увеличиваем сумму денег в лайве
        self.sumLive += matchToPredict.bet

        #Уменьшаем баланс
        self.balance -= matchToPredict.bet


    def onResult(self,matchToPredict, isWin):
        #Убираем сумму денег из лайва
        self.sumLive -= matchToPredict.bet

        if(isWin):
            #Фиксируем победу
            self.win += 1

            #Начинаем или продолжаем серию побед
            self.win_streak_counter += 1

            #Сбрасываем счётчик поражений
            self.lose_streak_counter = 0

            #Прирост баланса
            self.balance += matchToPredict.bet * matchToPredict.prediction_coef

            #Прибыль с каждой ставки
            self.margin += matchToPredict.bet * (matchToPredict.prediction_coef-1)

            # Фиксация самой большой выиграной ставки
            if (matchToPredict.bet > self.max_bet_win):
                self.max_bet_win = matchToPredict.bet


        else:
            #Фиксируем покажение
            self.lose += 1

            #Начинаем или продолжаем серию побед
            self.lose_streak_counter += 1

            #Сбрасываем счётчик побед
            self.win_streak_counter = 0

            #Фиксируем прибыль на данной ставке
            self.margin -= matchToPredict.bet


            # Фиксация самой большой выиграной ставки
            if (matchToPredict.bet > self.max_bet_lose):
                self.max_bet_lose = matchToPredict.bet


        #Проверка на достижение требуемого баланса
        if(self.balance>self.balance_need):
            print("\n")
            self.logger.info(f"Требуемый баланс достигнут {self.balance}")
            self.isFinish = True


        #Фиксируем окончание игры
        self.all += 1

        #Пересчитываем счётчики для серии побед и поражений
        if(self.win_streak_counter > self.win_streak_counter_max):
            self.win_streak_counter_max = self.win_streak_counter

        if (self.lose_streak_counter > self.lose_streak_counter_max):
            self.lose_streak_counter_max = self.lose_streak_counter

        return self.isFinish