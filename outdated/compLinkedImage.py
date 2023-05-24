from random import randint


class ImagePath:

    def __init__(self, imagePath, previous, nextImage=None,
                 status: bool = None):
        self.originalPath = imagePath
        self.previous = previous
        if previous is not None:
            previous.next = self
        self.next = nextImage
        self.status: bool = status

    @property
    def originalPath(self):
        return self._originalPath

    @originalPath.setter
    def originalPath(self, originalPath):
        self._originalPath = originalPath

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def previous(self):
        return self._previous

    @previous.setter
    def previous(self, previous):
        self._previous = previous

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, next_):
        self._next = next_


class LinkedImage:

    def __init__(self, maxlen: int = None):
        first = ImagePath('hi', None)
        self.first: ImagePath | None = first
        self.last: ImagePath | None = first
        self.current: ImagePath | None = first
        self.length: int = 1
        self.maxlen: int = maxlen

    def nextImage(self):
        if self.current.next is not None:
            self.current = self.current.next
            return
        self.current = ImagePath(self.newImage(), self.current)
        self.length += 1
        if self.maxlen is not None and self.length > self.maxlen:
            self.popLeft()

    def previousImage(self):
        if self.current.previous is None:
            return
        self.current = self.current.previous

    def popLeft(self):
        self.first.next.previous = None
        self.first = self.first.next
        self.length -= 1

    def newImage(self):
        return randint(0, 50)
