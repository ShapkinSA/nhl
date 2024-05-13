"""
    Парсинг файла конфигурации
"""
import xml.etree.ElementTree as ET
class WorkingWithCfg:

    @staticmethod
    def parsing_xml(xml_file_name):

        #Поиск по дереву конфигурационного файла
        tree = ET.parse(xml_file_name)
        root = tree.getroot()

        #Получаем конфиг загрузчика
        flashScoreSiteDownloader = root.findall("flashScoreSiteDownloader")[0].attrib

        #Получаем название алгоритма
        calculator_name = root.findall("calculator")[0].attrib['name']

        #Находим нужный алгоритм
        calculator_cfg = root.findall(calculator_name)[0].attrib

        #Получаем название алгоритма
        algorithm_name = root.findall("algorithm")[0].attrib['name']

        #Находим нужный алгоритм
        algorithm_cfg = root.findall(algorithm_name)[0].attrib

        return flashScoreSiteDownloader, calculator_cfg, algorithm_cfg


