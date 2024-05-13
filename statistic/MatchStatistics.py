from statistic.SideStatistics import SideStatistics
class MatchStatistics:

    @staticmethod
    def getFeaturesSize():

        ss = SideStatistics(0,0,0,0,0)

        p1_stats = {'home': ss.getZeroInit(), 'away': ss.getZeroInit()}
        p2_stats = {'home': ss.getZeroInit(), 'away': ss.getZeroInit()}

        personal_stats_1 = {'home': ss.getZeroInit(), 'away': ss.getZeroInit()}
        personal_stats_2 = {'home': ss.getZeroInit(), 'away': ss.getZeroInit()}

        return len(MatchStatistics.getArrayAttributes(p1_stats, p2_stats, personal_stats_1,personal_stats_2))

    @staticmethod
    def zeroSidesStatistic():
        ss = SideStatistics(0, 0, 0, 0, 0)
        return {'home': ss.getZeroInit(), 'away': ss.getZeroInit()}


    @staticmethod
    def getArrayAttributes(p1_stats, p2_stats, personal_stats_1, personal_stats_2):

        return [

            # p1_stats
            p1_stats["home"].counter_draw,
            p1_stats["home"].counter_lose,
            p1_stats["home"].counter_missing_goals,
            p1_stats["home"].counter_score_goals,
            p1_stats["home"].counter_win,

            p1_stats["away"].counter_draw,
            p1_stats["away"].counter_lose,
            p1_stats["away"].counter_missing_goals,
            p1_stats["away"].counter_score_goals,
            p1_stats["away"].counter_win,

            # p2_stats
            p2_stats["home"].counter_draw,
            p2_stats["home"].counter_lose,
            p2_stats["home"].counter_missing_goals,
            p2_stats["home"].counter_score_goals,
            p2_stats["home"].counter_win,

            p2_stats["away"].counter_draw,
            p2_stats["away"].counter_lose,
            p2_stats["away"].counter_missing_goals,
            p2_stats["away"].counter_score_goals,
            p2_stats["away"].counter_win,

            ########################################

            #p1_stats_team
            personal_stats_1["home"].counter_draw,
            personal_stats_1["home"].counter_lose,
            personal_stats_1["home"].counter_missing_goals,
            personal_stats_1["home"].counter_score_goals,
            personal_stats_1["home"].counter_win,

            personal_stats_1["away"].counter_draw,
            personal_stats_1["away"].counter_lose,
            personal_stats_1["away"].counter_missing_goals,
            personal_stats_1["away"].counter_score_goals,
            personal_stats_1["away"].counter_win,

            # p2_stats_team
            personal_stats_2["home"].counter_draw,
            personal_stats_2["home"].counter_lose,
            personal_stats_2["home"].counter_missing_goals,
            personal_stats_2["home"].counter_score_goals,
            personal_stats_2["home"].counter_win,

            personal_stats_2["away"].counter_draw,
            personal_stats_2["away"].counter_lose,
            personal_stats_2["away"].counter_missing_goals,
            personal_stats_2["away"].counter_score_goals,
            personal_stats_2["away"].counter_win,

                 ]












