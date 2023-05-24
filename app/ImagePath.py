from PIL import Image
from os import path, sep


class ImagePath:

    def __init__(self, imagePath: str, deleteDir: str, status: bool = None):
        self.properPath: str = imagePath
        self.deleteDir: str = deleteDir
        self.status: bool = status

    def __repr__(self):
        return f"ImagePath({self.properPath}, status={self.status})"

    def __str__(self):
        return f"properPath: {self.properPath}\n" \
               f"path: {self.path}\n" \
               f"status: {self.status}"

    @property
    def image(self) -> Image:
        """
        Creates a Pillow Image object using the path of the
        image. This way it is not necessary to keep all images
        in memory and only keep the paths in memory.

        :return: A Pillow Image object containing the image
        """
        try:
            return Image.open(self.path)
        except:
            # todo make it do something
            raise

    # ----------------------------- PATHS ------------------------------- #

    @property
    def properPath(self) -> str:
        """
        The proper path of the object indicates the location it
        should be at. When created this path is also its original
        path. If the image gets moved to a place that is not
        a delete path the new location will become the proper path.

        :return: The proper location of the image
        """
        return self._originalPath

    @properPath.setter
    def properPath(self, properPath: str):
        """
        Sets the proper path of the image.
        Will generally only be used when creating the object.
        If the image gets moved to a non delete path the original path
        will be changed.

        :param properPath: The proper location of the image
        """
        self._originalPath = path.abspath(properPath)

    def updateProperDir(self, properDir: str):
        self.properPath = path.join(properDir, self.filename)

    @property
    def deletePath(self) -> str:
        """
        it creates the new path by joining it delete path and
        the file name together.
        :return: The path the image will be if deleted
        """
        return path.abspath(path.join(self.deleteDir, self.filename))

    @property
    def deleteDir(self) -> str:
        """
        The directory that the image will be deleted to
        :return: str
        """
        return self._deleteDir

    @deleteDir.setter
    def deleteDir(self, deleteDir: str):
        """
        Set the directory that the image will be deleted to
        :param deleteDir: str
        """
        self._deleteDir = deleteDir

    @property
    def path(self) -> str:
        """
        If the image has not been deleted it returns the
        proper path. In case the image has been deleted
        it will return the delete path

        :return: the current path to the image
        """
        if self.status is not False:
            return self.properPath
        return self.deletePath

    @property
    def filename(self) -> str:
        """
        Takes the filename from the entire path.
        Is used for display but also for creating delete
        and move paths.

        :return: image's filename
        """
        return path.basename(self.properPath)

    @property
    def pathEnd(self) -> str:
        """
        Splits the file path to return the last 4 directories.
        Is used to display additional information on the
        location the image is stored in.
        Only returns the last 4 to reduce clutter.

        :return: last 4 directories of the file path
        """
        return path.join(*self.properPath.split(sep)[-5:-1])

    # ----------------------------- INFO ------------------------------- #

    @property
    def status(self) -> bool:
        """
        Indicates if an image has been kept or deleted
        None = no judgement has been passed
        False = the image has been selected for deleting
        True = the image has been selected to keep

        :return: the status of the image
        """
        return self._status

    @status.setter
    def status(self, newStatus: bool):
        """
        The setter is used to change the status of the image.

        :param newStatus: indicates the status of the image
        """
        self._status = newStatus

    @property
    def size(self) -> str:
        """
        Gets the size of the image in KB or MB.
        Depending on the size it will apply a different formatting.
        If the size is under an MB it will be rounded to 1 decimal.
        If the size is an MB or up it will be rounded to 2 decimals.

        :return: A string of the size in KB or MB
        """
        try:
            size = path.getsize(self.path)
            if size < 1_048_576:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / 1_048_576:.2f} MB"
        except FileNotFoundError:
            return ""

    # ------------------------ STATIC Image --------------------------- #

    @staticmethod
    def resolution(image: Image) -> tuple[int, int]:
        return image.size

    @staticmethod
    def ratio(image: Image) -> float:
        """
        :return: The ratio of the image resolution
        """
        return image.width / image.height

    @staticmethod
    def info(image: Image, size: str) -> str:
        return f"res: {image.width} x {image.height}\n" \
               f"size: {size}"

