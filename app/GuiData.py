from datetime import datetime
from os import walk, path, sep
from re import match
from typing import List

from Config import Config
from app.ImageList import ImageList


class GuiData:

    def __init__(self, config, update=None):
        self.config: Config = config

        self.blacklist = []
        self.dirList: List[str] = []
        self.dirProbabilities: List[int] = []
        self.createSessionLog()
        self.openBlacklist()
        if update is True:
            self.writeDirList()
        self.openDirList()
        self.imageList = ImageList(config, self.dirList, self.dirProbabilities,
                                   config.maxLenImageList)

    @property
    def config(self) -> Config:
        return self._config

    @config.setter
    def config(self, config: Config):
        self._config = config

    # ---------------------------- LOCATIONS ---------------------------- #

    @property
    def mainPath(self) -> str:
        """
        The root directory from which images are loaded.
        Simply mimics the method from config.
        :return:
        str: root directory
        """
        return self.config.mainPath

    def writeBlacklist(self):
        """
        Writes the blacklist in memory to the file
        specified in the config file.
        It writes the file out as one path per line.
        """
        with open(self.config.blacklistPath, 'w', encoding='utf-8') as file:
            for blacklistPath in self.blacklist:
                file.write(f"{blacklistPath}\n")

    def openBlacklist(self):
        """
        Clears the blacklist to avoid replacing the list.
        It then puts every line of the file inside it.
        With the method used, if the file is empty it will put
        white space inside it.
        If that is the case it will clear the list again.
        """
        self.blacklist.clear()
        try:
            with open(self.config.blacklistPath, 'r',
                      encoding='utf-8') as file:
                self.blacklist.extend(file.read().strip().split('\n'))
            if self.blacklist[0] == '':
                self.blacklist.clear()
        except FileNotFoundError as e:
            raise e

    @property
    def blacklistPattern(self) -> str:
        """
        Joins the blacklist together with | and replaces
        every path seperator with 2 separators to make it
        regex compatible.
        :return:
        str: A regex compatible pattern
        """
        return '|'.join(self.blacklist).replace(sep, 2*sep)

    def writeDirList(self):
        """
        Walks from the main path tree through every branch
        and writes each path name with a file count into
        the corresponding file.

        # todo add error message if path doesn't exist
        """
        # start_time = perf_counter()
        blacklist = self.blacklistPattern
        rootPath = self.config.mainPath
        if not path.lexists(rootPath):
            rootPath = self.config.defaultPath
        with open(self.config.dirListPath, 'w', encoding='utf-8') as file:
            for root, *_, files in walk(rootPath):
                if match(blacklist, root) and blacklist != '':
                    continue
                file.write(f"{path.join(root)}|{len(files)}\n")
        # end_time = perf_counter()
        # print(end_time - start_time)

    def openDirList(self):
        """
        Opens the path list and appends every path and their file
        count to separate lists. These are later used to choose
        a random path for image selection.

        Incase the file does not exist a call
        will be made to generate it.
        """
        self.dirList.clear()
        self.dirProbabilities.clear()
        try:
            with open(self.config.dirListPath, 'r', encoding='utf-8') as file:
                for dir_, count in map(lambda x: x.split('|'), file):
                    self.dirList.append(dir_)
                    self.dirProbabilities.append(int(count))
            if len(self.dirList) == 0:
                # todo add error message if empty
                self.dirList.append(self.config.defaultPath)
                self.dirProbabilities.append(1)
        except FileNotFoundError:
            self.writeDirList()
            self.openDirList()

    @property
    def windowIconPath(self) -> str:
        return r"static\transparent_window_icon.ico"

    @property
    def checkmarkPath(self) -> str:
        return r"static\checkmark.png"

    @property
    def crossPath(self) -> str:
        return r"static\cross.png"

    @property
    def imageIconPath(self) -> str:
        return r"static\image_icon_light.png"

    @property
    def dirIconPath(self) -> str:
        return r"static\open_folder.png"

    # ---------------------------- LOGGING ----------------------------- #

    @property
    def sessionLog(self) -> list:
        """
        The session log is used to keep track of the
        amount of images kept and deleted.
        It's a list of [date, kept, deleted]
        :return:
        List[str, int, int]: The current session log
        """
        return self._sessionLog

    # noinspection PyAttributeOutsideInit
    def createSessionLog(self):
        """
        Creates a new session log using the current datetime
        and sets it to the sessionLog attribute.
        The session log follows the standard [date, kept, deleted]
        """
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self._sessionLog: list = [date, 0, 0]

    def updateSessionLog(self, increase):
        """
        Increments the session log with the given increase.
        Updates kept and deleted simultaneously.

        General use case sees feeding it a tuple.
        Either (1, 0) or (0, 1).

        #
        """
        self._sessionLog[1] += increase[0]
        self._sessionLog[2] += increase[1]

    def writeSessionLog(self):
        """
        Appends the session log to the log file.

        In case no images have been kept or deleted it will
        not log the session.
        """
        log = self.sessionLog
        if all(amount == 0 for amount in log[1:]):
            return
        with open(self.config.logPath, 'a') as file:
            file.write(f"{log[0]};{log[1]};{log[2]}\n")
