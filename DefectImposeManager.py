import math
import os
import random
from PyQt5 import QtWidgets
import numpy as np
import cv2 as cv
import ConstValues
from IsolatorImage import IsolatorImage
from DefectImage import DefectImage
from perlin_noise import PerlinNoise


def DefectAddition(isolator: IsolatorImage, cracksPath: str, crackScale: int, whiteLimit: int, gaussianBlurValue: int,
                   side: int, isolatorType: int, crackedIsolatorsDir: str, logs: QtWidgets.QTextEdit):
    crackNum = 0
    # Перебираем трещины
    for crackName in os.listdir(cracksPath):
        if crackName == "Archive":
            continue

        crack = DefectImage()
        # Считываем изображение трещины
        crack.ReadImage(cracksPath + crackName)
        # Изменяем размер дефекта в соответсвии с размером изолятора
        cH, cW = isolator.GetCrackSize(crackScale)
        if crack.height >= cH:
            crack.ResizeHImage(cH)
        if crack.weight >= cW:
            crack.ResizeWImage(cW)
        # Инвертируем белый фон трещины на чёрный
        crack.InvertColors()
        # Накладываем дефект на заданную сторону
        if side == ConstValues.sidesForGenerate['left']:
            begH, begW = isolator.FindEdgePlace(crack.weight, crack.height, "left")
        elif side == ConstValues.sidesForGenerate['right']:
            begH, begW = isolator.FindEdgePlace(crack.weight, crack.height, "right")
        else:
            begH, begW = isolator.FindMiddlePlace(crack.weight, crack.height)

        # Если для трещины не было найдено места на изоляторе, то скипаем трещину
        if begH == -1:
            del crack
            print(f"\tОшибка наложения трещины {crackName} - не найдено место на изоляторе.")
            logs.append(f"\tОшибка наложения трещины {crackName} - не найдено место на изоляторе.")
            continue

        # Создаём локальную палитру изолятора
        if isolatorType == ConstValues.isolatorsTypes["glass"]:
            isolator.MakePalette(begW, begH, crack.weight, crack.height)
        elif isolatorType == ConstValues.isolatorsTypes["ceramicbrown"]:
            isolator.MakePaletteForBrown()
        elif isolatorType == ConstValues.isolatorsTypes["ceramicwhite"]:
            isolator.MakePaletteForWhite()
            whiteLimit = 255


        # Если палитра пустая, то скипаем трещину
        if len(isolator.localPalette) < 4:
            del crack
            print(f"\tОшибка наложения трещины {crackName} - мало цветов в палитре")
            logs.append(f"\tОшибка наложения трещины {crackName} - мало цветов в палитре")
            continue

        # Палитризуем трещину
        FromPalletToImage(isolator.localPalette, crack.image, whiteLimit)

        if len(crack.image) == 0:
            del crack
            print(f"\tОшибка наложения трещины {crackName} - трещина сломалась")
            logs.append(f"\tОшибка наложения трещины {crackName} - трещина сломалась")
            continue

        # Наложение трещины на изображение изолятора
        if isolatorType == ConstValues.isolatorsTypes["glass"]:
            crackedImage = isolator.AddDefect(crack.image, begW, begH, crack.weight, crack.height, 0.15, True,
                                              gaussianBlurValue)
        else:
            crackedImage = isolator.AddDefect(crack.image, begW, begH, crack.weight, crack.height, 0.25, True,
                                              gaussianBlurValue)

        if any([el == 0 for el in crackedImage.shape]):
            del crack
            print(f"\tОшибка наложения трещины {crackName} - изолятор сломался")
            logs.append(f"\tОшибка наложения трещины {crackName} - изолятор сломался")
            continue

        mainPath = os.getcwd()

        os.chdir(crackedIsolatorsDir)

        saveName = f"{'l' if side == ConstValues.sidesForGenerate['left'] else 'r' if side == ConstValues.sidesForGenerate['right'] else 'm'}" + crackName[:-4] + "_" + isolator.imageName
        # Сохранение изолятора с трещиной
        isSaved = cv.imwrite(saveName, crackedImage)

        if isSaved:
            print(f"\tНаложена трещина: {crackName}. Сохранённое изображение: {saveName}")
            logs.append(f"\tНаложена трещина: {crackName}. Сохранённое изображение: {saveName}")

        os.chdir(mainPath)
        crackNum += 1
        del crack


def DefectGeneration(isolator: IsolatorImage, side: int, smooth: int, gaussianBlurValue:int, isolatorType: int,
                     fillAlgorithm: int, crackedIsolatorsDir: str, logs: QtWidgets.QTextEdit):
    for defectTypeNum in range(0, ConstValues.realizedDefectTypes):
        defect = DefectImage()
        defect.GenerateDefect(defectTypeNum, isolator, side)

        # Создаём локальную палитру изолятора
        if isolatorType == ConstValues.isolatorsTypes["glass"]:
            isolator.MakePalette(defect.boundXBegin, defect.boundYBegin, defect.weight, defect.height, smooth)
        elif isolatorType == ConstValues.isolatorsTypes["ceramicbrown"]:
            isolator.MakePaletteForBrown()
        elif isolatorType == ConstValues.isolatorsTypes["ceramicwhite"]:
            isolator.MakePaletteForWhite()

        # Если палитра пустая, то скипаем трещину
        if len(isolator.localPalette) < 4:
            print(f"\tОшибка наложения трещины Type {defectTypeNum}, сторона {'l' if side == ConstValues.sidesForGenerate['left'] else 'r' if side == ConstValues.sidesForGenerate['right'] else 'm'} - мало цветов в палитре")
            logs.append(f"\tОшибка наложения трещины Type {defectTypeNum}, сторона {'l' if side == ConstValues.sidesForGenerate['left'] else 'r' if side == ConstValues.sidesForGenerate['right'] else 'm'} - мало цветов в палитре")
            del defect
            continue

        if fillAlgorithm == ConstValues.fillAlgorithms['voronoi']:
            pointsCount = 100 + int(((defect.height * defect.weight) / (isolator.height * isolator.weight)) * 100) * 2
            VoronoiFilling(isolator, defect, pointsCount)
        elif fillAlgorithm == ConstValues.fillAlgorithms['perlin']:
            PerlinFilling(isolator, defect)
        elif fillAlgorithm == ConstValues.fillAlgorithms['range']:
            RangeFilling(isolator, defect)

        # Наложение трещины на изображение изолятора
        if isolatorType == ConstValues.isolatorsTypes["glass"]:
            crackedImage = isolator.AddDefect(defect.image, defect.boundXBegin, defect.boundYBegin, defect.weight,
                                              defect.height, 0.15, True)
        else:
            crackedImage = isolator.AddDefect(defect.image, defect.boundXBegin, defect.boundYBegin, defect.weight,
                                              defect.height, 0.25, True, gaussianBlurValue)


        if any([el == 0 for el in crackedImage.shape]):
            print(f"\tОшибка наложения трещины Type {defectTypeNum}, сторона {'l' if side == ConstValues.sidesForGenerate['left'] else 'r' if side == ConstValues.sidesForGenerate['right'] else 'm'} - изолятор сломался")
            logs.append(f"\tОшибка наложения трещины Type {defectTypeNum}, сторона {'l' if side == ConstValues.sidesForGenerate['left'] else 'r' if side == ConstValues.sidesForGenerate['right'] else 'm'} - изолятор сломался")
            del defect
            continue

        mainPath = os.getcwd()
        os.chdir(crackedIsolatorsDir)
        saveName = f"Type_{defectTypeNum} {'l' if side == ConstValues.sidesForGenerate['left'] else 'r' if side == ConstValues.sidesForGenerate['right'] else 'm'} {isolator.imageName}"
        # Сохранение изолятора с трещиной
        isSaved = cv.imwrite(saveName, crackedImage)

        if isSaved:
            print(f"\tНаложена трещина: Type {defectTypeNum}, сторона {'l' if side == ConstValues.sidesForGenerate['left'] else 'r' if side == ConstValues.sidesForGenerate['right'] else 'm'}. Сохранённое изображение: {saveName}")
            logs.append(f"\tНаложена трещина: Type {defectTypeNum}, сторона {'l' if side == ConstValues.sidesForGenerate['left'] else 'r' if side == ConstValues.sidesForGenerate['right'] else 'm'}. Сохранённое изображение: {saveName}")

        os.chdir(mainPath)
        del defect


def LocalSum(image, i, j, rang):
    sumColor = [0, 0, 0]
    count = 0
    fromI = i - rang
    toI = i + rang + 1

    fromJ = j - rang
    toJ = j + rang + 1

    if i - rang < 0:
        fromI = 0

    if i + rang > len(image) - 1:
        toI = len(image)

    if j - rang < 0:
        fromJ = 0

    if j + rang > len(image[-1]) - 1:
        toJ = len(image[-1])

    for _i in range(fromI, toI + 1):
        for _j in range(fromJ, toJ + 1):
            try:
                sumColor[0] += image[_i][_j][0]
                sumColor[1] += image[_i][_j][1]
                sumColor[2] += image[_i][_j][2]
                count += 1
            except IndexError:
                continue

    return [int(el / count) for el in sumColor]


def FromPalletToImage(imagePalette, crackImage, whiteLimit):
    """Палитризирует переданное изображение


    :param imagePalette: Палитра
    :param crackImage: Палитризуемое изображение
    :param whiteLimit: Значение, ограничивающее "белые" цвета (цвет GBR, у которого значения всех каналов выше whiteLimit считаются "белыми")
    """
    distance = np.linalg.norm(crackImage[:, :, None] - imagePalette[None, None, :], axis=3)
    # palettised = np.argmin(distance, axis=2)
    palettised = np.argmax(distance, axis=2)
    for i in range(palettised.shape[0]):
        for j in range(palettised.shape[1]):
            if list(crackImage[i][j]) != [0, 0, 0] and (all([el <= whiteLimit for el in crackImage[i][j]])):
                crackImage[i][j] = imagePalette[palettised[i][j]]


def VoronoiFilling(isolator: IsolatorImage, defect: DefectImage, pointsCount):
    rect = (0, 0, defect.weight, defect.height)
    subdiv = cv.Subdiv2D(rect)

    points = [(random.randint(0, defect.weight - 1), random.randint(0, defect.height - 1)) for _ in range(0, pointsCount)]

    for p in points:
        subdiv.insert(p)

    imgVoronoi = np.zeros((defect.height, defect.weight, 3), dtype='uint8')
    DrawVoronoi(imgVoronoi, subdiv, isolator.localPalette)

    defect.FillDefect(imgVoronoi)


def DrawVoronoi(image, subdiv, palette):
    (facets, centers) = subdiv.getVoronoiFacetList([])
    palette_light = palette[int(len(palette) * 9 / 10):]
    palette_dark = palette[: int(len(palette) * 4 / 5)]

    for i in range(0, len(facets)):
        ifacet_arr = []
        for f in facets[i]:
            ifacet_arr.append(f)

        ifacet = np.array(ifacet_arr, int)

        if i % 2 == 0:
            color = list(palette_light[int((len(palette_light) - 1) * random.uniform(0, 1))])
        else:
            color = list(palette_dark[int((len(palette_dark) - 1) * random.uniform(0, 1))])

        color = [int(x) for x in color]

        cv.fillConvexPoly(image, ifacet, color, cv.LINE_AA, 0)
        ifacets = np.array([ifacet])
        cv.polylines(image, ifacets, False, color, 0, cv.LINE_AA, 0)


def PerlinFilling(isolator: IsolatorImage, defect: DefectImage):
    perlinNoise1 = PerlinNoise(octaves=3, seed=random.randint(1, 1000))
    perlinNoise2 = PerlinNoise(octaves=3, seed=random.randint(1, 1000))
    perlinNoise3 = PerlinNoise(octaves=100, seed=random.randint(1, 1000))

    noiseImage = np.array([[(perlinNoise1([i / defect.weight, j / defect.height])) +
                            (perlinNoise2([i / defect.weight, j / defect.height])) * 0.5 +
                            (perlinNoise3([i / defect.weight, j / defect.height])) * 0.25
                            for j in range(defect.weight)] for i in range(defect.height)])

    perlinPalette = np.unique(np.ravel(noiseImage), axis=0)
    accordanceColors = [isolator.localPalette.tolist()[math.floor(perlinPalette[i] * len(isolator.localPalette))]
                        for i in range(len(perlinPalette))]
    coloredNoise = np.array([[accordanceColors[perlinPalette.tolist().index(noiseImage[i][j])]
                            for j in range(0, defect.weight)]
                            for i in range(0, defect.height)], dtype='uint8')

    defect.FillDefect(coloredNoise)


def RangeFilling(isolator: IsolatorImage, defect: DefectImage):
    defect.RangeFillDefect(isolator.localPalette)


def CreateCircularMask(h, w, center=None, radius=None):
    """ Генерация маски круга
        :param h: Высота маски
        :param w: Ширина маски
        :param center: Центр круга (по умолчаю - центр изображения)
        :param radius: Радиус круга (по умолчанию - максимально возможный для данного изображения, т.е. половина)
        :return: Маска круга
        """
    if center is None:
        center = (int(w / 2), int(h / 2))
    if radius is None:
        radius = min(center[0], center[1], w - center[0], h - center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)
    circle_mask = np.zeros((h, w), dtype='uint8')
    for i in range(len(dist_from_center)):
        for j in range(len(dist_from_center[i])):
            if dist_from_center[i][j] <= radius:
                circle_mask[i][j] = 255
    return circle_mask


def CalcSquareBezie(t: float, points):
    tmp = 1 - t
    x = tmp ** 2 * points[0][0] + 2 * t * tmp * points[1][0] + t ** 2 * points[2][0]
    y = tmp ** 2 * points[0][1] + 2 * t * tmp * points[1][1] + t ** 2 * points[2][1]
    return (x, y)


def GetBeziePoints(dis, points):
    if dis <= 0:
        return [(0, 0)]
    t = 0
    res = []
    while t < 1:
        res.append(CalcSquareBezie(t, points))
        t += dis
    return np.array(res)
