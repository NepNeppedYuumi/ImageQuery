from os import path, makedirs, walk
from random import choices, choice
from shutil import move
from typing import List

from PIL import Image

from Config import Config
from app.ImagePath import ImagePath


class ImageList:
    """
    ImageList is a class that is used as a list container for
    ImagePath objects. It holds methods to create
    random ImagePath objects, and manipulate the list of
    objects. It makes use of an index pointer to keep track
    of the actively referenced image in the list, however
    there are methods to retrieve image regardless of the pointer.
    """

    def __init__(self, config: Config, dirList: List[str],
                 dirProbabilities: List[int] = None, maxlen: int = None):
        self.config = config
        self.dirList: List[str] = dirList
        self.dirProbabilities: List[int] | None = dirProbabilities
        self.index: int = 0
        self.maxlen: int = maxlen
        self.loadBuffer: int = 2
        self.images: List[ImagePath] = []
        self.loadedImages: List[Image] = []
        self.preLoadImages()

    def __repr__(self):
        return self.images

    # --------------------------- CURRENT ----------------------------- #

    @property
    def index(self) -> int:
        """
        The index of the current ImagePath object.
        :return: current index
        """
        return self._index

    @index.setter
    def index(self, index: int):
        """
        The index of the current ImagePath object.

        :param index: the new index
        """
        self._index = index

    @property
    def previousIndex(self) -> int:
        """
        Used to generalize code and handle easier error handling
        :return: the index of the previous image
        """
        return self.index - 1

    @property
    def nextIndex(self) -> int:
        """
        Used to generalize code and handle easier error handling
        :return: the index of the next image
        """
        return self.index + 1

    @property
    def current(self) -> ImagePath:
        """
        Returns the image at the current image index
        :return: current ImagePath object
        """
        try:
            return self.images[self.index]
        except AttributeError:
            return ImagePath("", "")
        # except IndexError:
        #     # WE'RE FUCKED
        #     raise

    @property
    def imageIndex(self) -> int:
        return len(self.loadedImages) - self.loadBuffer - 1

    def bufferIndex(self, left: bool = False) -> int:
        if left:
            return self.index - self.loadBuffer
        return self.index + self.loadBuffer

    @property
    def currentImage(self) -> Image:
        return self.loadedImages[self.imageIndex][0]

    @property
    def currentSize(self) -> str:
        return self.loadedImages[self.imageIndex][1]

    @property
    def currentInfo(self) -> str:
        return ImagePath.info(self.currentImage, self.currentSize)

    @property
    def currentRatio(self) -> float:
        return ImagePath.ratio(self.currentImage)

    def moveCurrent(self, movePath):
        """
        Moves the current image using the moveImage method
        :param movePath: The place to move the image to
        """
        self.moveImage(self.current, movePath)

    # ---------------------------- SHIFT ------------------------------ #

    def nextImage(self, statusCurrent: bool = None):
        """
        The status of the current image will be updated and the
        index is incremented by 1.

        If the current image is not the last image in the list,
        if the path of the next image does not exist
        the next image will be removed and nextImage will be
        called recursively, because of the recursion the index
        is reduced by 1.
        
        If the current image is the last image a new ImagePath object
        will be appended to the list.
        If after this the length of the list is longer than maxlen
        the first element of the list will be removed.
        In case maxlen is None there is no limit to the size of
        the list.
        """
        if statusCurrent is not None:
            self.current.status = statusCurrent
        self.index += 1
        self.shiftRight()
        if self.maxlen is not None and len(self.images) > self.maxlen:
            self.removeImage(0)

    def previousImage(self):
        """
        If the current image index is 0 it will do nothing,
        otherwise it will decrease the image index by 1.
        If the path of the new current image does not exist
        it will recursively call previousImage.
        """
        if self.index == 0:
            return
        self.index -= 1
        self.shiftLeft()

    def firstImage(self):
        """
        Sets the current image index to be the index of
        the first image.
        """
        oldIndex = self.index
        self.index = 0
        if oldIndex > 0:
            self.loadStart()

    def lastImage(self):
        """
        Sets the current image index to be the index of
        the last image.
        """
        oldIndex = self.index
        self.index = len(self.images) - 1 - self.loadBuffer
        if oldIndex < len(self.images) - 1 - self.loadBuffer:
            self.loadEnd()

    def shiftLeft(self):
        """
        Shifts the loadedImage array to the left
        of the image list by one. It acts as a buffer
        for image loading and handling.
        If the current index is smaller than the loadBuffer
        it does nothing as it's already loaded everything to
        the right.

        If the path to the left does not exist, it will
        remove the element from the list through removeImage.
        This reduces the index by 1. It then recursively call
        shiftLeft until it finds an image that exists.
        """
        bufferIndex = self.bufferIndex(True)

        if self.index < self.loadBuffer:
            self.loadedImages.pop()
            return
        if not self.pathExistsAt(bufferIndex):
            self.removeImage(bufferIndex)
            self.shiftLeft()
            return
        self.loadedImages.pop()
        self.loadImage(self.imageAt(bufferIndex), left=True)

    def shiftRight(self):
        """
        Shifts the loadedImage array to the right
        of the image list by one. It acts as a buffer
        for image loading and handling.

        If the current index is higher than the
        last index of the list, minus the loadBuffer, it will
        add a new ImagePath object to the list.
        If the path at the bufferIndex does not exist, it will
        remove the image and recursively call shiftRight until
        an image that exists is found.

        The image at the bufferIndex is added to LoadedImages
        If the current index is higher than the loadBuffer it will
        remove the first element of loadedImages

        might be slightly outdated
        """
        bufferIndex = self.bufferIndex()
        lastImage = self.index > len(self.images) - 1 - self.loadBuffer
        if lastImage:
            self.images.append(self.randomImagePath)
        if not self.pathExistsAt(bufferIndex):
            self.removeImage(bufferIndex)
            self.shiftRight()
            return
        loadBufferFull = len(self.loadedImages) > 2 * self.loadBuffer + 1
        if loadBufferFull:
            self.loadedImages.pop(0)
        self.loadImage(self.imageAt(bufferIndex))

    def loadStart(self):
        """
        loads the first loadBuffer + 1 images from the
        images list. Before loading, it clears the current
        loadedImages and will add images to loadedImages until
        its length is either loadBuffer + 1 or it's no longer possible
        to load enough images from self.images.

        To know what image to load it keeps track of an index.
        Before loading an image it will check if the path of the
        ImagePath object at the index exists.
        If the path does not exist it will remove the image
        from self.images and try again.
        If the path exists it will load the image at the index
        and increment the index it will be looking at by one.
        """
        self.loadedImages.clear()
        length = self.loadBuffer + 1
        index = 0
        while len(self.loadedImages) != length and \
                len(self.images) > length:
            if not self.pathExistsAt(index):
                self.removeImage(index)
                continue
            self.loadImage(self.imageAt(index))
            index += 1
        if len(self.images) < length:
            # todo implement adding new images
            raise

    def loadEnd(self):
        """
        loads the last 2 * loadBuffer + 1 images from the
        images list. Before loading, it clears the current
        loadedImages and will add images to loadedImages until its
        length is either 2 * loadBuffer + 1 or it's no longer possible
        to load enough images from self.images.

        To know what image to load it keeps track of an index.
        The index starts at the last position of self.images
        and will decrease from there.

        Before loading an image it will check if the path of the
        ImagePath object at the index exists.
        If the path does not exist it will remove the image
        from the list.
        If the path exists it will load the image at the index.
        Regardless of removal or loading, the index will
        always be decreased by 1.
        """
        self.loadedImages.clear()
        length = self.loadBuffer * 2 + 1
        index = len(self.images) - 1
        while len(self.loadedImages) != length and \
                len(self.images) > length:
            if self.pathExistsAt(index):
                self.loadImage(self.imageAt(index), left=True)
            else:
                self.removeImage(index)
            index -= 1
        if len(self.images) < length:
            # todo implement adding new images
            raise

    # ------------------------- RANDOM IMAGE -------------------------- #

    @property
    def randomPath(self) -> str:
        """
        Chooses a random path from the path list using the
        file count as probabilities for each path.
        In case the probabilities is None, it will simply choose
        a random path.
        :return:
        Str: random path
        """
        if self.dirProbabilities is not None:
            return choices(self.dirList, weights=self.dirProbabilities, k=1)[0]
        return choice(self.dirList)

    @property
    def randomFilePath(self) -> str:
        """
        Chooses a random file path from the path provided
        by randomPath.
        If the list is empty it will remove the used directory
        from the list.
        It will load in all files from the given
        path and choose a random file from it.
        If the pathname of the new image is the exact same as
        the previous path and there are at least 2 files in the list
        it will skip to the next iteration. If the length of the
        dirList is 1 and there is only 1 file left, a popup
        indicating this will come (to be implemented).
        If there is simply 1 file in the files list it will
        choose a new directory.

        In case the file is a supported file type it will return
        the file path.

        If the file path is not supported it will try again
        up till 20 times. In case no supported file is chosen
        a new call to randomPath will be made.
        It keeps looping until a supported file is found.
        :return:
        Str: image path
        """
        while True:
            directory = self.randomPath
            files = next(walk(directory))[2]
            if len(files) == 0:
                index = self.dirList.index(directory)
                del self.dirList[index]
                del self.dirProbabilities[index]
                # todo raise
                continue
            for i in range(20):
                file = choice(files)
                pathString = path.join(directory, file)
                if len(self.images) > 1 and \
                        pathString == self.images[-1].properPath:
                    if len(self.dirList) == 1 and len(files) == 1:
                        return ''
                        # TODO break this shit cuz this is fucky wucky
                    elif len(files) == 1:
                        break
                    continue
                if file.endswith(self.config.supportedFiletype):
                    return pathString

    @property
    def randomImagePath(self) -> ImagePath:
        """
        Creates an ImagePath object using a random file path
        obtained from randomFilePath.
        :return: random ImagePath object
        """
        return ImagePath(self.randomFilePath, self.config.deletePath)

    # -------------------------- IMAGE LIST --------------------------- #

    def preLoadImages(self):
        """
        Pre loads both
        """
        for _ in range(self.loadBuffer + 1):
            imagePath: ImagePath = self.randomImagePath
            self.images.append(imagePath)
            self.loadImage(imagePath)

    def loadImage(self, imagePath: ImagePath, left=False):
        """
        Loads an image object and related information.
        It takes the Image object and makes a copy of it
        to store it into memory, it also retrieves the size
        of the image and stores it.

        The image is then added to loadedImages.
        If left is True, images are inserted at the start
        of loadedImages. The default is for left to be False,
        which has images being added to the end of the list.
        :param imagePath: Is used to load the image from
        :param left:
        """
        image: Image = imagePath.image
        size: str = imagePath.size
        loadedImage = (image.copy(), size)
        if left:
            self.loadedImages.insert(0, loadedImage)
        else:
            self.loadedImages.append(loadedImage)

    def removeImage(self, index: int):
        """
        Removes ImagePath object from the image list
        at the specified index
        :param index:
        :return:
        """
        if self.index > index:
            self.index -= 1
        del self.images[index]

    def imageAt(self, index: int) -> ImagePath:
        """
        returns the image at specified index.
        Has no safeguard for being out of bounds.
        :param index:
        :return: Specified ImagePath object
        """
        return self.images[index]

    def pathExistsAt(self, index: int) -> bool:
        """
        Checks if the path of the ImagePath object exists
        at the specified index.
        :param index:
        :return: a boolean, True if it exists
        """
        return path.exists(self.imageAt(index).path)

    @staticmethod
    def moveImage(imagePath: ImagePath, newPath: str):
        """
        The method moves an ImagePath object to a new path.
        If the new path is keep or delete, the new path will be
        set to their respective path for the current image.
        If there is no match, the newPath wil be constructed with
        the directory path and the filename. In this case makedirs is
        run to make sure that the path exists.

        After that the image is moved from its current path to the
        new path.
        In case the new path did not match anything the properPath
        is set to be the new path.

        :param imagePath: the ImagePath object
        :param newPath: The place the image should be moved to
        """
        matched = True
        match newPath:
            case 'keep':
                newPath = imagePath.properPath
            case 'delete':
                newPath = imagePath.deletePath
            case _:
                matched = False
                newPath = path.join(newPath, imagePath.filename)
                makedirs(path.dirname(newPath), exist_ok=True)
        try:
            move(imagePath.path, newPath)
        except FileNotFoundError as e:
            if not path.exists(newPath):
                # todo add implementation if neither move locations exist
                raise e
        if not matched:
            imagePath.properPath = newPath
