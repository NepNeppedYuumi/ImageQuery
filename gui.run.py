from Config import Config
from app.GuiData import GuiData
from app.GUI import GUI


def main():
    config = Config('config.ini')
    guiData = GuiData(config, update=True)
    gui = GUI(guiData)
    gui.mainloop()
    print(config.sleepTime)
    print(config.turnOff)


if __name__ == '__main__':
    main()
