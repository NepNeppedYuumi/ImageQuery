from os import path
from typing import Dict, Union, List

from configobj import ConfigObj


class Config:

    def __init__(self, filename: str = 'config.ini'):
        self.filename = filename
        self.config = ConfigObj(filename)

    @property
    def config(self) -> ConfigObj:
        return self._config

    @config.setter
    def config(self, config: ConfigObj):
        self._config = config

    def clearDict(self, dictName: str):
        self.config[dictName].clear()

    def createValue(self, dictName: str, key: str, value):
        """
        Creates or sets a value at will.
        :param dictName:
        :param key:
        :param value:
        :return:
        """
        self.config[dictName][key] = value

    # ---------------------------- LOCATIONS ---------------------------- #
    @property
    def usedPath(self) -> int:
        return int(self.config['locations']['usedPath'])

    @usedPath.setter
    def usedPath(self, usedPath: Union[str, int]):
        self.config['locations']['usedPath'] = str(usedPath)

    @property
    def mainPath(self) -> str:
        return path.abspath(
            self.config['locations']['mainPaths'][self.usedPath])

    @property
    def mainPaths(self) -> List[str]:
        return self.config['locations']['mainPaths']

    @mainPaths.setter
    def mainPaths(self, mainPaths: List[str]):
        """
        mainPaths is an ini dictionary
        generally used like:
        self.config.mainPaths[i] = newPath

        to only edit the paths and things that are different
        """
        self.config['locations']['mainPaths'] = mainPaths

    @property
    def defaultPath(self):
        defaultPath = path.abspath(f"static{path.sep}images")
        return defaultPath

    @property
    def usedDeletePath(self) -> int:
        return int(self.config['locations']['usedDeletePath'])

    @usedDeletePath.setter
    def usedDeletePath(self, usedDeletePath: Union[str, int]):
        self.config['locations']['usedDeletePath'] = str(usedDeletePath)

    @property
    def deletePath(self) -> str:
        return path.abspath(self.config['locations']
                            ['deletePaths'][self.usedDeletePath])

    @property
    def deletePaths(self) -> List[str]:
        return self.config['locations']['deletePaths']

    @deletePaths.setter
    def deletePaths(self, deletePaths: List[str]):
        """
        generally used like:
        self.config.deletePaths[i] = newPath

        to only edit the paths and things that are different
        """
        self.config['locations']['deletePaths'] = deletePaths

    @property
    def usedKeepPath(self) -> int:
        return int(self.config['locations']['usedKeepPath'])

    @usedKeepPath.setter
    def usedKeepPath(self, usedKeepPath: Union[str, int]):
        self.config['locations']['usedKeepPath'] = str(usedKeepPath)

    @property
    def keepPath(self) -> str:
        return path.abspath(self.config['locations']
                            ['keepPaths'][self.usedKeepPath])

    @property
    def keepPaths(self) -> List[str]:
        return self.config['locations']['keepPaths']

    @keepPaths.setter
    def keepPaths(self, keepPaths: List[str]):
        """
        generally used like:
        self.config.deletePaths[i] = newPath

        to only edit the paths and things that are different
        """
        self.config['locations']['deletePaths'] = keepPaths

    @property
    def blacklistPath(self) -> str:
        return path.abspath(self.config['locations']['blacklistPath'])

    @blacklistPath.setter
    def blacklistPath(self, blacklistPath: str):
        self.config['locations']['blacklistPath'] = blacklistPath

    @property
    def logPath(self) -> str:
        return self.config['locations']['logPath']

    @property
    def dirListPath(self) -> str:
        return f"generated\\dirList{self.usedPath}.txt"

    # --------------------------- APPEARANCE ---------------------------- #

    @property
    def title(self) -> str:
        return self.config['appearance']['title']

    @property
    def screenCord(self) -> str:
        return self.config['appearance']['screenCord']

    @screenCord.setter
    def screenCord(self, cords: Union[List[str], tuple[str, str]]):
        self.config['appearance']['screenCord'] = f"{cords[0]}+{cords[1]}"

    @property
    def size(self) -> str:
        return f"{self.width}x{self.height}"

    @property
    def width(self) -> str:
        return self.config['appearance']['width']

    @width.setter
    def width(self, width: Union[str, int]):
        self.config['appearance']['width'] = str(width)

    @property
    def height(self) -> str:
        return self.config['appearance']['height']

    @height.setter
    def height(self, height: Union[str, int]):
        self.config['appearance']['height'] = str(height)

    @property
    def menuFgColor(self) -> Union[str, List[str]]:
        return self.config['appearance']['menuFgColor']

    @property
    def mainFgColor(self) -> Union[str, List[str]]:
        return self.config['appearance']['mainFgColor']

    @property
    def dataFrameFgColor(self) -> Union[str, List[str]]:
        return self.config['appearance']['dataFrameFgColor']

    @property
    def patternMatchColor(self) -> Union[str, List[str]]:
        return self.config['appearance']['patternMatchColor']

    @property
    def badPatternMatchColor(self) -> Union[str, List[str]]:
        return self.config['appearance']['badPatternMatchColor']

    @property
    def badPathMatchColor(self) -> Union[str, List[str]]:
        return self.config['appearance']['badPathMatchColor']

    # --------------------------- BEHAVIOUR ----------------------------- #

    @property
    def resizeDelay(self) -> int:
        return int(self.config['behaviour']['resizeDelay'])

    @property
    def supportedFiletype(self) -> tuple[str, ...]:
        return tuple(self.config['behaviour']['supportedFiletype'])

    @property
    def maxLenImageList(self) -> int:
        return int(self.config['behaviour']['maxLenImageList'])

    @property
    def turnOff(self) -> bool:
        return bool(int(self.config['behaviour']['turnOff']))

    @property
    def sleepTime(self) -> int:
        return int(self.config['behaviour']['sleepTime'])

    # ---------------------------- PATTERNS ----------------------------- #

    @property
    def sourcePatterns(self) -> Dict[str, str]:
        return dict(self.config['sourcePatterns'])

    @property
    def badPatterns(self) -> Dict[str, str]:
        return dict(self.config['badPatterns'])

    @property
    def badPath(self) -> Dict[str, str]:
        return dict(self.config['badPath'])

    # -------------------------- KEYBINDINGS ---------------------------- #

    @property
    def keyBinds(self) -> Dict[str, str]:
        return dict(self.config['keyBinds'])

    # ---------------------------- AUTO MOVE ---------------------------- #

    @property
    def autoMove(self) -> Dict[str, list[str, str]]:
        return dict(self.config['autoMove'])

    def moveFrom(self, key) -> str:
        return self.config['autoMove'][key][0]

    def moveTo(self, key) -> str:
        return self.config['autoMove'][key][1]

    # ----------------------- WRITE TO CONFIG --------------------------- #

    def writeToConfig(self):
        self.config.write()
