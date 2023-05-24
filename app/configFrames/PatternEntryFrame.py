from typing import List, Tuple

import customtkinter as ctk

from Config import Config
from .EntryFrame import EntryFrame


class PatternEntryFrame(EntryFrame):
    def __init__(self, master: ctk.CTkFrame, tabStringProperty,
                 config: Config, configDictName: str,
                 exploreButton: bool = False):
        super().__init__(master, config)

        self.stringVars: List[Tuple[ctk.StringVar, ctk.StringVar]] = []
        self.configDictName: str = configDictName
        self.explorerButtonCheck: bool = exploreButton

        for key, value in tabStringProperty.items():
            stringVars = (
                ctk.StringVar(self, key), ctk.StringVar(self, value)
            )
            self.stringVars.append(stringVars)
            self.keyValuePairEntry(
                *stringVars)
        self.addPlusButton(self.plusButtonEvent)

    def updateConfig(self):
        self.config.clearDict(self.configDictName)
        for key, value in self.stringVars:
            keyStr, valueStr = key.get(), value.get()
            if keyStr == '' or valueStr == '':
                continue
            self.config.createValue(
                self.configDictName, keyStr, valueStr
            )

    @EntryFrame.plusButtonEventWrapper
    def plusButtonEvent(self):
        emptyVars = (ctk.StringVar(), ctk.StringVar())
        self.keyValuePairEntry(*emptyVars)
        return emptyVars

