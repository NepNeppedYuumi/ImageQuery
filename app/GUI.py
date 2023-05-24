from io import BytesIO
from re import search
from subprocess import run, Popen
from threading import Thread
from typing import Tuple, List
from os import path

import customtkinter as ctk
import win32clipboard
from PIL import Image, ImageTk

from app.GuiData import GuiData
from app.ImageList import ImageList
from app.ImagePath import ImagePath
from app.configFrames.BlacklistEntryFrame import BlacklistEntryFrame
from app.configFrames.KeybindFrame import KeybindFrame
from app.configFrames.PathEntryFrame import PathEntryFrame
from app.configFrames.PatternEntryFrame import PatternEntryFrame
from app.configFrames.AutoMovePathFrame import AutoMovePathFrame
from app.ErrorFrame import ErrorFrame


class GUI(ctk.CTk):

    # ----------------------------- INITS ------------------------------ #
    def __init__(self, guiData: GuiData):
        super().__init__()
        # -------------------------- SETUP -------------------------- #

        self.guiData: GuiData = guiData
        self.protocol("WM_DELETE_WINDOW", self.__onClose)

        self.wm_iconbitmap(self.guiData.windowIconPath)

        # self.geometry(self.config.size + '+' + self.config.screenCord) # todo
        self.geometry("800x700+500+100")
        self.update_idletasks()
        self.resizable(True, True)
        self.title(self.config.title)

        self.timer = None
        self._copyInProgress: bool = False
        self.statusLabel: ctk.CTkLabel | None = None
        self.imagePatternFrames: List[ctk.CTkFrame] = []

        # -------------------------- GRID --------------------------- #
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ------------------------- FRAMES -------------------------- #
        self.__navigationFrameInit()
        self.__homeFrameInit()

        self.configFrame = None

        self.errorFrame = ErrorFrame(self, self.config.mainFgColor)

        self.__keyBindsInit()

    @property
    def config(self):
        return self.guiData.config

    @property
    def imageList(self) -> ImageList:
        return self.guiData.imageList

    def __navigationFrameInit(self):
        # create title bar frame
        self.navigationFrame = ctk.CTkFrame(
            self, fg_color=self.config.menuFgColor)

        self.navigationFrame.grid(row=0, sticky="nsew")

        # ------------------------- BUTTONS ------------------------- #
        """
        Adds buttons to top bar menu. Current buttons are:
        Home frame
        Config frame
        
        Pressing these buttons switches the visible active frame
        """
        # TODO change buttons to labels for better appearance
        self.homeFrameButton = ctk.CTkButton(
            self.navigationFrame, text="Home (1)",
            command=self.__homeFrameButtonEvent)
        self.configButton = ctk.CTkButton(
            self.navigationFrame, text="Config (2)",
            command=self.__configButtonEvent)

        self.homeFrameButton.grid(row=2, column=0, padx=(20, 10), pady=10,
                                  sticky='e')
        self.configButton.grid(row=2, column=1, padx=10, pady=10,
                               sticky='w')

    # ------------------------- HOME FRAME -------------------------- #

    def __gridHomeFrame(self):
        self.homeFrame.grid(row=1, column=0, sticky="nsew")

    def __homeFrameInit(self):
        """
        Home frame is the frame where most of the app is run.
        It holds the image frame and image data frame.
        """
        self.homeFrame = ctk.CTkFrame(self, corner_radius=0)
        self.__gridHomeFrame()

        # -------------------------- GRID --------------------------- #
        """
        The home frame is given 2 columns.
        Column 0 is for the image frame.
        Column 1 is for the data frame and is small.
        """
        self.homeFrame.grid_rowconfigure(0, weight=1)
        self.homeFrame.grid_columnconfigure(0, weight=1)
        self.homeFrame.grid_columnconfigure(1, weight=0)

        # ------------------------- FRAMES -------------------------- #
        """
        The initializers for the image frame and image data frame.
        """
        self.__imageFrameInit()
        self.__dataFrameInit()

    # ------------------------- IMAGE FRAME ------------------------- #

    def __imageFrameInit(self):
        self.imageFrame = ctk.CTkFrame(
            self.homeFrame, corner_radius=0, fg_color=self.config.mainFgColor
        )

        # ----------------------- GRID LAYOUT ----------------------- #
        """
        a 3 x 2 frame. 
        row 1 takes most space, row 0 and 2 take less space.
        """
        self.imageFrame.grid(sticky="nsew")
        self.imageFrame.grid_rowconfigure(0, weight=0)
        self.imageFrame.grid_rowconfigure(1, weight=1)
        self.imageFrame.grid_rowconfigure(2, weight=0)

        self.imageFrame.grid_columnconfigure(0, weight=1)
        self.imageFrame.grid_columnconfigure(1, weight=1)

        # -------------------------- ROW 1 -------------------------- #
        # -------------------------FILENAME ------------------------- #
        """
        filename and last few lines of path of the image
        """
        self.nameLabel = ctk.CTkLabel(
            self.imageFrame, text=f"{self.imageList.current.filename}\n"
                                  f"{self.imageList.current.pathEnd}")
        self.nameLabel.grid(row=0, column=0, columnspan=2,
                            padx=20, pady=(20, 5), sticky="nsew")

        # -------------------------- ROW 2 -------------------------- #
        # ---------------------- IMAGE SECTION ---------------------- #
        """
        Creates a canvas that covers most of the frame.
        The event handler manages the adding of the actual image.
        """
        self.canvas = ctk.CTkCanvas(
            self.imageFrame, bg=self.config.mainFgColor, highlightthickness=0)
        self.canvas.grid(row=1, columnspan=2, padx=20, pady=5,
                         sticky="nsew")
        self.canvas.bind('<Configure>', self.__on_canvas_resize)

        # -------------------------- ROW 3 -------------------------- #
        # ------------------------- BUTTONS ------------------------- #
        """
        keep, delete, previous, next, first and last buttons
        """
        self.optionButtonFrame = ctk.CTkFrame(
            self.imageFrame, bg_color="transparent", fg_color="transparent"
        )
        self.optionButtonFrame.grid(
            row=2, column=0, columnspan=2, pady=(5, 20)
        )

        self.optionButtons = []
        self.optionButtonsDetails = (
            ("<<", 50, self.__firstImageEvent),
            ("<", 50, self.__previousButtonEvent),
            ("Keep", 140, self.__keepButtonEvent),
            ("Delete", 140, self.__deleteButtonEvent),
            (">", 50, self.__nextButtonEvent),
            (">>", 50, self.__lastImageEvent)
        )
        for text, width, event in self.optionButtonsDetails:
            optionButton = ctk.CTkButton(
                self.optionButtonFrame, text=text, height=25, width=width,
                command=event
            )
            optionButton.pack(padx=2, pady=0, side='left')
            self.optionButtons.append(optionButton)

        checkmark = ctk.CTkImage(
            Image.open(self.guiData.checkmarkPath), size=(20, 20))
        cross = ctk.CTkImage(
            Image.open(self.guiData.crossPath), size=(20, 20))

        self.keptLabel = ctk.CTkLabel(
            self.imageFrame, text='', image=checkmark, height=20, width=50
        )
        self.deletedLabel = ctk.CTkLabel(
            self.imageFrame, text='', image=cross, height=20, width=50
        )

    # -------------------------- DATA FRAME ------------------------- #
    def __dataFrameInit(self):
        self.dataFrame = ctk.CTkFrame(
            self.homeFrame, corner_radius=0,
            fg_color=self.config.dataFrameFgColor)
        self.dataFrame.grid(row=0, column=1, sticky="nsew")

        # # ----------------------- GRID LAYOUT ----------------------- #
        self.dataFrame.grid_rowconfigure(0, weight=0)
        self.dataFrame.grid_rowconfigure(1, weight=1)
        self.dataFrame.grid_rowconfigure(2, weight=0)

        # -------------------------- ROW 1 -------------------------- #
        # ------------------------- POP UP -------------------------- #
        # TODO
        self.dataPopUpLabel = ctk.CTkLabel(
            self.dataFrame, bg_color='transparent', fg_color='transparent',
            text="", height=100
        )
        self.dataPopUpLabel.grid(row=0, sticky='nsew')

        # -------------------------- ROW 2 -------------------------- #
        # ---------------------- ATTRIBUTES ------------------------- #
        """
        Creates a data label which holds information about the image.
        Current information:
        Dimensions: width x height
        Size: KB | MB
        """
        self.imageInfoFrame = ctk.CTkFrame(
            self.dataFrame, bg_color='transparent', fg_color='transparent'
        )
        self.imageInfoFrame.grid(row=1, column=0, sticky='nsew',
                                 pady=0)

        self.dataLabel = ctk.CTkLabel(
            self.imageInfoFrame, text=self.imageList.currentInfo,
            width=140
        )
        self.dataLabel.pack(padx=5, pady=5, side='top')

        # ------------------------ PATTERNS ------------------------- #
        """
        outdated explanation:
        Creates all pattern labels, currently 3 sets, 
        spaces them into row 3 and 4.
        It creates 2 labels in each set, to make it seem like it
        has a border around it.
        After creating the empty overlapping labels it calls
        the label update method to update their text and colour
        
        An example label is created an placed in the initial list
        to reduce warnings from pycharm.
        """
        self.updatePatternLabels()

        # -------------------------- ROW 5 -------------------------- #
        # ------------------------- BUTTONS ------------------------- #
        """
        Creates two buttons on the bottom of the data frame:
        open image button
        open directory button
        
        both buttons have only an image and no text, in case
        of key binds the keybind will be set as text by
        the update key binds method
        """

        image_icon_image = ctk.CTkImage(
            Image.open(self.guiData.imageIconPath), size=(18, 18))
        self.dir_icon_image = ctk.CTkImage(
            Image.open(self.guiData.dirIconPath), size=(18, 18))

        self.dataFrameButtonFrame = ctk.CTkFrame(
            self.dataFrame, fg_color='transparent'
        )

        self.openImageButton = ctk.CTkButton(
            self.dataFrameButtonFrame, text="", image=image_icon_image,
            width=50, height=25, command=self.__openImageEvent)
        self.openDirButton = ctk.CTkButton(
            self.dataFrameButtonFrame, text="", image=self.dir_icon_image,
            width=50, height=25, command=self.__openDirEvent)

        self.openImageButton.grid(row=3, column=0, padx=(2, 2), pady=20,
                                  sticky="es")
        self.openDirButton.grid(row=3, column=1, padx=(2, 2), pady=20,
                                sticky="ws")

        self.dataFrameButtonFrame.grid(row=2)

    # ------------------------ CONFIG FRAME ------------------------- #

    def __gridConfigFrame(self):
        self.configFrame.grid(row=1, sticky="nsew")

    def __configFrameInit(self):
        """
        uses pack instead of grid

        check if you want buffer between the two bars or not
        or that you want the selections to be centered
        maybe the navigation frame should be horizontal not vertical?
        """
        self.configFrame = ctk.CTkFrame(self)

        self.configTabsTabview = ctk.CTkTabview(
            self.configFrame, command=self.focus
        )
        self.configTabsTabview.pack(fill='both', expand=True)

        # ----------------------- PATH FRAME ------------------------ #
        self.configTabsTabview.add("main paths")
        self.pathFrame = PathEntryFrame(
            self.configTabsTabview.tab("main paths"), self.config
        )
        self.pathFrame.pack(fill='both', expand=True)

        # --------------------- PATTERN FRAMES ----------------------- #
        self.configPatternFrames = []

        tabData = (
            ("Source patterns", "sourcePatterns", self.config.sourcePatterns,
             False),
            ("Bad patterns", "badPatterns", self.config.badPatterns, False),
            ("Bad paths", "badPath", self.config.badPath, True)
        )
        # creates the tabs and PatternEntryFrames one by one.
        for tabName, dictName, tabVars, exploreButton in tabData:
            self.configTabsTabview.add(tabName)
            frame = PatternEntryFrame(
                self.configTabsTabview.tab(tabName), tabVars, self.config,
                dictName, exploreButton=exploreButton
            )
            frame.pack(fill='both', expand=True)
            self.configPatternFrames.append(frame)
        s, b1, b2 = self.configPatternFrames
        self.sourcePatternsFrame = s
        self.badPatternsFrame = b1
        self.badPathsFrame = b2
        del self.configPatternFrames
        # Modifies the entry to PatternEntryFrames

        # --------------------- BLACKLIST FRAME ---------------------- #
        self.configTabsTabview.add("blacklist")
        self.blacklistFrame = BlacklistEntryFrame(
            self.configTabsTabview.tab("blacklist"), self.config,
            self.guiData.blacklist
        )
        self.blacklistFrame.pack(fill='both', expand=True)
        # ---------------------- KEYBIND FRAME ----------------------- #
        self.configTabsTabview.add("key binds")
        self.keybindFrame = KeybindFrame(
            self.configTabsTabview.tab("key binds"), self.config
        )
        self.keybindFrame.pack(fill='both', expand=True)

        # --------------------- AUTOMOVE FRAME ----------------------- #
        self.configTabsTabview.add('auto move')
        self.autoMoveFrame = AutoMovePathFrame(self.configTabsTabview.tab(
            'auto move'), self.config)
        self.autoMoveFrame.pack(fill='both', expand=True)

    # ------------------------- KEY BINDS --------------------------- #

    def __keyBindsInit(self):
        self.bind('<Control-c>', self.__copyImage)
        self.bind('<Escape>', self.__onClose)
        self.bind('<Key-2>', self.__configButtonEvent)
        self.bind('<Key-1>', self.__homeFrameButtonEvent)

        self.homeButtons = [
            ('open', self.openImageButton), ('openDir', self.openDirButton)
        ]
        for details, button in zip(self.optionButtonsDetails,
                                   self.optionButtons):
            self.homeButtons.append((details[0], button))
        self.updateKeyBinds(self.homeButtons)

    # --------------------------- FACTORIES ----------------------------- #
    @staticmethod
    def coloredBorderLabelFactory(
            master: ctk.CTkFrame, text: str,
            borderColor: str | Tuple[str, str], fgColor: str | Tuple[str, str],
            width: int = 136, height: int = 46, padx: int = 2, pady: int = 2
    ):
        frame = ctk.CTkFrame(
            master, fg_color=borderColor
        )
        label = ctk.CTkLabel(
            frame, text=text, fg_color=fgColor, width=width, height=height,
        )
        label.pack(padx=padx, pady=pady)
        return frame

    # ----------------------------- EVENTS ------------------------------ #

    def __homeFrameButtonEvent(self, *_):
        self.configFrame.grid_forget()
        self.focus()
        self.__gridHomeFrame()
        self.updateConfigChanges()
        self.bind('<Control-c>', self.__copyImage)
        self.bind('<Key-1>', self.__homeFrameButtonEvent)
        self.bind('<Key-2>', self.__configButtonEvent)
        self.updateKeyBinds(self.homeButtons)

    def __configButtonEvent(self, *_):
        if self.configFrame is None:
            self.__configFrameInit()
        self.homeFrame.grid_forget()
        self.__gridConfigFrame()
        self.unbind('<Control-c>')
        self.unbind('<Key-1>')  # TODO make entryFrame's ignore these
        self.unbind('<Key-2>')
        self.unbindKeys(self.homeButtons)

    def __on_canvas_resize(self, event):
        # Cancel any existing timer
        if self.timer:
            self.after_cancel(self.timer)

        # Start a new timer to update the canvas after the delay
        self.timer = self.after(
            self.config.resizeDelay, self.__updateImageSize, event
        )

    @staticmethod
    def shiftEvent(event):
        """
        Facilitates changing the current image by executing
        the method that changes the current image and
        then follows up by updating the currently displayed
        image and all related information by calling updateImage.
        :param event: The method to be executed
        :return: the wrapper
        """
        def worker(self):
            event(self)
            self.updateImage()
        return worker

    @staticmethod
    def shiftLeft(buttonEvent):
        """
        Facilitates shifting to the left by making the
        imageList move to the left.
        :param buttonEvent: The button method
        :return: The wrapper
        """
        def worker(self):
            buttonEvent(self)
            self.imageList.previousImage()
        return worker

    @staticmethod
    def shiftRight(buttonEvent):
        """
        Facilitates shifting to the right by making the
        imageList move to the right. The event returns
        the status of the current image and will be passed
        to the method that loads the next image.
        :param buttonEvent: The button method
        :return: The wrapper
        """
        def worker(self):
            statusCurrent = buttonEvent(self)
            self.imageList.nextImage(statusCurrent=statusCurrent)
        return worker

    @shiftEvent
    @shiftRight
    def __keepButtonEvent(self):
        """
        Will keep the current image.
        Wrapped by shiftRight and shiftEVent to handle common
        actions.
        If the status of the current image is already True it
        will simply end the method and return None.

        A movePath is defined, which starts out as an empty
        string. If it is no longer an empty string later on
        the image will get moved to its corresponding path.

        If the current status is None, it will update the session
        log with 1 additional kept image.
        If the current status is False, it will update the session
        log with 1 kept image, and 1 less removed image.
        It will also set the movePath to 'keep'

        It will check if the current images gets a positive result
        from the autoMoveMatch method. If this is true, it will
        set the movePath to the corresponding MoveTo.

        If the movePath is no longer an empty string the current
        image will be moved with moveImage to the movePath.
        If autoMove evaluates to True, the current image's
        properDir will be updated.

        The method will return True to set the status of the
        current image by the wrapper shiftRight

        shiftEvent will update the displayed image.
        :return: bool, new status of the current imagee
        """
        current: ImagePath = self.imageList.current
        if current.status is True:
            return None
        movePath: str = ""
        if current.status is None:
            self.guiData.updateSessionLog((1, 0))
        elif current.status is False:
            self.guiData.updateSessionLog((1, -1))
            movePath = 'keep'
        if autoMove := self.autoMoveMatch():
            movePath = self.config.moveTo(autoMove)
        if movePath != "":
            self.imageList.moveImage(current, movePath)
            if autoMove:
                self.imageList.current.updateProperDir(movePath)
        return True

    @shiftEvent
    @shiftRight
    def __deleteButtonEvent(self):
        """
        Deletes the current image and moves it to the
        delete folder.

        If the status is False the image is already deleted,
        and it will return None.

        It will move the current image to the delete folder
        by passing 'delete' to the moveImage method.
        It will update the session log corresponding to the current
        status.
        It then returns False to indicate the new
        status for the current image.
        :return: bool, new status of the current image
        """
        current: ImagePath = self.imageList.current
        if current.status is False:
            return None
        self.imageList.moveImage(current, 'delete')
        if current.status is True:
            self.guiData.updateSessionLog((-1, 1))
        else:
            self.guiData.updateSessionLog((0, 1))
        return False

    @shiftEvent
    @shiftLeft
    def __previousButtonEvent(self):
        return

    @shiftEvent
    @shiftRight
    def __nextButtonEvent(self):
        return None

    @shiftEvent
    def __firstImageEvent(self):
        self.imageList.firstImage()

    @shiftEvent
    def __lastImageEvent(self):
        self.imageList.lastImage()

    def __openImageEvent(self):
        # Create a new thread to load the image
        thread = Thread(target=lambda x: run(['start', '', x], shell=True),
                        args=(self.imageList.current.path,))
        thread.start()

    def __openDirEvent(self):
        Popen(f'explorer /select,"{self.imageList.current.path}"')

    def __copyImage(self, event=None):
        if self.homeFrame.cget('fg_color') != "transparent" and \
                not self._copyInProgress:
            self._copyInProgress = True
            thread = Thread(target=self.__copyImageThread,
                            args=(event,))
            thread.start()

    def __copyImageThread(self, *_):
        # Open the image file in binary mode
        with BytesIO() as output:
            self.imageList.currentImage.convert("RGB").save(output,
                                                            "BMP")
            data = output.getvalue()[14:]
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB,
                                            data)
            win32clipboard.CloseClipboard()
        self._copyInProgress = False

    def __onClose(self, *_):
        self.guiData.writeSessionLog()
        self.guiData.writeBlacklist()
        self.config.width, self.config.height = \
            self.winfo_width(), self.winfo_height()
        self.config.screenCord = (self.winfo_rootx(), self.winfo_rooty())
        self.config.writeToConfig()
        # self.quit()
        self.destroy()

    # ----------------------------- UPDATES ----------------------------- #
    def updateImage(self):
        """
        Updates everything related to the image
        It calls for the name to be updated, the displayed image,
        the data label and pattern labels to be updated.
        It also updated the status label.
        :return:
        """
        self.updateNameLabel()
        mock_event = type('', (), {'width': self.canvas.winfo_width(),
                                   'height': self.canvas.winfo_height()})()
        self.__updateImageSize(mock_event)
        self.__updateStatusLabel()
        self.updateDataLabel()
        self.updatePatternLabels()

    def updateNameLabel(self):
        self.nameLabel.configure(text=self.imageList.current.filename + '\n'
                                 + self.imageList.current.pathEnd)

    def __updateImageSize(self, event):
        canvas_ratio = event.width / event.height
        image_ratio = self.imageList.currentRatio
        # get coordinates
        if canvas_ratio > image_ratio:  # canvas is wider than the image
            height = int(event.height)
            width = int(height * image_ratio)
        else:  # canvas is narrower than the image
            width = int(event.width)
            height = int(width / image_ratio)

        resized_image = self.imageList.currentImage.resize((width, height))
        self.resized_tk = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(
            int(event.width / 2),
            int(event.height / 2),
            anchor='center',
            image=self.resized_tk)

    def __updateStatusLabel(self):
        statusOptions = {None: None, False: self.deletedLabel,
                         True: self.keptLabel}
        newStatus = statusOptions.get(self.imageList.current.status)
        if newStatus is None and self.statusLabel is not None:
            self.statusLabel.grid_forget()
        elif newStatus is not None and self.statusLabel != newStatus:
            if self.statusLabel is not None:
                self.statusLabel.grid_forget()
            newStatus.grid(row=2, column=1, pady=(5, 20), sticky='e')
        self.statusLabel = newStatus

    def updateDataLabel(self):
        self.dataLabel.configure(text=self.imageList.currentInfo)

    def updateConfigChanges(self):
        configTabs = (
            self.pathFrame, self.sourcePatternsFrame, self.badPatternsFrame,
            self.badPathsFrame, self.keybindFrame, self.autoMoveFrame
        )
        for frame in configTabs:
            frame.updateConfig()
        blacklistChange = self.blacklistFrame.updateConfig()
        if self.guiData.mainPath != self.config.mainPath or blacklistChange:
            self.guiData.writeBlacklist()
            self.guiData.writeDirList()
            self.guiData.openDirList()

    def updatePatternLabels(self):
        """
        Updates the colored pattern labels in the image data
        section.
        First it destroys all previous pattern frames.

        It then matches loops through all different pattern types
        and matches the pattern for each.
        Pattern matching is done with the patternMatching
        method. For each pattern found by patternMatching it makes
        a coloredBorderLabel using the corresponding factory.
        Each frame is packed to the imageInfoFrame and added
        to the imagePatternFrames list.

        The different patterns can be seen in patternData
        """
        for frame in self.imagePatternFrames:
            frame.pack_forget()
            frame.destroy()
        self.imagePatternFrames.clear()
        patternData = (
            (self.config.sourcePatterns, self.imageList.current.filename,
             "Name matches", self.config.patternMatchColor),
            (self.config.badPatterns, self.imageList.current.filename,
             "Bad name", self.config.badPatternMatchColor),
            (self.config.badPath, self.imageList.current.path,
             "Bad path", self.config.badPathMatchColor)
        )
        for pattern, comparedText, displayText, color in patternData:
            patternMatch = self.patternMatching(pattern, comparedText)
            for match in patternMatch:
                text = f"{displayText}:\n{match}"
                patternFrame = self.coloredBorderLabelFactory(
                    self.imageInfoFrame, text, color,
                    self.config.dataFrameFgColor
                )
                patternFrame.pack(padx=5, pady=5, side='top')
                self.imagePatternFrames.append(patternFrame)

    def updateKeyBinds(self, buttons):
        # TODO make button writing better
        for name, button in buttons:
            key = self.config.keyBinds.get(name, None)
            text = button.cget('text').split('(')
            if key is None or key == '':
                self.unbindKeys(((name, button),))
                button.configure(text=text[0])
            else:
                if key.isalpha():
                    self.bind(f"<Key-{key.lower()}>",
                              lambda event, btn=button: btn.invoke())
                    self.bind(f"<Key-{key.upper()}>",
                              lambda event, btn=button: btn.invoke())
                else:
                    self.bind(f"<Key-{key}>",
                              lambda event, btn=button: btn.invoke())
                button.configure(text=f"{text[0]}({key})")

    def unbindKeys(self, buttons):
        # TODO fix this shitty implementation
        for name, button in buttons:
            key = self.config.keyBinds.get(name, None)
            if key is not None:
                if key.isalpha():
                    self.unbind(f"<Key-{key.lower()}>")
                    self.unbind(f"<Key-{key.upper()}>")
                else:
                    self.unbind(f"<Key-{key}>")

    # ----------------------------- CHECKS ------------------------------ #

    @staticmethod
    def patternMatching(patterns, string):
        """
        Matches all patterns in a dictionary to a string.
        Makes use of regex search to see if the pattern
        is somewhere contained within the string.
        It adds the key of each item in the dictionary to
        a list if the pattern matches.
        It returns a list with all keys.
        If no matches are made it returns an empty list.
        :param patterns: A dictionary with the patterns
                        key: patternType, value: pattern
        :param string: Patterns get matched to this
        :return: list of all patternTypes
        """
        patternMatches = []
        for patternType, pattern in patterns.items():
            if search(pattern, string):
                patternMatches.append(patternType)
        return patternMatches

    def autoMoveMatch(self) -> bool | str:
        """
        Checks if the current image's proper path matches any
        of the moveFrom patterns using regex. In case it matches
        it will return the key of the value pair.
        :return: The key of the move if it matches, False if it
                doesn't match.
        """
        for patternType, move in self.config.autoMove.items():
            moveFrom, _ = move
            moveFrom = moveFrom.replace(path.sep, 2*path.sep)
            if search(moveFrom, self.imageList.current.properPath):
                return patternType
        return False
