import copy
import math
import random

import cv2 as cv
import numpy as np
from Image import Image


def smoothing(arr, step):
    """Сглаживание палитры
    
    
    :param arr: палитра
    :param step: шаг сглаживания
    :return: сглаженная палитра
    """
    ret = []
    for i in range(0, math.floor(len(arr) / step)):
        r, g, b = 0, 0, 0
        for j in range(0, step):
            b += arr[i * step + j][0]
            g += arr[i * step + j][1]
            r += arr[i * step + j][2]
        ret.append([int(b / step), int(g / step), int(r / step)])
    return ret


def lum_sum(color):
    """Подсчёт яркости цвета GBR
    
    :param color: Цвет GBR
    :return: Яркость цвета GBR
    """
    arr = np.zeros(len(color))
    for i in range(0, len(color)):
        arr[i] = 0.114 * color[i][0] + 0.587 * color[i][1] + 0.299 * color[i][2]
    return arr


# Класс изображения изолятора
class IsolatorImage(Image):
    mask = None  # Маска изолятора

    localPalette = None  # Локальная палитра

    maskedImage = None  # Маскированное изображение изолятора (без фона)

    contour = None  # Контур изолятора

    middleContourIndex = int

    def ReadMask(self, maskPath=str):
        """Считывание маски изолятора с диска


        :param maskPath: Путь до маски изолятора на диске
        """
        try:
            self.mask = cv.imread(maskPath, cv.IMREAD_GRAYSCALE)

        except FileNotFoundError and FileExistsError:
            print("Указан неверный путь!")
            exit(-1)

    def MakeMaskedImage(self):
        """Создание маскированного изображения изолятора (удаление фона)

        """
        self.maskedImage = cv.bitwise_and(self.image, self.image, mask=self.mask)

    def MakePalette(self, begH, begW, h, w, smoothRange=5):
        """Создание локальной палитры

        :param begH: высота до левого верхнего угла baudbox'а
        :param begW: ширина до левого верхнего угла baudbox'а
        :param h: высота baudbox'а
        :param w: ширина baudbox'а
        :param smoothRange: Шаг сглаживания малитры (по умолчанию = 5)
        """
        self.localPalette = np.zeros((h, w, 3), dtype='uint8')
        for i in range(begH, begH + h):
            for j in range(begW, begW + w):
                if self.mask[i][j]:
                    self.localPalette[i - begH][j - begW] = self.maskedImage[i][j]

        self.localPalette = np.ravel(self.localPalette).reshape((h * w, 3))

        self.localPalette = np.unique(self.localPalette, axis=0)

        darkLimit = 100
        whiteLimit = 230
        count = 0
        while count != len(self.localPalette):
            if all([el > darkLimit for el in self.localPalette[count]]): #and all([el < whiteLimit for el in self.localPalette[count]]):
                count += 1
            else:
                self.localPalette = np.delete(self.localPalette, count, axis=0)

        # region удаление шумов в палитре (сглаживание)
        indexes = []
        for i in range(0, len(self.localPalette)):
            if all(self.localPalette[i] == [0, 0, 0]):
                indexes.append(i)

        self.localPalette = np.delete(self.localPalette, indexes, axis=0)

        b = lum_sum(self.localPalette)
        idx = b.argsort()
        self.localPalette = [self.localPalette[i] for i in idx]

        self.localPalette = np.array(smoothing(self.localPalette, smoothRange), dtype='uint8')

        # endregion

    def AddCrack(self, crackImage, begH, begW, h, w, alpha, isBlur=False, gaussianBlur=3):
        """Наложение трещины на изолятор

        :param gaussianBlur:
        :param crackImage: Изображение трещины
        :param begH: высота до левого верхнего угла baudbox'а
        :param begW: ширина до левого верхнего угла baudbox'а
        :param h: высота baudbox'а
        :param w: ширина baudbox'а
        :param alpha: альфа-канал (чем выше значение, тем прозрачнее)
        :param isBlur: нужно ли размылить трещину
        :return:
        """

        boundImage = copy.deepcopy(self.image)
        boundImage = boundImage[begH:begH + h, begW:begW + w]

        if any([el == 0 for el in boundImage.shape]):
            return np.array(0)

        for i in range(0, h):
            for j in range(0, w):
                if list(crackImage[i][j]) == [0, 0, 0]:
                    crackImage[i][j] = boundImage[i][j]

        cv.addWeighted(boundImage, alpha, crackImage, 1 - alpha, 0, boundImage)

        if isBlur:
            boundImage = cv.GaussianBlur(boundImage, (gaussianBlur, gaussianBlur), 0)

        crackedImage = copy.deepcopy(self.image)

        crackedImage[begH:begH + h, begW:begW + w] = boundImage

        # for i in range(begH, begH + h):
        #     for j in range(begW, begW + w):
        #         if list(crackImage[i - begH][j - begW]) != [0, 0, 0]:
        #             self.image[i][j] = boundImage[i - begH][j - begW]

        return crackedImage

    def GetCrackSize(self, crackScale):
        """Получить размеры трещины для данного изолятора

        :param crackScale: размер трещины относительно изолятора
        :return: высота и ширина трещины
        """

        countMaskPixel = np.count_nonzero(self.mask != 0)

        isolVolume = countMaskPixel / (self.height * self.weight)

        crackH = int((self.height * isolVolume) / crackScale)
        crackW = int((self.weight * isolVolume) / crackScale * 1.5)

        return crackH, crackW

    def MakeContour(self):
        # Находим контур маски
        contour, hierarchy = cv.findContours(self.mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        # Строим удобный контур
        self.contour = [point[0] for point in contour[0]]

        hightSlice = [point[1] for point in self.contour]

        self.middleContourIndex = hightSlice.index(max(hightSlice))

        # print(self.contour[self.middleContourIndex])
        # self.middleContourIndex = int(len(self.contour) / 2)

    def FindEdgePlace(self, h, w, side):
        # region Находим необходимые точки
        if side == "left":
            tryCount = 0
            while True:
                leftPointIndex = int(self.middleContourIndex - random.randint(0, int(len(self.contour) * 0.1)))
                leftPoint = self.contour[leftPointIndex]
                # leftPoint[1] -= 2
                # Проверяем, помещается ли трещина. Если трещина не поместилась много раз, скипаем её (возвращаем ошибку)
                try:
                    if self.mask[leftPoint[1] - h][leftPoint[0]] != 0 and self.mask[leftPoint[1]][leftPoint[0] + w] != 0:
                        break
                    elif tryCount > 10:
                        return -1, -1
                    else:
                        tryCount += 1
                except IndexError:
                    if tryCount > 10:
                        return -1, -1
                    tryCount += 1
                    continue

            return leftPoint[1] - h, leftPoint[0]
        elif side == "right":
            tryCount = 0
            while True:
                rightPointIndex = int(self.middleContourIndex + random.randint(0, int(len(self.contour) * 0.1)))
                rightPoint = self.contour[rightPointIndex]
                # rightPoint[1] -= 2
                # Проверяем, помещается ли трещина. Если трещина не поместилась много раз, скипаем её (возвращаем ошибку)
                try:
                    if self.mask[rightPoint[1] - h][rightPoint[0]] != 0 and self.mask[rightPoint[1]][rightPoint[0] - w] != 0:
                        break
                    elif tryCount > 10:
                        return -1, -1
                    else:
                        tryCount += 1
                except IndexError:
                    if tryCount > 10:
                        return -1, -1
                    tryCount += 1
                    continue

            return rightPoint[1] - h, rightPoint[0] - w

        elif side == "middle":
            middlePoint = self.contour[self.middleContourIndex]

            return middlePoint[1] - h, middlePoint[0]
        # endregion

    def FindMiddlePlace(self, h, w):
        tryCount = 0
        middleLine = self.height - int(self.height / 3)
        ringSize = 15
        while True:
            randomSide = random.choice(["right", "left", "middle"])
            edgeH, edgeW = self.FindEdgePlace(h, w, randomSide)

            if edgeH == -1:
                return -1, -1

            if randomSide == "middle" and random.choice(["left"]):
                edgeW -= w

            if middleLine >= edgeH - ringSize and tryCount < 10:
                tryCount += 1
                continue
            elif tryCount >= 10:
                return edgeH, edgeW
            else:
                tryCount1 = 0
                while True:
                    newEdgeH = random.randint(middleLine, edgeH - ringSize)
                    if ((randomSide == "left" and self.mask[newEdgeH][edgeW] == 0) or (randomSide == "right" and self.mask[newEdgeH][edgeW + w] == 0)) and tryCount1 < 5:
                        tryCount1 += 1
                        continue
                    else:
                        break

                return newEdgeH, edgeW

    def MakePaletteForBrown(self):
        self.localPalette = []
        for rVal in range(250, 255):
            for gVal in range(240, 255):
                for bVal in range(240, 255):
                    self.localPalette.append([rVal, gVal, bVal])
        self.localPalette = np.array(self.localPalette)

    def MakePaletteForWhite(self):
        self.localPalette = []
        for val in range(70, 160):
            self.localPalette.append([val, val, val])
        self.localPalette = np.array(self.localPalette)
