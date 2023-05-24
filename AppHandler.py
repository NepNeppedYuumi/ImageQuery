import subprocess
from time import sleep

from Config import Config


class AppHandler:
    CONFIG_PATH: str = 'config.ini'

    def __init__(self):
        self.config: Config | None = Config(self.CONFIG_PATH)
        self.sleepTime: int = self.config.sleepTime
        self.update: bool = True
        self.counter: int = 0
        self.turnOff: bool = False
        self.startUp: bool = True

        self.config = None

    def runGUI(self):
        output = subprocess.check_output(
            ['python', 'gui.run.py'], text=True
        )
        output = output.split()
        sleepTime, turnOff = output
        self.sleepTime = int(sleepTime)

    def timer(self):
        sleep(self.sleepTime * 60)

    def runLoop(self):
        while not self.turnOff:
            if (self.counter == 0 and not self.startUp) or self.counter != 0:
                self.timer()
            self.runGUI()
            self.counter += 1
            break


def main():
    appHandler = AppHandler()
    appHandler.runLoop()


if __name__ == '__main__':
    main()
