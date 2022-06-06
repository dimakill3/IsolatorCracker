import math

import cv2 as cv

import ConstValues
import DefectImposeManager
from BasePoints import BasePoints
from Image import Image
import numpy as np


# Класс изображения дефекта
from IsolatorImage import IsolatorImage


class DefectImage(Image):

    alphaChannel = None

    contour = None

    boundXBegin = int

    boundYBegin = int

    def ReadImage(self, imagePath=str):
        """Считать изображение с диска

        :param imagePath: Путь до изображения на диске
        """
        try:
            # Считываем изображение
            self.image = cv.imread(imagePath, cv.IMREAD_UNCHANGED)
            self.height = self.image.shape[0]
            self.weight = self.image.shape[1]

            # Трэшхолд для a-канала
            for i in range(0, self.height):
                for j in range(0, self.weight):
                    if self.image[i][j][-1] < 26:
                        self.image[i][j] = np.zeros(4, dtype='uint8')

            # Сохраняем значения a-канала
            self.alphaChannel = self.image[:, :, 3]
            # делаем изображение RGB
            self.image = cv.cvtColor(self.image, cv.COLOR_BGRA2BGR)
            self.imageName = imagePath.split('/')[-1]

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
        """Изменить размер дефекта

        :param h: Новая высота дефекта
        """
        self.image = cv.resize(self.image, (self.weight, h))
        self.height = h

    def ResizeWImage(self, w):
        """Изменить размер дефекта

        :param w: Новая ширина дефекта
        """
        self.image = cv.resize(self.image, (w, self.height))
        self.weight = w

    def GenerateDefect(self, defectType: int, isolator: IsolatorImage, side: int):
        self.image = np.zeros((isolator.height, isolator.weight), dtype='uint8')

        if defectType == ConstValues.defectTypes['straight']:
            self.GenerateStraightCrack(isolator.basePoints, side)
        elif defectType == ConstValues.defectTypes['round']:
            self.GenerateRoundCrack(isolator.basePoints, side)

        kernel = DefectImposeManager.CreateCircularMask(5, 5, radius=2)
        dilate_crack_mask = cv.dilate(self.image, kernel, iterations=1)
        self.image = cv.erode(dilate_crack_mask, kernel, iterations=1)

        contour = np.array(isolator.contour)

        for i in range(0, isolator.height):
            for j in range(0, isolator.weight):
                if self.image[i][j] and (cv.pointPolygonTest(contour, [j, i], False) < 0):
                    self.image[i][j] = 0

        countour, hierarchy = cv.findContours(self.image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        self.boundXBegin, self.boundYBegin, self.weight, self.height = cv.boundingRect(countour[0])

        boundImage = np.zeros((self.height, self.weight), dtype='uint8')
        for i in range(0, self.height):
            for j in range(0, self.weight):
                boundImage[i][j] = self.image[i + self.boundYBegin][j + self.boundXBegin]

        self.image = np.array(boundImage)

        self.contour, hierarchy = cv.findContours(self.image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    def GenerateStraightCrack(self, basePoints: BasePoints, side):
        beginPoint = None
        endPoint = None

        if side == ConstValues.sidesForGenerate['left']:
            beginPoint = basePoints.leftPoint
            endPoint = basePoints.dopLeftPoint
        elif side == ConstValues.sidesForGenerate['right']:
            beginPoint = basePoints.rightPoint
            endPoint = basePoints.dopRightPoint
        elif side == ConstValues.sidesForGenerate['middle']:
            beginPoint = basePoints.middlePoint
            endPoint = basePoints.dopMiddlePoint

        X = np.linspace(beginPoint[0], endPoint[0], 10)
        Y = np.linspace(beginPoint[1], endPoint[1], 10)
        thick = 5
        for i in range(0, len(X) - 1):
            cv.line(self.image, [int(X[i]), int(Y[i])], [int(X[i + 1]), int(Y[i + 1])], 255, thickness=thick)
            if i % int((len(X) - 1) / 4) == 0 and thick != 1 and i != 0:
                thick -= 1

    def GenerateRoundCrack(self, basePoints: BasePoints, side):
        beginPoint = None
        endPoint = None
        dopPoint = None

        if side == ConstValues.sidesForGenerate['left']:
            beginPoint = basePoints.leftPoint
            endPoint = basePoints.dopLeftPoint
            dopPoint = basePoints.middlePoint
        elif side == ConstValues.sidesForGenerate['right']:
            beginPoint = basePoints.rightPoint
            endPoint = basePoints.dopRightPoint
            dopPoint = basePoints.middlePoint
        elif side == ConstValues.sidesForGenerate['middle']:
            beginPoint = basePoints.leftPoint
            endPoint = basePoints.dopMiddlePoint
            dopPoint = basePoints.rightPoint

        beziePoints = DefectImposeManager.GetBeziePoints(0.01, [beginPoint, endPoint, dopPoint])
        beziePoints = [[int(beziePoints[i][0]), int(beziePoints[i][1])] for i in range(0, len(beziePoints))]

        for i in range(1, len(beziePoints)):
            if i <= (len(beziePoints) + 1) / 4 or i + (len(beziePoints) + 1) / 4 > len(beziePoints):
                cv.line(self.image, beziePoints[i - 1], beziePoints[i], 255, thickness=3)
            elif i <= (len(beziePoints) + 1) / 3 or i + (len(beziePoints) + 1) / 3 > len(beziePoints):
                cv.line(self.image, beziePoints[i - 1], beziePoints[i], 255, thickness=4)
            else:
                cv.line(self.image, beziePoints[i - 1], beziePoints[i], 255, thickness=5)

    def FillDefect(self, fillImage):
        coloredDefect = np.zeros((self.height, self.weight, 3), dtype='uint8')

        for i in range(0, self.height):
            for j in range(0, self.weight):
                if self.image[i][j]:
                    coloredDefect[i][j] = fillImage[i][j]
                else:
                    coloredDefect[i][j] = [0, 0, 0]

        self.image = coloredDefect

    def RangeFillDefect(self, palette):

        coloredDefect = np.zeros((self.height, self.weight, 3), dtype='uint8')

        for i in range(self.height):
            for j in range(self.weight):
                if self.image[i][j]:
                    distance = math.ceil(cv.pointPolygonTest(self.contour[0], [j, i], True))
                    if distance == 0:
                        distance = 4
                    coloredDefect[i][j] = palette[int((len(palette) - 1) * (1 - abs(1 / distance)))]

        self.image = coloredDefect
