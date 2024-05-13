"""
    Работа с сайтом статистики (Выкачивание матчей с формированием файла)
    Запись файла сформированной статистики по каждой игре для алгоритма обучения
"""
import csv
import os
from datetime import datetime
import requests
from pyxtension.streams import stream
from logs.CustomLogger import CustomLogger
import concurrent.futures
from match.Match import Match
from reflection.Reflection import Reflection

class FlashScoreSiteDownloader:

    def __init__(self, flashScoreSiteDownloader_cfg, calculator_cfg):
        self.start_year = int(flashScoreSiteDownloader_cfg["start_year"])
        self.logger = CustomLogger().getLogger(type(self).__name__)

        self.pathToSiteData = os.path.abspath("nhl.csv")
        self.pathToNetworkData = os.path.abspath("nhl_network_data.csv")

        if(eval(flashScoreSiteDownloader_cfg["init_load_data"])):
            self.formInfoFromSite()

        self.calculator = Reflection.get_class("statisticsCalculators." + calculator_cfg["name"] + ".py",
                                          self.pathToSiteData, self.pathToNetworkData,
                                          calculator_cfg)


    def rec_to_file_from_site(self,all_matches):
        self.logger.info(f"Создание файла")
        file = open(self.pathToSiteData, 'w', newline='', encoding="utf-8")

        with concurrent.futures.ThreadPoolExecutor() as tpe:
            # Смотрим информацию по каждому турниру
            rows = stream([tpe.submit(match.getRowFromMatch) for match in all_matches]).map(lambda x: x.result()).toList()
        with file:
            writer = csv.writer(file)
            writer.writerows(rows)

        self.logger.info(f"Файл успешно создан")

    def rec_to_file_for_network(self,x, y):

        file = open(self.calculator.pathToNetworkData, 'w', newline='')
        rows = []

        with file:
            writer = csv.writer(file)
            for i in range(len(x)):
                row = list(x[i][:])
                row.append(y[i])
                rows.append(row)
            writer.writerows(rows)


    def formInfoFromSite(self):

        # Время начала выполнения скрипта
        start_time = datetime.now()

        headers = {"x-fsign": "SW9D1eZo"}

        #Все матчи
        all_matches = set()

        # Суммарное количество матчей
        games_counter = 0

        for i in range(30):

            #2022-2023
            url = f'https://d.flashscorekz.com/x/feed/tr_1_198_G2Op923t_176_{i}_3_ru-kz_1'

            response = requests.get(url=url, headers=headers)

            data = response.text.split('¬')
            data_list = [{}]

            for item in data:
                key = item.split('÷')[0]
                value = item.split('÷')[-1]

                if '~' in key:
                    data_list.append({key: value})
                else:
                    data_list[-1].update({key: value})

            for game in data_list:

                # Фиксируем название чемпионата
                if 'ZA' in list(game.keys())[0]:

                    # TODO: рассматриваем только регулярку
                    if ("Плей-офф" in game.get("~ZA") or "Предсезонка" in game.get("~ZA") or "Все звезды" in game.get(
                            "~ZA")):
                        break

                    name_tour = game.get("~ZA")
                    print("\n" + name_tour)

                if 'AA' in list(game.keys())[0]:

                    date = datetime.fromtimestamp(int(game.get("AD")))
                    team_1 = game.get("AE")
                    team_2 = game.get("AF")
                    score = f'{game.get("AG")} : {game.get("AH")}'

                    # TODO: освовное время или овертайм (10)
                    isOvertime = 0
                    if (game.get("AC") == "10"):
                        str_game = "{} После ОТ {} {} {} ".format(date, team_1, score, team_2)
                        isOvertime = 1
                    else:
                        str_game = "{} {} {} {} ".format(date, team_1, score, team_2)

                    # Учитываем только завершившиеся матчи или лайв
                    if (("None" in score) == False and ((str_game in all_matches) == False)):
                        print(str_game)
                        games_counter += 1

                    # games.add(str_game)
                    all_matches.add(Match(date, team_1, game.get("AG"), game.get("AH"), team_2, isOvertime))

        all_matches = sorted(list(all_matches), key=lambda x: x.date)

        self.logger.info(f"Общее количество найденных матчей {len(all_matches)}")

        self.logger.info(f"Количество матчей с ОТ {stream(all_matches).filter(lambda x: x.result==1).toList().size()}")

        #Запись матчей в csv файл
        self.rec_to_file_from_site(all_matches)

        self.logger.info(f"Время выполнения нахождения и записи данных с сайта в csv файл {datetime.now() - start_time}")



