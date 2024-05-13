"""
    Формирование статистики по каждой игре для алгоритма обучения
"""
import csv
import pickle
import numpy as np
from dateutil.relativedelta import relativedelta
from pyxtension.streams import stream
from logs.CustomLogger import CustomLogger
from match.Match import Match
from statistic.MatchStatistics import MatchStatistics
from statistic.SideStatistics import SideStatistics
class StatisticsCalculatorOne:

    x_size = -100

    def createObjByArgs(args):
        return StatisticsCalculatorOne(args[0],args[1], stream(args[2]["daysWindowSize"].split(",")).map(lambda x: int(x)).toList())

    def __init__(self, pathToSiteData, pathToNetworkData, matchesWindowSize):
        self.pathToSiteData = pathToSiteData
        self.matchesWindowSize = matchesWindowSize
        self.pathToNetworkData = pathToNetworkData
        self.logger = CustomLogger().getLogger(type(self).__name__)
        self.all_teams_stats = dict()
        self.matches_with_data = dict()
        self.group_keys_dict = dict()
        self.last_windows_stats = None
        self.features_size = 0
        self.rez_len_features_size = 0

        #Длина окна для заполнения статистики
        self.statsTimeFrame = stream(matchesWindowSize).map(lambda x: relativedelta(days=x)).toList()

        if (StatisticsCalculatorOne.x_size == -100):
            self.features_size = MatchStatistics.getFeaturesSize() + 2
            self.rez_len_features_size = MatchStatistics.getFeaturesSize() * len(self.statsTimeFrame) + 2
            self.logger.info(f"Количество анализируемых признаков { self.rez_len_features_size}")


    def afterInit(self):
        # Получение всех игр из файла с их результатами
        self.all_matches = self.read_all_matches_from_file()
        self.teams = self.getAllTeams(self.all_matches)

        #Выделение окон для лайва (последние матчи для каждого окна)
        #Фиксируем время последней игры
        if(self.last_windows_stats==None):

            #Достаём нужный JSON в соответствие с количетвом признаков и составом окон
            daysWindowSize_str = str(self.matchesWindowSize[0])
            for i in range(1, len(self.matchesWindowSize)):
                daysWindowSize_str += " " + str(self.matchesWindowSize[i])

            with open(f"json {self.rez_len_features_size} {daysWindowSize_str}.txt", 'rb') as f:
                self.last_windows_stats = pickle.load(f)


    def getStatisticsForOneMatch(self, match):
        return self.getStatisticsByOneGame(match, self.teams, self.players)

    def getStatisticsForAllMatchesFromFile(self):

        # Получение всех игр из файла с их результатами
        matches = self.read_all_matches_from_file()

        teams = self.getAllTeams(matches)
        players = self.getAllPlayers(matches)

        x = np.zeros((len(matches), self.rez_len_features_size))
        y = np.zeros((len(matches),))

        self.logger.info(f"Количество матчей для обработки: {len(matches)}")

        # Формируем информацию для статистики
        self.getPreStatistics(matches)

        # Рассчитываем статистику для каждой игры
        for i in range(len(self.group_keys_dict[self.daysWindowSize[0]][matches[0].date])):
            x[i] = np.zeros( self.rez_len_features_size)

        match_ind_count = i+1

        current_stat = dict()
        for i in range(0, len(self.daysWindowSize)):
            current_stat[self.daysWindowSize[i]] = dict()

        current_time_group = ""

        for i in range(match_ind_count, len(matches)):
            #Находим первую игру группы матчей. Если её дата не изменилась по сравнению с прошлой итерацией - дублируем статистику
            if(current_time_group != self.group_keys_dict[self.daysWindowSize[0]][matches[i].date][0]):
                current_stat = self.getPreStatisticsCalculatedByOneFrame(current_stat, matches[i].date)
                current_time_group = self.group_keys_dict[self.daysWindowSize[0]][matches[i].date][0]

            #Переводим статистику в признаки
            x[i] = self.getStatistics(current_stat, matches[i], teams, players)

            #Фиксируем результат игры
            y[i] = matches[i].result

        #Фиксируем последние окна (для мониторинга в онлайне)
        self.last_windows_stats = current_stat

        #Запись статистики последнего окна в файл
        self.rec_last_window_stats()

        return x, y

    def read_all_matches_from_file(self):
        matches = []
        with open(self.pathToSiteData, newline='', encoding='utf-8') as File:
            reader = csv.reader(File)
            for row in reader:
                match = Match.getMatchFromFile(row[0],row[1],row[2],row[3],row[4],row[5])
                matches.append(match)
        #Сортируем список матчей
        matches = sorted(matches,key=lambda x: x.date)

        return matches

    def getAllTeams(self,matches):

        teams_map = {}
        # Количество команд
        team_turple_team_1 = stream(matches).map(lambda x: x.team_1).toList()
        team_turple_team_2 = stream(matches).map(lambda x: x.team_2).toList()

        team_turple = team_turple_team_1 + team_turple_team_2

        count = 0

        for team in team_turple:
            if (teams_map.get(team) == None):
                teams_map[team] = count
                count += 1

        return teams_map

    def correctStats(self, old_stats, tmp_stats, operation):
        if(operation=="+"):
            old_stats["home"].counter_win = old_stats["home"].counter_win + tmp_stats["home"].counter_win
            old_stats["home"].counter_draw = old_stats["home"].counter_draw + tmp_stats["home"].counter_draw
            old_stats["home"].counter_lose = old_stats["home"].counter_lose + tmp_stats["home"].counter_lose
            old_stats["home"].counter_score_goals = old_stats["home"].counter_score_goals + tmp_stats["home"].counter_score_goals
            old_stats["home"].counter_missing_goals = old_stats["home"].counter_missing_goals + tmp_stats["home"].counter_missing_goals

            old_stats["away"].counter_win = old_stats["away"].counter_win + tmp_stats["away"].counter_win
            old_stats["away"].counter_draw = old_stats["away"].counter_draw + tmp_stats["away"].counter_draw
            old_stats["away"].counter_lose = old_stats["away"].counter_lose + tmp_stats["away"].counter_lose
            old_stats["away"].counter_score_goals = old_stats["away"].counter_score_goals + tmp_stats["away"].counter_score_goals
            old_stats["away"].counter_missing_goals = old_stats["away"].counter_missing_goals + tmp_stats["away"].counter_missing_goals
        else:
            old_stats["home"].counter_win = old_stats["home"].counter_win - tmp_stats["home"].counter_win
            old_stats["home"].counter_draw = old_stats["home"].counter_draw - tmp_stats["home"].counter_draw
            old_stats["home"].counter_lose = old_stats["home"].counter_lose - tmp_stats["home"].counter_lose
            old_stats["home"].counter_score_goals = old_stats["home"].counter_score_goals - tmp_stats["home"].counter_score_goals
            old_stats["home"].counter_missing_goals = old_stats["home"].counter_missing_goals - tmp_stats["home"].counter_missing_goals

            old_stats["away"].counter_win = old_stats["away"].counter_win - tmp_stats["away"].counter_win
            old_stats["away"].counter_draw = old_stats["away"].counter_draw - tmp_stats["away"].counter_draw
            old_stats["away"].counter_lose = old_stats["away"].counter_lose - tmp_stats["away"].counter_lose
            old_stats["away"].counter_score_goals = old_stats["away"].counter_score_goals - tmp_stats["away"].counter_score_goals
            old_stats["away"].counter_missing_goals = old_stats["away"].counter_missing_goals - tmp_stats["away"].counter_missing_goals

        return old_stats

    def correctSideStatistics(self, old_stats, tmp_stats, operation):
        if (operation == "+"):
            old_stats.counter_win = old_stats.counter_win + tmp_stats.counter_win
            old_stats.counter_draw = old_stats.counter_draw + tmp_stats.counter_draw
            old_stats.counter_lose = old_stats.counter_lose + tmp_stats.counter_lose
            old_stats.counter_score_goals = old_stats.counter_score_goals + tmp_stats.counter_score_goals
            old_stats.counter_missing_goals = old_stats.counter_missing_goals + tmp_stats.counter_missing_goals
        else:
            old_stats.counter_win = old_stats.counter_win - tmp_stats.counter_win
            old_stats.counter_draw = old_stats.counter_draw - tmp_stats.counter_draw
            old_stats.counter_lose = old_stats.counter_lose - tmp_stats.counter_lose
            old_stats.counter_score_goals = old_stats.counter_score_goals - tmp_stats.counter_score_goals
            old_stats.counter_missing_goals = old_stats.counter_missing_goals - tmp_stats.counter_missing_goals
        return old_stats

    def addGameToStatistics(self, new_matches, new_stats):

        stats_tmp = dict()
        for match in new_matches:
            stats_tmp = self.getPreStatisticsByOneGame(match,stats_tmp)

        for new_key in stats_tmp:

            # Если статистики с такими игроками нету, то просто из добавляем
            if(new_stats.get(  new_key  ) == None):
                new_stats[new_key] = stats_tmp[new_key]
            else:

                #Корректируем stats
                new_stats[new_key]["stats"] = self.correctStats(new_stats[new_key]["stats"],stats_tmp[new_key]["stats"], "+")

                # Корректируем stats_team
                for team in stats_tmp[new_key]["stats_team"]:
                    if(new_stats[new_key]["stats_team"].get(  team  )==None):
                        new_stats[new_key]["stats_team"][team] = stats_tmp[new_key]["stats_team"][team].copy()
                    else:
                        new_stats[new_key]["stats_team"][team] = self.correctStats(new_stats[new_key]["stats_team"][team], stats_tmp[new_key]["stats_team"][team], "+")

                # Корректируем personal_stats_player_teams_without_side
                for enemy in stats_tmp[new_key]["personal_stats_player_teams_without_side"]:

                    if (new_stats[new_key]["personal_stats_player_teams_without_side"].get(enemy) == None):
                        new_stats[new_key]["personal_stats_player_teams_without_side"][enemy] = stats_tmp[new_key]["personal_stats_player_teams_without_side"][enemy].copy()
                    else:

                        for personal_game in stats_tmp[new_key]["personal_stats_player_teams_without_side"][enemy]:

                            if (new_stats[new_key]["personal_stats_player_teams_without_side"][enemy].get(  personal_game  )!=None):

                                new_stats[new_key]["personal_stats_player_teams_without_side"][enemy][personal_game] = \
                                    self.correctStats(new_stats[new_key]["personal_stats_player_teams_without_side"][enemy][personal_game], stats_tmp[new_key]["personal_stats_player_teams_without_side"][enemy][personal_game], "+")

                            #Добавляем в личные встречи новую сигнатуру этих игроков
                            else:
                                new_stats[new_key]["personal_stats_player_teams_without_side"][enemy][personal_game] = stats_tmp[new_key]["personal_stats_player_teams_without_side"][enemy][personal_game]


                # Корректируем personal_stats
                for enemy_player in stats_tmp[new_key]["personal_stats"]:

                    if(new_stats[new_key]["personal_stats"].get(enemy_player)==None):
                        new_stats[new_key]["personal_stats"][enemy_player] = stats_tmp[new_key]["personal_stats"][enemy_player].copy()

                    else:

                        new_stats[new_key]["personal_stats"][enemy_player] = self.correctStats(new_stats[new_key]["personal_stats"][enemy_player],stats_tmp[new_key]["personal_stats"][enemy_player], "+")

                # Корректируем personal_stats_player_teams_with_side
                for enemy in stats_tmp[new_key]["personal_stats_player_teams_with_side"]:

                    if (new_stats[new_key]["personal_stats_player_teams_with_side"].get(enemy) == None):
                        new_stats[new_key]["personal_stats_player_teams_with_side"][enemy] = stats_tmp[new_key]["personal_stats_player_teams_with_side"][enemy].copy()

                    else:

                        for personal_team_game in stats_tmp[new_key]["personal_stats_player_teams_with_side"][enemy]:

                            if (new_stats[new_key]["personal_stats_player_teams_with_side"][enemy].get(  personal_team_game  )!=None):

                                new_stats[new_key]["personal_stats_player_teams_with_side"][enemy][personal_team_game] = self.correctSideStatistics(new_stats[new_key]["personal_stats_player_teams_with_side"][enemy][personal_team_game], stats_tmp[new_key]["personal_stats_player_teams_with_side"][enemy][personal_team_game], "+")

                            #Добавляем в личные встречи
                            else:
                                new_stats[new_key]["personal_stats_player_teams_with_side"][enemy][personal_team_game] = stats_tmp[new_key]["personal_stats_player_teams_with_side"][enemy][personal_team_game]

        return new_stats


    def removeGameToStatistics(self, old_matches, new_stats):

        stats_tmp = dict()

        for match in old_matches:
            stats_tmp = self.getPreStatisticsByOneGame(match, stats_tmp)

        for new_key in stats_tmp:


            # Корректируем stats
            new_stats[new_key]["stats"] = self.correctStats(new_stats[new_key]["stats"],
                                                            stats_tmp[new_key]["stats"], "-")

            # Корректируем stats_team
            for team in stats_tmp[new_key]["stats_team"]:
                    new_stats[new_key]["stats_team"][team] = self.correctStats(
                        new_stats[new_key]["stats_team"][team], stats_tmp[new_key]["stats_team"][team], "-")

            # Корректируем personal_stats_player_teams_without_side
            for enemy in stats_tmp[new_key]["personal_stats_player_teams_without_side"]:

                for personal_game in stats_tmp[new_key]["personal_stats_player_teams_without_side"][enemy]:

                    new_stats[new_key]["personal_stats_player_teams_without_side"][enemy][personal_game] = self.correctStats(
                        new_stats[new_key]["personal_stats_player_teams_without_side"][enemy][personal_game],
                        stats_tmp[new_key]["personal_stats_player_teams_without_side"][enemy][personal_game], "-")

            # Корректируем personal_stats
            for enemy_player in stats_tmp[new_key]["personal_stats"]:
                new_stats[new_key]["personal_stats"][enemy_player] = self.correctStats(
                    new_stats[new_key]["personal_stats"][enemy_player],stats_tmp[new_key]["personal_stats"][enemy_player], "-")

            # Корректируем personal_stats_player_teams_with_side
            for enemy in stats_tmp[new_key]["personal_stats_player_teams_with_side"]:
                for personal_team_game in stats_tmp[new_key]["personal_stats_player_teams_with_side"][enemy]:

                    new_stats[new_key]["personal_stats_player_teams_with_side"][enemy][personal_team_game] = self.correctSideStatistics(
                        new_stats[new_key]["personal_stats_player_teams_with_side"][enemy][personal_team_game],
                        stats_tmp[new_key]["personal_stats_player_teams_with_side"][enemy][personal_team_game], "-")

        return new_stats

    def calcWindow(self, key_window, group_key, currentStats):

        #Находим статистику для одной из данных игр (для другой аналогично)
        key = self.group_keys_dict[key_window][group_key][0]

        # Матчи который были на прошлом интервале
        m_lost = self.matches_with_data[key_window][key]["lost"]

        # Матчи на текущем интервале
        m_apear = self.matches_with_data[key_window][key]["new"]

        # Добавляем игру в статистику
        if (len(m_apear) > 0):
            currentStats[key_window] = self.addGameToStatistics(m_apear, currentStats[key_window])
        # Добавляем пустую статистику
        else:
            currentStats[key_window] = dict()

        # Удаляем игру из статистики
        if (len(m_lost) > 0 and len(m_apear) > 0):
            self.removeGameToStatistics(m_lost, currentStats[key_window])


    def getPreStatisticsCalculatedByOneFrame(self, current_stat, group_key):
        # Итерируемся по количеству временных окон
        for n in range(len(self.statsTimeFrame)):
            self.calcWindow(self.daysWindowSize[n],group_key, current_stat)
        return current_stat

    def getPreStatistics(self, allMatches):

        self.logger.info("Начало процесса формирования окон матчей со статистикой")

        #Итерируемся по количеству временных окон
        for n in range (len(self.statsTimeFrame)):

            matches_with_data = dict()

            windowMatches = dict()
            windowGames = []

            #Левая граница окна (индекс)
            ind_left = 0

            for i in range(0,len(allMatches)):

                #Временные рамки
                time_shift = allMatches[i].date_datetime - self.statsTimeFrame[n]

                #Проверка на уже заполненную информацию
                windowGames_copy = windowGames.copy()

                if(i>0 and allMatches[i-1].date_datetime == allMatches[i].date_datetime):
                    matches_with_data[allMatches[i].__str__()] = matches_with_data[allMatches[i-1].__str__()]
                    continue

                lost_matches = []
                append_matches = []

                for k in range(len(windowGames_copy)):
                    # if(windowMatches_copy[k].date_datetime < (allMatches[i].date_datetime - self.statsTimeFrame[n])):
                    if(windowGames_copy[k].date_datetime < time_shift):
                        # windowMatches.remove(windowMatches_copy[k])
                        if (windowGames.count(windowGames_copy[k]) != 0):
                            lost_matches.append(windowGames_copy[k])
                            windowGames.remove(windowGames_copy[k])
                    else:
                        break


                #Заполнение
                for j in range(ind_left,i):

                    if(allMatches[j].date_datetime > time_shift and matches_with_data[allMatches[i-1].__str__()]["new"].count(allMatches[j])==0):
                        append_matches = allMatches[j:i]
                        windowGames.extend(append_matches)
                        ind_left = j
                        break

                windowMatches["lost"] = lost_matches
                windowMatches["new"] = append_matches
                matches_with_data[allMatches[i].__str__()] = windowMatches.copy()


            keys = list(matches_with_data.keys())

            group_keys = list(stream(keys).map(lambda x: x.__str__().split("Z")[0]+"Z").toSet())
            group_keys.sort()
            group_keys_dict = dict()
            count_key = 0
            for group_key in group_keys:
                matchList = []

                for i in range (count_key,len(keys)):
                    if(group_key in keys[i]):
                        matchList.append(keys[i])
                    else:
                        count_key = i
                        group_keys_dict[group_key] = matchList.copy()
                        break

            group_keys_dict[group_key] = matchList.copy()

            self.matches_with_data[self.daysWindowSize[n]] = matches_with_data
            self.group_keys_dict[self.daysWindowSize[n]] = group_keys_dict


    def getStatistics(self,current_stat, match, teams, players):

        #Количество признаков в одном окне
        size_w = self.features_size - Match.getParametersLength()

        #Статистика для каждой длины окна интервала наблюдения конкатенируется
        rez = np.zeros((len(self.daysWindowSize), size_w))

        #Статистика игры по онлайн стате + названия игроков и команд
        match_stats_array = match.getAllParametersVector(players, teams)

        for i in range(len(self.daysWindowSize)):

            #Статистика для конкретного временного среза
            all_players_stats = current_stat[self.daysWindowSize[i]]

            #Проверяем на наличике статистики для этих двух игроков
            if(all_players_stats.get(match.player_1) == None or all_players_stats.get(match.player_2) == None):
                continue

            #Статистика первого и второго игрока
            p1 = all_players_stats[match.player_1]
            p2 = all_players_stats[match.player_2]

            #Проверка на наличие данных в статистике
            p1_stats_team_match_team_1 = p1["stats_team"][match.team_1] if p1["stats_team"].get(match.team_1)!= None else MatchStatistics.zeroSidesStatistic()
            p2_stats_team_match_team_2 = p2["stats_team"][match.team_2] if p2["stats_team"].get(match.team_2)!= None else MatchStatistics.zeroSidesStatistic()

            p1_personal_stats_match_player_2 = p1["personal_stats"][match.player_2] if p1["personal_stats"].get(match.player_2)!= None else MatchStatistics.zeroSidesStatistic()
            p2_personal_stats_match_player_1 = p2["personal_stats"][match.player_1] if p2["personal_stats"].get(match.player_1)!= None else MatchStatistics.zeroSidesStatistic()


            #Личные встречи фиксированных команд без привязки к стороне
            p1_personal_stats_player_teams_without_side = MatchStatistics.zeroSidesStatistic()
            find = False
            for key in p1["personal_stats_player_teams_without_side"].keys():
                #Находим соперника
                if(key == match.player_2):

                    #Находим игру на данных командах
                    for game in p1["personal_stats_player_teams_without_side"][key]:

                        #находим соответствующее противостояние
                        if(match.player_1 in game and match.player_2 in game and match.team_1 in game and match.team_1 in game):

                            #Достаём статистику противостояния дома
                            if(p1["personal_stats_player_teams_without_side"][key][game].get("home")!=None):
                                p1_personal_stats_player_teams_without_side['home'] = p1["personal_stats_player_teams_without_side"][key][game]["home"]

                            #Достаём статистику противостояния в гостях
                            if(p1["personal_stats_player_teams_without_side"][key][game].get("away")!=None):
                                p1_personal_stats_player_teams_without_side['away'] = p1["personal_stats_player_teams_without_side"][key][game]["away"]

                            find = True
                            break
                if(find):
                    break

            # Личные встречи фиксированных команд без привязки к стороне
            p2_personal_stats_player_teams_without_side = MatchStatistics.zeroSidesStatistic()
            find = False
            for key in p2["personal_stats_player_teams_without_side"].keys():

                # Находим соперника
                if (key == match.player_1):

                    # Находим игру на данных командах
                    for game in p2["personal_stats_player_teams_without_side"][key]:

                        # находим соответствующее противостояние
                        if (match.player_1 in game and match.player_2 in game and match.team_1 in game and match.team_1 in game):

                            # Достаём статистику противостояния дома
                            if (p2["personal_stats_player_teams_without_side"][key][game].get("home") != None):
                                p2_personal_stats_player_teams_without_side['home'] = p2["personal_stats_player_teams_without_side"][key][game]["home"]

                            # Достаём статистику противостояния в гостях
                            if (p2["personal_stats_player_teams_without_side"][key][game].get("away") != None):
                                p2_personal_stats_player_teams_without_side['away'] = p2["personal_stats_player_teams_without_side"][key][game]["away"]

                            find = True
                            break
                if (find):
                    break


            #Конкретная сигнатура матча
            gameGame = f"{match.team_1} ({match.player_1}) - {match.team_2} ({match.player_2})"

            #Личные встречи фиксированных команд без привязки к стороне
            p1_personal_stats_player_teams_with_side = SideStatistics.getZeroInit()
            find = False
            for key in p1["personal_stats_player_teams_with_side"].keys():

                #Находим соперника
                if(key == match.player_2):

                    #Находим игру на данных командах
                    for game in p1["personal_stats_player_teams_with_side"][key]:

                        #находим соответствующее противостояние
                        if(game == gameGame):

                            p1_personal_stats_player_teams_with_side = p1["personal_stats_player_teams_with_side"][key][game]

                            find = True
                            break
                if(find):
                    break

            # Личные встречи фиксированных команд без привязки к стороне
            p2_personal_stats_player_teams_with_side = SideStatistics.getZeroInit()
            find = False
            for key in p2["personal_stats_player_teams_with_side"].keys():

                # Находим соперника
                if (key == match.player_2):

                    # Находим игру на данных командах
                    for game in p2["personal_stats_player_teams_with_side"][key]:

                        # находим соответствующее противостояние
                        if (game == gameGame):
                            p1_personal_stats_player_teams_with_side = p2["personal_stats_player_teams_with_side"][key][game]

                            find = True
                            break
                if (find):
                    break


            # Формирование итоговой таблицы с признаками
            rez[i] = np.asarray(MatchStatistics.getArrayAttributes( p1["stats"],
                                                                    p2["stats"],
                                                                    p1_stats_team_match_team_1,
                                                                    p2_stats_team_match_team_2,
                                                                    p1_personal_stats_match_player_2,
                                                                    p2_personal_stats_match_player_1,
                                                                    p1_personal_stats_player_teams_without_side,
                                                                    p2_personal_stats_player_teams_without_side,
                                                                    p1_personal_stats_player_teams_with_side,
                                                                    p2_personal_stats_player_teams_with_side,
                                                                    )).reshape((1, -1))

        # Конкатенируем в один результирующий массив
        rez = np.reshape(rez, size_w * len(self.daysWindowSize))

        # Подставляем название игроков и команд
        rez = np.concatenate([match_stats_array, rez], axis = 0)

        return rez.reshape((1, -1))


    def addActualInformationAboutFinishedGames(self, match):
        #Перезаписываем статистику последних игр каждого окна (корректировка в лайве. Ка бы расширяем окно свежеполученными данными). Ключём является последняя игра из файла со статистикой
        for days in self.daysWindowSize:
            self.last_windows_stats[days] = self.addGameToStatistics(match, self.last_windows_stats[days])


    def getStatisticsOnOneSideOneGame(self, match, side):
        if (side == "Player_1"):
            counter_win = 1 if match.score_1 > match.score_2 else 0
            counter_lose = 1 if match.score_1 < match.score_2 else 0
            counter_score_goals = match.score_1
            counter_missing_goals = match.score_2
        else:
            counter_win = 1 if match.score_1 < match.score_2 else 0
            counter_lose = 1 if match.score_1 > match.score_2 else 0
            counter_score_goals = match.score_2
            counter_missing_goals = match.score_1

        counter_draw = 1 if match.score_1 == match.score_2 else 0

        return SideStatistics(counter_win,counter_draw,counter_lose,counter_score_goals,counter_missing_goals)


    def getPreStatisticsByOneGame(self, match, currentStatistics):

        #Личная стреча двух игроков
        currentStatistics[match.player_1] = dict()
        currentStatistics[match.player_2] = dict()

        #Заполнение общей статистики
        currentStatistics[match.player_1]["stats"] = {"home": self.getStatisticsOnOneSideOneGame(match, "Player_1"), "away": SideStatistics.getZeroInit()}
        currentStatistics[match.player_2]["stats"] = {"home": SideStatistics.getZeroInit(), "away": self.getStatisticsOnOneSideOneGame(match, "Player_2")}

        #Заполнение статистики по командам
        currentStatistics[match.player_1]["stats_team"] = dict()
        currentStatistics[match.player_2]["stats_team"] = dict()

        currentStatistics[match.player_1]["stats_team"][match.team_1] = {"home": self.getStatisticsOnOneSideOneGame(match, "Player_1"), "away": SideStatistics.getZeroInit()}
        currentStatistics[match.player_2]["stats_team"][match.team_2] = {"home": SideStatistics.getZeroInit(), "away": self.getStatisticsOnOneSideOneGame(match, "Player_2")}


        #Унифицируем название игры
        universal_match_name = match.getUniversalMatchName()

        currentStatistics[match.player_1]["personal_stats_player_teams_without_side"] = dict()
        currentStatistics[match.player_2]["personal_stats_player_teams_without_side"] = dict()

        currentStatistics[match.player_1]["personal_stats_player_teams_without_side"][match.player_2] = dict()
        currentStatistics[match.player_2]["personal_stats_player_teams_without_side"][match.player_1] = dict()

        currentStatistics[match.player_1]["personal_stats_player_teams_without_side"][match.player_2][universal_match_name] = {"home": self.getStatisticsOnOneSideOneGame(match, "Player_1"), "away": SideStatistics.getZeroInit()}
        currentStatistics[match.player_2]["personal_stats_player_teams_without_side"][match.player_1][universal_match_name] = {"home": SideStatistics.getZeroInit(), "away": self.getStatisticsOnOneSideOneGame(match, "Player_2")}


        #Заполнение статистики по личным встречам с привязкой к стороне
        currentStatistics[match.player_1]["personal_stats_player_teams_with_side"] = dict()
        currentStatistics[match.player_2]["personal_stats_player_teams_with_side"] = dict()

        currentStatistics[match.player_1]["personal_stats_player_teams_with_side"][match.player_2] = dict()
        currentStatistics[match.player_2]["personal_stats_player_teams_with_side"][match.player_1] = dict()

        currentStatistics[match.player_1]["personal_stats_player_teams_with_side"][match.player_2][match.getMatchName()] = self.getStatisticsOnOneSideOneGame(match, "Player_1")
        currentStatistics[match.player_2]["personal_stats_player_teams_with_side"][match.player_1][match.getMatchName()] = self.getStatisticsOnOneSideOneGame(match, "Player_2")

        #Персональная статистика
        currentStatistics[match.player_1]["personal_stats"] = dict()
        currentStatistics[match.player_2]["personal_stats"] = dict()

        currentStatistics[match.player_1]["personal_stats"][match.player_2] = {"home": self.getStatisticsOnOneSideOneGame(match, "Player_1"), "away": SideStatistics.getZeroInit()}
        currentStatistics[match.player_2]["personal_stats"][match.player_1] = {"home": SideStatistics.getZeroInit(), "away": self.getStatisticsOnOneSideOneGame(match, "Player_2")}

        return currentStatistics

    def getStatisticsByOneGame(self,match, teams, players):

        #Количество признаков в одном окне
        size_w = self.features_size - Match.getParametersLength()

        #Статистика для каждой длины окна интервала наблюдения конкатенируется
        rez = np.zeros((len(self.daysWindowSize), size_w))

        #Статистика игры по онлайн стате + названия игроков и команд
        match_stats_array = match.getAllParametersVector(players, teams)

        #Если данного игрока нет в статистике
        if(match_stats_array is None):
            return None

        for i in range(len(self.daysWindowSize)):

            # Статистика для последнего временного среза для заданного окна
            all_players_stats = self.last_windows_stats[self.daysWindowSize[i]]

            #Статистика первого и второго игрока
            p1 = all_players_stats[match.player_1]
            p2 = all_players_stats[match.player_2]

            #Проверка на наличие данных в статистике
            p1_stats_team_match_team_1 = p1["stats_team"][match.team_1] if p1["stats_team"].get(match.team_1)!= None else MatchStatistics.zeroSidesStatistic()
            p2_stats_team_match_team_2 = p2["stats_team"][match.team_2] if p2["stats_team"].get(match.team_2)!= None else MatchStatistics.zeroSidesStatistic()

            p1_personal_stats_match_player_2 = p1["personal_stats"][match.player_2] if p1["personal_stats"].get(match.player_2)!= None else MatchStatistics.zeroSidesStatistic()
            p2_personal_stats_match_player_1 = p2["personal_stats"][match.player_1] if p2["personal_stats"].get(match.player_1)!= None else MatchStatistics.zeroSidesStatistic()


            #Личные встречи фиксированных команд без привязки к стороне
            p1_personal_stats_player_teams_without_side = MatchStatistics.zeroSidesStatistic()
            find = False
            for key in p1["personal_stats_player_teams_without_side"].keys():
                #Находим соперника
                if(key == match.player_2):

                    #Находим игру на данных командах
                    for game in p1["personal_stats_player_teams_without_side"][key]:

                        #находим соответствующее противостояние
                        if(match.player_1 in game and match.player_2 in game and match.team_1 in game and match.team_1 in game):

                            #Достаём статистику противостояния дома
                            if(p1["personal_stats_player_teams_without_side"][key][game].get("home")!=None):
                                p1_personal_stats_player_teams_without_side['home'] = p1["personal_stats_player_teams_without_side"][key][game]["home"]

                            #Достаём статистику противостояния в гостях
                            if(p1["personal_stats_player_teams_without_side"][key][game].get("away")!=None):
                                p1_personal_stats_player_teams_without_side['away'] = p1["personal_stats_player_teams_without_side"][key][game]["away"]

                            find = True
                            break
                if(find):
                    break

            # Личные встречи фиксированных команд без привязки к стороне
            p2_personal_stats_player_teams_without_side = MatchStatistics.zeroSidesStatistic()
            find = False
            for key in p2["personal_stats_player_teams_without_side"].keys():

                # Находим соперника
                if (key == match.player_1):

                    # Находим игру на данных командах
                    for game in p2["personal_stats_player_teams_without_side"][key]:

                        # находим соответствующее противостояние
                        if (match.player_1 in game and match.player_2 in game and match.team_1 in game and match.team_1 in game):

                            # Достаём статистику противостояния дома
                            if (p2["personal_stats_player_teams_without_side"][key][game].get("home") != None):
                                p2_personal_stats_player_teams_without_side['home'] = p2["personal_stats_player_teams_without_side"][key][game]["home"]

                            # Достаём статистику противостояния в гостях
                            if (p2["personal_stats_player_teams_without_side"][key][game].get("away") != None):
                                p2_personal_stats_player_teams_without_side['away'] = p2["personal_stats_player_teams_without_side"][key][game]["away"]

                            find = True
                            break
                if (find):
                    break


            #Конкретная сигнатура матча
            gameGame = f"{match.team_1} ({match.player_1}) - {match.team_2} ({match.player_2})"

            #Личные встречи фиксированных команд без привязки к стороне
            p1_personal_stats_player_teams_with_side = SideStatistics.getZeroInit()
            find = False
            for key in p1["personal_stats_player_teams_with_side"].keys():

                #Находим соперника
                if(key == match.player_2):

                    #Находим игру на данных командах
                    for game in p1["personal_stats_player_teams_with_side"][key]:

                        #находим соответствующее противостояние
                        if(game == gameGame):

                            p1_personal_stats_player_teams_with_side = p1["personal_stats_player_teams_with_side"][key][game]

                            find = True
                            break
                if(find):
                    break

            # Личные встречи фиксированных команд без привязки к стороне
            p2_personal_stats_player_teams_with_side = SideStatistics.getZeroInit()
            find = False
            for key in p2["personal_stats_player_teams_with_side"].keys():

                # Находим соперника
                if (key == match.player_2):

                    # Находим игру на данных командах
                    for game in p2["personal_stats_player_teams_with_side"][key]:

                        # находим соответствующее противостояние
                        if (game == gameGame):
                            p1_personal_stats_player_teams_with_side = p2["personal_stats_player_teams_with_side"][key][game]

                            find = True
                            break
                if (find):
                    break


            # Формирование итоговой таблицы с признаками
            rez[i] = np.asarray(MatchStatistics.getArrayAttributes( p1["stats"],
                                                                    p2["stats"],
                                                                    p1_stats_team_match_team_1,
                                                                    p2_stats_team_match_team_2,
                                                                    p1_personal_stats_match_player_2,
                                                                    p2_personal_stats_match_player_1,
                                                                    p1_personal_stats_player_teams_without_side,
                                                                    p2_personal_stats_player_teams_without_side,
                                                                    p1_personal_stats_player_teams_with_side,
                                                                    p2_personal_stats_player_teams_with_side,
                                                                    )).reshape((1, -1))

        # Конкатенируем в один результирующий массив
        rez = np.reshape(rez, size_w * len(self.daysWindowSize))

        # Подставляем название игроков и команд
        rez = np.concatenate([match_stats_array, rez], axis = 0)

        return rez.reshape((1, -1))

    def rec_last_window_stats(self):
        daysWindowSize_str = str(self.daysWindowSize[0])
        for i in range (1,len(self.daysWindowSize)):
            daysWindowSize_str += " "+str(self.daysWindowSize[i])

        with open(f"json {self.rez_len_features_size} {daysWindowSize_str}.txt", 'wb') as f:
            pickle.dump(self.last_windows_stats, f)


    def read_network_data_from_file(self):
        x = []
        y = []

        with open(self.pathToNetworkData, newline='', encoding="utf-8") as File:
            reader = csv.reader(File)

            for row in reader:
                row = list(np.float_(row))
                x_row = row[:len(row) - 1]
                y_row = row[len(row) - 1]

                x.append(x_row)
                y.append(y_row)

        return np.asarray(x).reshape((len(x), len(row) - 1)), np.asarray(y).reshape((len(y), 1))
