import copy
import sys

import cv2 as cv
from Image import Image
import numpy as np


# Класс трещины
class Crack(Image):

    alphaChannel = None

    def ReadImage(self, imagePath=str):
        """Считать изображение с диска

        :param imagePath: Путь до изображения на диске
        """
        try:
            # Считываем изображение
            self.image = cv.imread(imagePath, cv.IMREAD_UNCHANGED)
            self.height = self.image.shape[0]
            self.weight = self.image.shape[1]

            # np.set_printoptions(threshold=sys.maxsize)
            # print(self.image)

            # Трэшхолд для a-канала
            for i in range(0, self.height):
                for j in range(0, self.weight):
                    if self.image[i][j][-1] < 26:
                        self.image[i][j] = np.zeros(4, dtype='uint8')

            # Сохраняем значения a-канала
            self.alphaChannel = self.image[:, :, 3]
            # делаем изображение RGB
            self.image = cv.cvtColor(self.image, cv.COLOR_BGRA2BGR)

        except FileNotFoundError and FileExistsError:
            print("Указан неверный путь!")
            exit(-1)

    def InvertColors(self):
        """Инверсия цветов фона (с белого на чёрный)

        """
        for i in range(0, self.height):
            for j in range(0, self.weight):
                if list(self.image[i][j]) == [255, 255, 255]:
                    self.image[i][j] = [0, 0, 0]


    def ResizeHImage(self, h):
        """Изменить размер трещины

        :param h: Новая высота трещины
        :param w: Новая ширина трещины
        """
        self.image = cv.resize(self.image, (self.weight, h))
        self.height = h


    def ResizeWImage(self, w):
        """Изменить размер трещины

        :param h: Новая высота трещины
        :param w: Новая ширина трещины
        """
        self.image = cv.resize(self.image, (w, self.height))
        self.weight = w


    def DelRedContour(self):
        kernel = np.ones((3, 3), 'uint8')
        dilate_crack_mask = cv.dilate(self.image, kernel, iterations=1)
        self.image = cv.erode(dilate_crack_mask, kernel, iterations=1)
