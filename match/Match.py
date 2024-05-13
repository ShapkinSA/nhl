from datetime import datetime

class Match:
    def __init__(self, date, team_1, score_1, score_2, team_2, isOvertime):
        if(date==""):
            return
        self.date = date
        self.date_string = datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
        self.team_1 = team_1
        self.score_1 = score_1
        self.score_2 = score_2
        self.team_2 = team_2

        #TODO
        """
            1 - win 
            2 - draw
            3 - lose
        """

        if(isOvertime==True):
            self.result = 1
        else:
            if (score_1>score_2):
                self.result = 1
            else:
                self.result = 3



        #TODO
        """
            1 - win h
            2 - lose h
            3 - win h in OT
            4 - lose h in OT
        """

        # if(isOvertime==False):
        #     if (score_1>score_2):
        #         self.result = 1
        #     else:
        #         self.result = 2
        # else:
        #     if (score_1>score_2):
        #         self.result = 3
        #     else:
        #         self.result = 4


    def __str__(self):
        if (self.result==1):
            return f"{self.date_string} После ОТ {self.team_1} {self.score_1}:{self.score_2} {self.team_2} "
        else:
            return f"{self.date_string} {self.team_1} {self.score_1}:{self.score_2} {self.team_2} "


    def __eq__(self, other):
        """Overrides the default implementation"""
        return self.__str__()==other.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def getRowFromMatch(self):
        return [self.date_string,  self.team_1, self.score_1, self.score_2, self.team_2, self.result]

    @staticmethod
    def getMatchFromFile(date_string, team_1, score_1, score_2, team_2, result):
        match = Match("","","","","","")
        match.date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        match.date_string = date_string
        match.team_1 = team_1
        match.score_1 = int(score_1)
        match.score_2 = int(score_2)
        match.team_2 = team_2
        match.result = int(result)
        return match