from typing import List

import customtkinter as ctk

from Config import Config
from .EntryFrame import EntryFrame


class BlacklistEntryFrame(EntryFrame):

    def __init__(self, master, config: Config, blacklist: List, **kwargs):
        super().__init__(master, config, **kwargs)
        self.blacklist: List = blacklist
        self.stringVars: List[ctk.StringVar] = []
        for blacklistPath in self.blacklist:
            stringVar = ctk.StringVar(self, blacklistPath)
            self.deletablePathEntry(
                stringVar
            )
            self.stringVars.append(stringVar)
        self.addPlusButton(self.plusButtonEvent)

    def updateConfig(self):
        oldBlacklist = self.blacklist.copy()
        self.blacklist.clear()
        for var in self.stringVars:
            if var.get() == '':
                continue
            self.blacklist.append(var.get())
        if any(old == new for old, new in zip(oldBlacklist, self.blacklist)) \
                or len(oldBlacklist) != self.blacklist:
            return True
        return False

    def deletablePathEntry(
            self, value: ctk.StringVar
    ):
        entryFrame = self.newRowFrame(self)
        self.packFrame(entryFrame)
        self.deleteButton(entryFrame, value)
        self.addEntry(entryFrame, value, width=self.valueWidth)
        self.explorerButton(entryFrame, value)

    @EntryFrame.plusButtonEventWrapper
    def plusButtonEvent(self):
        emptyVar = ctk.StringVar()
        self.deletablePathEntry(emptyVar)
        return emptyVar
