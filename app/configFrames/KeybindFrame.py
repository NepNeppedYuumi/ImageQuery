from typing import List, Tuple

import customtkinter as ctk

from Config import Config
from .EntryFrame import EntryFrame


class KeybindFrame(EntryFrame):

    def __init__(self, master, config: Config, **kwargs):
        super().__init__(master, config, **kwargs)

        self.stringVars: List[Tuple[str, ctk.StringVar]] = []
        self.values: List[str] = []

        for key, value in self.config.keyBinds.items():
            stringVars = (
                key, ctk.StringVar(self, value)
            )
            self.values.append(value)
            self.stringVars.append(stringVars)
            self.labelEntry(*stringVars)

    def updateConfig(self):
        self.config.clearDict("keyBinds")
        for key, value in self.stringVars:
            if value.get() == '':
                continue
            if value.get() in self.config.config['keyBinds'].values():
                value.set('')
            self.config.createValue("keyBinds", key, value.get())

    def labelEntry(self, key, value):
        entryFrame = self.newRowFrame(self)
        self.packFrame(entryFrame)
        self.addLabelWidget(entryFrame, key, width=100)
        self.addEntry(
            entryFrame, value,  width=50, validate="key",
            validatecommand=(entryFrame.register(self.validateInput),
                             '%P', '%s')
        )

    def validateInput(self, newText, prevText):
        # TODO figure out if checking dupes is even possible here
        # print("is this shit happeni")
        # print(self)
        # print(newText)
        # print(prevText)
        if len(newText) > 1:
            return False
        elif len(newText) == 0:
            # self.values.remove(prevText)
            return True
        # elif newText in self.values:
        #     return False
        # self.values.append(newText)
        else:
            return True
