import os
import random
import numpy as np
import cv2 as cv

import ConstValues
from IsolatorImage import IsolatorImage
from Crack import Crack

isolatorsTypesDictionary = {"glass": 0, "ceramicbrown": 1, "ceramicwhite": 2}


# def StartCompute(isolatorsDir: str, masksDir: str, crackScale: int, isolatorType: str, isolatorColor: str, sidesForGenerate: list, crackedIsolatorsDir: str):
#     for maskName, imageName in zip(os.listdir(masksDir), os.listdir(isolatorsDir)):
#         print("Коричневый изолятор " + imageName + ":")
#         isol = IsolatorImage()
#         # Считываем изображение и маску изолятора
#         isol.ReadImage(isolatorsDir + imageName)
#         # Если изображение плохое, отсеиваем его
#         if isol.weight > isol.height:
#             del isol
#             continue
#         isol.ReadMask(masksDir + maskName)
#         # Вырезаем цветной изолятор по маске
#         isol.MakeMaskedImage()
#         # Узнаём контур изолятора для нанесения трещин
#         isol.MakeContour()
#         # Корректируем размер трещины для изолятора
#         # (Если изображение изолятора слишком маленькое, трещина должна быть меньше)
#         crackScale = random.randint(crackScale - 1, crackScale + 1)
#         cH, cW = isol.GetCrackSize(crackScale)
#
#         if sidesForGenerate.count(ConstValues.sidesForGenerate['left']) > 0:
#             # Наносим трещину слева
#             CrackAddition(isol, imageName, cH, cW, ConstValues.leftEdgeCrackDirectory,
#                           ConstValues.sidesForGenerate['left'], isolatorsTypesDictionary[isolatorType+isolatorColor],
#                           crackedIsolatorsDir)
#         if sidesForGenerate.count(ConstValues.sidesForGenerate['right']) > 0:
#             # Наносим трещину справа
#             CrackAddition(isol, imageName, cH, cW, ConstValues.rightEdgeCrackDirectory,
#                           ConstValues.sidesForGenerate['right'], isolatorsTypesDictionary[isolatorType+isolatorColor],
#                           crackedIsolatorsDir)
#         if sidesForGenerate.count(ConstValues.sidesForGenerate['middle']) > 0:
#             # Наносим трещину по середине
#             CrackAddition(isol, imageName, cH, cW, ConstValues.middleCrackDirectory,
#                           ConstValues.sidesForGenerate['middle'], isolatorsTypesDictionary[isolatorType+isolatorColor],
#                           crackedIsolatorsDir)
#
#         # Удаляем изолятор перед тем как взять новый
#         del isol


def CrackAddition(isol, imageName, cH, cW, path, side, isolParam, crackedIsolatorsDir, whiteLimit, gaussianBlurValue,
                  logs):
    crackNum = 0
    # Перебираем трещины
    for crackName in os.listdir(path):
        if crackName == "Archive":
            continue

        crack = Crack()

        # Считываем изображение трещины
        crack.ReadImage(path + crackName)

        # crack.DelRedContour()

        if crack.height >= cH:
            crack.ResizeHImage(cH)

        if crack.weight >= cW:
            crack.ResizeWImage(cW)

        # Инвертируем белый фон трещины на чёрный
        crack.InvertColors()

        if side == ConstValues.sidesForGenerate['left']:
            begH, begW = isol.FindEdgePlace(crack.height, crack.weight, "left")
        elif side == ConstValues.sidesForGenerate['right']:
            begH, begW = isol.FindEdgePlace(crack.height, crack.weight, "right")
        else:
            begH, begW = isol.FindMiddlePlace(crack.height, crack.weight)

        # Если для трещины не было найдено места на изоляторе, то скипаем трещину
        if begH == -1:
            del crack
            print(f"\tОшибка наложения трещины {crackName} - не найдено место на изоляторе.")
            logs.append(f"\tОшибка наложения трещины {crackName} - не найдено место на изоляторе.")
            continue

        # Создаём локальную палитру изолятора
        if isolParam == isolatorsTypesDictionary["glass"]:
            isol.MakePalette(begH, begW, crack.height, crack.weight)
        elif isolParam == isolatorsTypesDictionary["ceramicbrown"]:
            isol.MakePaletteForBrown()

        # Если палитра пустая, то скипаем трещину
        if len(isol.localPalette) == 0:
            del crack
            print(f"\tОшибка наложения трещины {crackName} - мало цветов в палитре")
            logs.append(f"\tОшибка наложения трещины {crackName} - мало цветов в палитре")
            continue

        # region Выводим палитру
        # printPalette = np.zeros((50, len(isol.localPalette), 3), dtype='uint8')

        # for i in range(0, 50):
        #     printPalette[i] = isol.localPalette

        # cv.imshow("Palette", printPalette)
        # cv.moveWindow('Palette', 400, 300)
        # cv.waitKey(100)
        # endregion

        # region Вывод трещины до и после палитризации
        # cv.imshow(f"Crack {crackName}", crack.image)
        # cv.moveWindow(f'Crack {crackName}', 400 + isol.weight + 10, 400)
        # cv.waitKey(100)

        # Палитризуем трещину
        FromPalletToImage(isol.localPalette, crack.image, whiteLimit)

        # cv.imshow(f"Paletted Crack {crackName}", crack.image)
        # cv.moveWindow(f"Paletted Crack {crackName}", 400 + isol.weight + 10, 500)
        # cv.waitKey(100)
        # endregion

        if len(crack.image) == 0:
            del crack
            print(f"\tОшибка наложения трещины {crackName} - трещина сломалась")
            logs.append(f"\tОшибка наложения трещины {crackName} - трещина сломалась")
            continue

        # Наложение трещины на изображение изолятора
        if isolParam == isolatorsTypesDictionary["glass"]:
            crackedImage = isol.AddCrack(crack.image, begH, begW, crack.height, crack.weight, 0.25,
                                         gaussianBlur=gaussianBlurValue)
        else:
            crackedImage = isol.AddCrack(crack.image, begH, begW, crack.height, crack.weight, 0.25, True,
                                         gaussianBlurValue)

        if any([el == 0 for el in crackedImage.shape]):
            del crack
            print(f"\tОшибка наложения трещины {crackName} - изолятор сломался")
            logs.append(f"\tОшибка наложения трещины {crackName} - изолятор сломался")
            continue

        # region Обводка трещины
        # cv.rectangle(crackedImage, [begW, begH],
        #              [begW + crack.weight, begH + crack.height], (0, 255, 0), 1)

        # Вывод изолятора с трещиной
        # cv.imshow("Cracked isol", crackedImage)
        # cv.moveWindow('Cracked isol', 400, 400)
        # cv.waitKey(5000)
        # # cv.waitKey()
        # cv.destroyAllWindows()
        # endregion

        mainPath = os.getcwd()

        os.chdir(crackedIsolatorsDir)

        saveName = f"{'l' if side == ConstValues.sidesForGenerate['left'] else 'r' if side == ConstValues.sidesForGenerate['right'] else 'm'}" + crackName[:-4] + "_" + imageName
        # Сохранение изолятора с трещиной
        issaved = cv.imwrite(saveName, crackedImage)

        if issaved:
            print(f"\tНаложена трещина: {crackName}. Сохранённое изображение: {saveName}")
            logs.append(f"\tНаложена трещина: {crackName}. Сохранённое изображение: {saveName}")

        os.chdir(mainPath)
        crackNum += 1
        del crack


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
