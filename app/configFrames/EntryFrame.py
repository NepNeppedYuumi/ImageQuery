from os import path

import customtkinter as ctk

from Config import Config


class EntryFrame(ctk.CTkScrollableFrame):
    """
    Not all methods are used or required for every subclass of it.
    But if used in more than one it will be included by the parent
    to allow for more customizing of the subclasses.
    """
    keyWidth = 200
    valueWidth = 400
    exploreButtonWidth = 50
    deleteButtonWidth = 22
    plusButtonWidth = 40

    def __init__(self, master, config: Config, command=None,
                 **kwargs):
        super().__init__(master, **kwargs, fg_color="transparent",
                         bg_color="transparent")
        self.config = config  # TODO this means you store one config for every
        #                           frame, isn't this impractical af?
        self.stringVars = None
        self.explorerButtonCheck: bool = False

    @staticmethod
    def newRowFrame(master):
        return ctk.CTkFrame(master, fg_color="transparent",
                            bg_color="transparent")

    @staticmethod
    def packFrame(widget: ctk.CTkFrame | ctk.CTkLabel | ctk.CTkButton):
        widget.pack(side='top', padx=10, pady=5)

    @staticmethod
    def packWidget(widget):
        widget.pack(side='left', padx=(5, 5))

    @staticmethod
    def addEntry(master: ctk.CTkFrame, stringVar: ctk.StringVar | None,
                 width: int = 200, **kwargs):
        entry = ctk.CTkEntry(
            master, width=width, textvariable=stringVar, **kwargs
        )
        entry.pack(side='left', padx=5)

    def addLabel(self, text: str, width: int = 200):
        label = ctk.CTkLabel(
            self, width=width, text=text
        )
        self.packFrame(label)

    def addLabelWidget(self, master: ctk.CTkFrame, text: str,
                       width: int = 200):
        label = ctk.CTkLabel(
            master, width=width, text=text
        )
        self.packWidget(label)

    def explorerButton(self, master, stringVar: ctk.StringVar):
        button = ctk.CTkButton(
            master, text="...", width=self.exploreButtonWidth,
            command=lambda: self.openExplorer(stringVar))
        button.pack(side='left', padx=(5, 5))

    @staticmethod
    def openExplorer(stringVar: ctk.StringVar):
        inputPath = ctk.filedialog.askdirectory()
        if path:
            stringVar.set(path.abspath(inputPath))

    def deleteButton(self, master, value):
        button = ctk.CTkButton(
            master, text="x", width=self.deleteButtonWidth, command=lambda:
            self.deleteButtonEvent(master, value))
        button.pack(side='left', padx=(0, 10))

    def deleteButtonEvent(self, master, value):
        master.pack_forget()
        self.stringVars.remove(value)

    # noinspection PyAttributeOutsideInit
    def addPlusButton(self, command):
        # TODO make look nice on screen
        self.plusButton = ctk.CTkButton(
            self, text="+", width=self.plusButtonWidth, command=command)
        self.packFrame(self.plusButton)

    @staticmethod
    def plusButtonEventWrapper(func):
        """
        Handles the common actions between pressing the plus
        button in a config frame. It unpacks the plus button
        from the frame, then lets the config frame specific
        method handle creating an empty variable frame,
        and then appends that to the variable list and packs
        the plus button again.
        :param func: Creates the empty variable frame
        :return: A wrapper around the plusButton event
        """
        def eventWrapper(self, *args, **kwargs):
            self.plusButton.pack_forget()
            emptyValue = func(self, *args, **kwargs)
            self.stringVars.append(emptyValue)
            self.packFrame(self.plusButton)
        return eventWrapper

    def keyValuePairEntry(
            self, key: ctk.StringVar, value: ctk.StringVar,
            deleteButton: bool = True, **kwargs
    ):
        entryFrame = self.newRowFrame(self)
        # entryFrame.grid(row=index, column=0, padx=10,
        #                 pady=5, sticky='w')
        self.packFrame(entryFrame)
        if deleteButton:
            self.deleteButton(entryFrame, (key, value))
        self.addEntry(entryFrame, key, width=self.keyWidth, **kwargs)
        self.addEntry(entryFrame, value, width=self.valueWidth, **kwargs)
        if self.explorerButtonCheck:
            self.explorerButton(entryFrame, value)
