from typing import List

import customtkinter as ctk

from Config import Config
from .EntryFrame import EntryFrame


class PathEntryFrame(EntryFrame):

    def __init__(self, master, config: Config,
                 command=None, **kwargs):
        super().__init__(master, config, **kwargs)
        self.stringVars: List[List[ctk.StringVar]] = [[], []]
        self.radioVars = [ctk.IntVar(value=self.config.usedPath),
                          ctk.IntVar(value=self.config.usedDeletePath)]
        self.pathLists = (self.config.mainPaths, self.config.deletePaths)
        labelStrings = ("Used file tree:", "Used delete directory:")
        for i, entryList in enumerate(self.stringVars):
            self.addLabel(labelStrings[i])
            varValue = 0
            for path in self.pathLists[i]:
                var = ctk.StringVar(self, path)
                entryList.append(var)
                self.addEntryRadioButton(
                    self.radioVars[i], var, varValue
                )
                varValue += 1

    def updateConfig(self):
        for i, entries in enumerate(self.stringVars):
            for pathIndex, entry in enumerate(entries):
                if entry.get() == "":
                    continue
                if i == 0:
                    self.config.mainPaths[pathIndex] = entry.get()
                elif i == 1:
                    self.config.deletePaths[pathIndex] = entry.get()
            if i == 0:
                self.config.usedPath = self.radioVars[i].get()
            elif i == 1:
                self.config.usedDeletePath = self.radioVars[i].get()

    def addEntryRadioButton(self, radioVar, stringVar: ctk.StringVar,
                            value: int):
        entryFrame = self.newRowFrame(self)
        self.packFrame(entryFrame)
        radioButton = ctk.CTkRadioButton(
            entryFrame, variable=radioVar, text='', width=0,
            value=value)
        self.packWidget(radioButton)
        self.addEntry(
            entryFrame, stringVar, width=
            self.valueWidth + self.keyWidth - self.exploreButtonWidth
        )
        self.explorerButton(entryFrame, stringVar)
