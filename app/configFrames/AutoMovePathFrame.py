from typing import List, Tuple

import customtkinter as ctk

from Config import Config
from .EntryFrame import EntryFrame


class AutoMovePathFrame(EntryFrame):
    def __init__(self, master: ctk.CTkFrame, config: Config):
        super().__init__(master, config)

        self.stringVars: \
            List[Tuple[ctk.StringVar, ctk.StringVar, ctk.StringVar]] = []

        for key, values in self.config.autoMove.items():
            moveFrom, moveTo = values
            stringVars = (
                ctk.StringVar(self, key), ctk.StringVar(self, moveFrom),
                ctk.StringVar(self, moveTo)
            )
            self.stringVars.append(stringVars)
            self.moveFrame(*stringVars)
        self.addPlusButton(self.plusButtonEvent)

    def updateConfig(self):
        self.config.clearDict('autoMove')
        for key, moveFrom, moveTo in self.stringVars:
            keyStr, moveFromStr, moveToStr = key.get(), moveFrom.get(), \
                                             moveTo.get()
            if keyStr == '' or moveToStr == '' or moveToStr == '':
                continue

            self.config.createValue(
                'autoMove', keyStr, [moveFromStr, moveToStr]
            )

    def moveFrame(self, key, moveFrom, moveTo):
        entryFrame = self.newRowFrame(self)
        self.packFrame(entryFrame)
        self.deleteButton(entryFrame, (key, moveFrom, moveTo))
        self.addEntry(entryFrame, key, width=self.keyWidth-50)
        self.addEntry(entryFrame, moveFrom, width=self.keyWidth)
        self.explorerButton(entryFrame, moveFrom)
        self.addEntry(entryFrame, moveTo, width=self.keyWidth)
        self.explorerButton(entryFrame, moveTo)

    @EntryFrame.plusButtonEventWrapper
    def plusButtonEvent(self):
        emptyVars = (ctk.StringVar(), ctk.StringVar(), ctk.StringVar())
        self.moveFrame(*emptyVars)
        return emptyVars
