class SideStatistics:

    def __init__(self, counter_win, counter_draw, counter_lose, counter_score_goals,counter_missing_goals):
        self.counter_win = counter_win
        self.counter_draw = counter_draw
        self.counter_lose = counter_lose
        self.counter_score_goals = counter_score_goals
        self.counter_missing_goals = counter_missing_goals

    @staticmethod
    def getZeroInit():
        return SideStatistics(0,0,0,0,0)





