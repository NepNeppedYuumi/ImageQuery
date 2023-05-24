import random
from collections import deque
from queue import Queue
from compLinkedImage import ImagePath as ImagePathLinked
from compLinkedImage import LinkedImage
from time import time


class ImagePath:

    def __init__(self, imagePath, status: bool = None):
        self.originalPath = imagePath
        self.status: bool = status

    @property
    def originalPath(self):
        return self._originalPath

    @originalPath.setter
    def originalPath(self, originalPath):
        self._originalPath = originalPath

    @property
    def path(self):
        if self.status is not False:
            return self.originalPath
        # return self.config.deletePath + sep + self.filename

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status


class ImageDeque(deque):

    def __init__(self, maxlen: int = None):
        super().__init__(maxlen=maxlen)
        self.offset: int = 0  # indicates the amount of rotation to the left.

    def nextImage(self):
        if self.offset > 0:
            self.rotate(-1)
            self.offset -= 1
            return
        self.append(ImagePath(self.newImage()))

    def previousImage(self):
        if self.offset >= len(self):
            return
        self.rotate(1)
        self.offset += 1

    def newImage(self):
        return random.randint(0, 50)


class ImageDequeDouble:

    def __init__(self, maxlen: int = None):
        self.left = deque(maxlen=maxlen)
        self.right = deque()
        self.current = ImagePath(self.newImage())

    def nextImage(self):
        self.left.append(self.current)
        if len(self.right) == 0:
            self.current = ImagePath(self.newImage())
            return
        self.current = self.right.popleft()

    def previousImage(self):
        if len(self.left) == 0:
            return
        self.right.appendleft(self.current)
        self.current = self.left.pop()

    def newImage(self):
        return random.randint(0, 50)


class ImageList:

    def __init__(self, maxlen: int = None):
        self.images = []
        self.index = -1
        self.maxlen = maxlen

    def nextImage(self):
        self.index += 1
        if self.index < len(self.images) - 1:
            return
        self.images.append(ImagePath(self.newImage()))
        if self.maxlen is not None and len(self.images) > self.maxlen:
            self.popLeft()

    def previousImage(self):
        if self.index == 0:
            return
        self.index -= 1

    def newImage(self):
        return "hi how are you doing my lovely lady"

    def popLeft(self):
        if self.index > 0:
            self.index -= 1
        self.images.pop(0)


if __name__ == '__main__':
    structures = (ImageDeque, ImageDequeDouble, LinkedImage,
                  ImageList)
    times = []
    memory_usage = []

    initial = 0
    body = 1000

    loops = 10
    maxlen = 1000

    examples = []
    decision = random.choices((1, -1), weights=(6,4), k=body)
    for structureClass in structures:
        structure = structureClass(maxlen)
        start = time()
        for i in range(maxlen):
            structure.nextImage()

        for loop in range(loops):
            for i in range(initial):
                structure.nextImage()
            for choice in decision:
                if choice == 1:
                    structure.nextImage()
                else:
                    structure.previousImage()
        end = time()
        times.append(end-start)
    print(f"The list was loaded with {initial} objects.\n"
          f"Then that list was worked with {body} times.\n"
          f"with a maxlen of {maxlen}\n"
          f"This was ran {loops} times.")
    for structure, time in zip(structures, times):
        print(f"{structure.__name__} took a total of {time:10e}")
