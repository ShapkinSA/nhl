from cfg.WorkingWithCfg import WorkingWithCfg
from flashScoreSiteDownloader.FlashScoreSiteDownloader import FlashScoreSiteDownloader
from logs.CustomLogger import CustomLogger
from reflection.Reflection import Reflection

if __name__ == '__main__':

    logger = CustomLogger().getLogger("main")

     #Создание csv файлов
    flashScoreSiteDownloader_cfg, calculator_cfg, algorithm_cfg = WorkingWithCfg.parsing_xml("settings.xml")

    flashScoreSiteDownloader = FlashScoreSiteDownloader(flashScoreSiteDownloader_cfg,calculator_cfg)

    #Создаём модель алгоритма
    algorithm = Reflection.get_class("algorithms."+algorithm_cfg["name"]+".py", algorithm_cfg, flashScoreSiteDownloader.calculator)
