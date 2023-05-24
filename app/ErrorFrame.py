import customtkinter as ctk
import winsound

from app.GuiData import GuiData


class ErrorFrame(ctk.CTkToplevel):

    def __init__(self, master: ctk.CTk, fgColor: str):
        super().__init__(master, fg_color=fgColor)
        self.protocol("WM_DELETE_WINDOW", self.onClose)
        self.bind('<Escape>', self.onClose)
        self.title('Error')
        self.text: str = "This is an error!"
        self.label: ctk.CTkLabel = ctk.CTkLabel(self, text=self.text)
        self.withdraw()

    def setPosition(self):
        masterX: int = self.master.winfo_rootx()
        masterY: int = self.master.winfo_rooty()
        masterWidth: int = self.master.winfo_width()
        masterHeight: int = self.master.winfo_height()

        windowWidth: int = self.winfo_width()
        windowHeight: int = self.winfo_height()

        x = masterX + (masterWidth - windowWidth) // 2
        y = masterY + (masterHeight - windowHeight) // 2

        self.geometry(f"+{x}+{y}")

    def show(self):
        self.playErrorSound()
        self.setPosition()
        self.deiconify()
        self.grab_set()
        self.wait_window()

    def onFocusIn(self, event):
        if str(event.widget) != str(self):
            self.playErrorSound()

    @staticmethod
    def playErrorSound():
        winsound.PlaySound("SystemExclamation", winsound.SND_NOWAIT)

    def onClose(self, *args):
        self.resetText()
        self.grab_release()
        self.withdraw()

    def updateText(self, errorText: str):
        self.label.configure(text=errorText)

    def resetText(self):
        self.label.configure(text='')
