import math
import random
import sys
import os
import DefectImposeManager
import ConstValues

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from IsolatorImage import IsolatorImage

from Properties import Properties
from design.gui import Ui_MainWindow

tabPages = {'tabCompute': 0, 'tabProperties': 1}


# Класс-расширение GUI для реализации логики
class IsolatorCracker(QtWidgets.QMainWindow):
    properties = Properties()
    optimalValues = ConstValues.OptimalValues()
    ComputeThreadInstance = None
    gaussianBlurLastValue = 0

    # Инициализируем расширяющий класс
    def __init__(self):
        super(IsolatorCracker, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initGUI()

    # Инициализируем логику GUI
    def initGUI(self):
        """
        Настрйока и реализация логики интерфейса
        :return:
        """
        # Скрываем опциональные элементы
        self.ui.gbCeramicColor.setVisible(False)
        self.ui.gbGenerateParams.setVisible(False)
        # Указываем путь по умолчанию для треснувших изоляторов
        self.ui.lePathToFolder.setText(ConstValues.crackedGlassIsolDirectory)
        # Привязываем кнопки к действиям при нажатии
        self.ui.btnChooseFolder.clicked.connect(self.selectFolder)
        self.ui.btnCompute.clicked.connect(self.compute)
        self.ui.btnStop.clicked.connect(self.stopCompute)
        self.ui.cbLeft.clicked.connect(lambda: self.sidesParameterChanged(ConstValues.sidesForGenerate['left']))
        self.ui.cbMiddle.clicked.connect(lambda: self.sidesParameterChanged(ConstValues.sidesForGenerate['middle']))
        self.ui.cbRight.clicked.connect(lambda: self.sidesParameterChanged(ConstValues.sidesForGenerate['right']))
        self.ui.btnGlassMode.clicked.connect(lambda: self.parametersModeChanged(ConstValues.isolatorsTypes['glass']))
        self.ui.btnCeramicBrownMode.clicked.connect(lambda: self.parametersModeChanged(ConstValues.isolatorsTypes['ceramicbrown']))
        self.ui.btnCeramicWhiteMode.clicked.connect(lambda: self.parametersModeChanged(ConstValues.isolatorsTypes['ceramicwhite']))
        # Инициализируем слайдеры
        self.initSlider(self.ui.lblWhiteLimitMin, self.ui.lblWhiteLimitMax, ConstValues.minWhiteLimit,
                        ConstValues.maxWhiteLimit, self.optimalValues.optimalWhiteLimit,
                        self.ui.sliderWhiteLimit, self.ui.leWhiteLimitValue)

        self.initSlider(self.ui.lblGaussianBlurMin, self.ui.lblGaussianBlurMax, ConstValues.minGaussianBlur,
                        ConstValues.maxGaussianBlur, self.optimalValues.optimalGaussianBlur,
                        self.ui.sliderGaussianBlur, self.ui.leGaussianBlurValue)

        self.gaussianBlurLastValue = self.ui.sliderGaussianBlur.value()

        self.ui.sliderGaussianBlur.valueChanged.connect(lambda: self.customizeGaussianSliderStep())

        self.initSlider(self.ui.lblCrackScaleMin, self.ui.lblCrackScaleMax, ConstValues.minCrackScale,
                        ConstValues.maxCrackScale, self.optimalValues.optimalCrackScale,
                        self.ui.sliderCrackScale, self.ui.leCrackScaleValue)

        self.initSlider(self.ui.lblPaletteSmoothingMin, self.ui.lblPaletteSmoothingMax, ConstValues.minPaletteSmoothing,
                        ConstValues.maxPaletteSmoothing, self.optimalValues.optimalPaletteSmoothing,
                        self.ui.sliderPaletteSmoothing, self.ui.lePaletteSmoothingValue)

        # Логика Radio Button\
        self.ui.rbCeramic.toggled.connect(lambda: self.setElementVisible(self.ui.gbCeramicColor, True))
        self.ui.rbGlass.toggled.connect(lambda: self.setElementVisible(self.ui.gbCeramicColor, False))

        self.ui.rbCrackGeneration.toggled.connect(lambda: self.setElementVisible(self.ui.gbGenerateParams, True))
        self.ui.rbCrackAddition.toggled.connect(lambda: self.setElementVisible(self.ui.gbGenerateParams, False))
        # Логика смены страницы
        self.ui.mainTabWidget.currentChanged.connect(self.mainTabWidgetPageChanged)

    def selectFolder(self):
        """
        Выбор директории
        :return:
        """
        pathToFolder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        if pathToFolder == "":
            pathToFolder = ConstValues.crackedGlassIsolDirectory
        self.ui.lePathToFolder.setText(pathToFolder)

    def compute(self):
        """
        Запуск генерации в отдельном потоке
        :return:
        """
        # Отключаем кликабельность части интерфейса
        self.freezeSomeUIWhileCompute(True)
        # Чистим логи
        self.ui.teLogs.clear()
        self.properties.setCrackedIsolatorsDir(self.ui.lePathToFolder.text() + '/')
        self.properties.setHowIsolatorsToCompute(int(self.ui.leHowIsolatorsCompute.text()))
        # Запускаем поток генерации
        self.ComputeThreadInstance = ComputeThread(properties=self.properties, logs=self.ui.teLogs)
        self.ComputeThreadInstance.start()
        # Подписываемся на сигналы из потока
        self.ComputeThreadInstance.incProgressBar.connect(self.increaceProgressBarValue)
        self.ComputeThreadInstance.computeFinished.connect(self.computeFinished)
        self.ComputeThreadInstance.computeStopped.connect(self.computeFinished)

    def stopCompute(self):
        """
        Преждевременная остановка генерации
        :return:
        """
        # Посылаем потоку запрос на его остановку (получение сигнала обрабатывается внутри потока)
        self.ComputeThreadInstance.requestInterruption()

    def computeFinished(self, computeResult, crackedIsolatorsCount):
        """
        Действия при завершении генерации
        :param computeResult: Результат генерации
        :param crackedIsolatorsCount: Количество обработанных изоляторов
        :return:
        """
        self.freezeSomeUIWhileCompute(False)
        self.ui.progressBar.setValue(0)
        self.ComputeThreadInstance.stop()
        del self.ComputeThreadInstance
        self.showComputeResult(computeResult, crackedIsolatorsCount)

    def freezeSomeUIWhileCompute(self, freeze: bool):
        """
        Влияет на кликабельность части интерфейса
        :param freeze: заморозить/разморозить интерфейс
        :return:
        """
        self.enableCompute(not freeze)
        self.ui.btnStop.setEnabled(freeze)
        self.ui.mainTabWidget.setTabEnabled(tabPages['tabProperties'], not freeze)

    def showComputeResult(self, result: str, crackedIsolatorsCount: int):
        """
        Вывод результатов генерации
        :param result: Результат генерации
        :param crackedIsolatorsCount: Количество обработанных изоляторов
        :return:
        """
        QtWidgets.QMessageBox.information(self, "Результат",
                                          result + f" Обработано {crackedIsolatorsCount} из {self.ui.leHowIsolatorsCompute.text()} изоляторов",
                                          QtWidgets.QMessageBox.Ok)

    def increaceProgressBarValue(self, value):
        """
        Изменения значения ProgressBar
        :param value: значение, которое будет установлено для ProgressBar
        :return:
        """
        self.ui.progressBar.setValue(value)

    def readProperties(self):
        """
        Считать настройки генерации
        :return:
        """
        isolatorsDir = ""
        masksDir = ""
        isolatorType = ""
        isolatorColor = ""
        if self.ui.rbGlass.isChecked():
            isolatorsDir = ConstValues.isolatorDirectory
            masksDir = ConstValues.maskDirectory
            isolatorType = "glass"
        elif self.ui.rbBrown.isChecked():
            isolatorsDir = ConstValues.ceramicBrownIsolDirectory
            masksDir = ConstValues.ceramicBrownMaskDirectory
            isolatorType = "ceramic"
            isolatorColor = "brown"
        elif self.ui.rbWhite.isChecked():
            isolatorsDir = ConstValues.ceramicWhiteIsolDirectory
            masksDir = ConstValues.ceramicWhiteMaskDirectory
            isolatorType = "ceramic"
            isolatorColor = "white"

        computeType = 0

        if self.ui.rbCrackAddition.isChecked():
            computeType = ConstValues.computeTypes['addition']
        elif self.ui.rbCrackGeneration.isChecked():
            computeType = ConstValues.computeTypes['generation']

        fillAlgorithm = 0

        if self.ui.rbVoronoyDiagram.isChecked():
            fillAlgorithm = ConstValues.fillAlgorithms['voronoi']
        elif self.ui.rbPerlinNoise.isChecked():
            fillAlgorithm = ConstValues.fillAlgorithms['perlin']
        elif self.ui.rbRangeInCrack.isChecked():
            fillAlgorithm = ConstValues.fillAlgorithms['range']

        self.properties = Properties(isolatorType, isolatorColor, isolatorsDir, masksDir, crackScale=self.ui.sliderCrackScale.value(),
                                     whiteLimit=self.ui.sliderWhiteLimit.value(), gaussianBlur=self.ui.sliderGaussianBlur.value(),
                                     paletteSmoothing=self.ui.sliderPaletteSmoothing.value(), computeType=computeType, fillAlgorithm=fillAlgorithm)

        if self.ui.cbLeft.isChecked():
            self.properties.addSideForGenerate('left')

        if self.ui.cbMiddle.isChecked():
            self.properties.addSideForGenerate('middle')

        if self.ui.cbRight.isChecked():
            self.properties.addSideForGenerate('right')

    def mainTabWidgetPageChanged(self):
        """
        Смена страницы
        :return:
        """
        if tabPages[self.ui.mainTabWidget.currentWidget().objectName()] == tabPages['tabCompute']:
            self.readProperties()
            neededExtention = '.png'

            numFiles = 0
            for file in os.listdir(self.properties.isolatorsDir):
                if os.path.isfile(os.path.join(self.properties.isolatorsDir, file)) and file.join(neededExtention):
                    numFiles += 1

            if numFiles == 0:
                self.enableCompute(False)
            else:
                self.enableCompute(True)

            strFoundIsolators = f"Found {numFiles} {self.properties.isolatorType + '' + self.properties.isolatorColor} isolators"

            self.initSlider(self.ui.lblComputeIsolatorsMin, self.ui.lblComputeIsolatorsMax,
                            1, numFiles, numFiles, self.ui.sliderComputeIsolators, self.ui.leHowIsolatorsCompute)

            self.ui.lblFoundIsolators.setText(strFoundIsolators)

    def enableCompute(self, enable: bool):
        """
        Изменяем возможность запуска обработки
        :param enable: Разрешить или запретить запуск обработки
        :return:
        """
        self.ui.btnCompute.setEnabled(enable)
        self.ui.lblComputeIsolatorsMin.setEnabled(enable)
        self.ui.lblComputeIsolatorsMax.setEnabled(enable)
        self.ui.sliderComputeIsolators.setEnabled(enable)
        self.ui.leHowIsolatorsCompute.setEnabled(enable)
        self.ui.btnChooseFolder.setEnabled(enable)

    def setElementVisible(self, element: QtWidgets, visible: bool):
        """
        Изменить видимость элемента UI
        :param element: элемент, чью видимость мы изменяем
        :param visible: видимость
        :return:
        """
        element.setVisible(visible)

    def leForSlidersTextEdited(self, minValue, maxValue, lineEdit: QtWidgets.QLineEdit, slider: QtWidgets.QSlider):
        """
        Логика lineEdit для слайдеров. Изменение значения в lineEdit влияет на slider
        :param minValue: минимальное значение слайдера
        :param maxValue: миксимальное значение слайдера
        :param lineEdit: элемент lineEdit
        :param slider: элемент slider
        :return:
        """
        try:
            value = int(lineEdit.text())
        except ValueError:
            value = slider.minimum()

        lineEdit.setText(str(value))

        if value > maxValue:
            lineEdit.setText(str(maxValue))
        elif value < minValue:
            lineEdit.setText(str(minValue))

        slider.setValue(value)

    def sliderValueChanged(self, lineEdit: QtWidgets.QLineEdit, slider: QtWidgets.QSlider):
        """
        Изменение значения слайдера
        :param lineEdit: элемент lineEdit
        :param slider: элемент slider
        :return:
        """
        value = slider.value()

        lineEdit.setText(str(value))

    def initSlider(self, lblMin: QtWidgets.QLabel, lblMax: QtWidgets.QLabel, minValue, maxValue, currentValue,
                   slider: QtWidgets.QSlider, lineEdit: QtWidgets.QLineEdit):
        """
        Инициализация составного слайдера
        :param lblMin: элемент label для минимального значения слайдера
        :param lblMax: элемент label для максимального значения слайдера
        :param minValue: минимальное значение слайдера
        :param maxValue: максимальное значение слайдера
        :param currentValue: начальное (оптимальное) значение слайдера
        :param slider: элемент slider
        :param lineEdit: элемент lineEdit
        :return:
        """
        lblMin.setText(str(minValue))
        slider.setMinimum(minValue)

        lblMax.setText(str(maxValue))
        slider.setMaximum(maxValue)

        lineEdit.textEdited.connect(
            lambda: self.leForSlidersTextEdited(minValue, maxValue,
                                                lineEdit, slider))

        slider.valueChanged.connect(
            lambda: self.sliderValueChanged(lineEdit, slider))

        slider.setValue(currentValue)

    def customizeGaussianSliderStep(self):
        newValue = self.ui.sliderGaussianBlur.value()
        if self.gaussianBlurLastValue < newValue:
            if newValue % 2 == 1:
                self.ui.sliderGaussianBlur.setValue(newValue)
            else:
                self.ui.sliderGaussianBlur.setValue(newValue + 1)
        elif self.gaussianBlurLastValue > newValue:
            if newValue % 2 == 1:
                self.ui.sliderGaussianBlur.setValue(newValue)
            else:
                self.ui.sliderGaussianBlur.setValue(newValue - 1)


    def setSliderValue(self, slider: QtWidgets.QSlider, value: int):
        slider.setValue(value)

    def parametersModeChanged(self, chooseMode):
        values = ConstValues.OptimalValues()

        values.getModeSettings(chooseMode)

        if chooseMode == ConstValues.isolatorsTypes['glass']:
            self.ui.rbGlass.setChecked(True)
        else:
            self.ui.rbCeramic.setChecked(True)
            if chooseMode == ConstValues.isolatorsTypes['ceramicbrown']:
                self.ui.rbBrown.setChecked(True)
            elif chooseMode == ConstValues.isolatorsTypes['ceramicwhite']:
                self.ui.rbWhite.setChecked(True)

        self.setSliderValue(self.ui.sliderCrackScale, values.optimalCrackScale)
        self.setSliderValue(self.ui.sliderWhiteLimit, values.optimalWhiteLimit)
        self.setSliderValue(self.ui.sliderGaussianBlur, values.optimalGaussianBlur)
        self.setSliderValue(self.ui.sliderPaletteSmoothing, values.optimalPaletteSmoothing)
        pass

    def sidesParameterChanged(self, side: int):
        if not self.ui.cbLeft.isChecked() and not self.ui.cbMiddle.isChecked() and not self.ui.cbRight.isChecked():
            if side == ConstValues.sidesForGenerate['left']:
                self.ui.cbLeft.setChecked(True)
            elif side == ConstValues.sidesForGenerate['middle']:
                self.ui.cbMiddle.setChecked(True)
            elif side == ConstValues.sidesForGenerate['right']:
                self.ui.cbRight.setChecked(True)
            QtWidgets.QMessageBox.warning(self, "Предупреждение",
                                          "Должна быть выбрана хотя бы одна сторона для генерации!",
                                          QtWidgets.QMessageBox.Ok)


class ComputeThread(QThread):
    incProgressBar = pyqtSignal(int)
    computeStopped = pyqtSignal(str, int)
    computeFinished = pyqtSignal(str, int)

    def __init__(self, properties: Properties, logs: QtWidgets.QTextEdit, parent=None):
        super(ComputeThread, self).__init__(parent)
        self.properties = properties
        self.logs = logs

    def run(self):
        crackedIsolatorsCount = 0
        for maskName, imageName in zip(os.listdir(self.properties.masksDir), os.listdir(self.properties.isolatorsDir)):
            if not self.isInterruptionRequested():
                crackedIsolatorsCount += 1
                print("Изолятор " + imageName + f"({crackedIsolatorsCount}/{self.properties.howIsolatorsToCompute}):")
                self.logs.append("Изолятор " + imageName + ":\n")
                isol = IsolatorImage()
                # Считываем изображение и маску изолятора
                isol.ReadImage(self.properties.isolatorsDir + imageName)
                # Если изображение плохое, отсеиваем его
                if isol.weight > isol.height:
                    del isol
                    print("\tИзображение не подходит по размеру!")
                    self.logs.append("\tИзображение не подходит по размеру!\n")
                    continue
                isol.ReadMask(self.properties.masksDir + maskName)
                # Вырезаем цветной изолятор по маске
                isol.MakeMaskedImage()
                # Узнаём контур изолятора для нанесения трещин
                isol.MakeContour()
                crackScale = random.randint(self.properties.crackScale - 1, self.properties.crackScale + 1)

                for side in self.properties.sidesForGenerate:
                    if self.properties.computeType == ConstValues.computeTypes['addition']:
                        DefectImposeManager.DefectAddition(isol, ConstValues.cracksDirectories[ConstValues.sidesForGenerate[side]],
                                                           crackScale,
                                                           self.properties.whiteLimit,
                                                           self.properties.gaussianBlur,
                                                           ConstValues.sidesForGenerate[side],
                                                           ConstValues.isolatorsTypes[self.properties.isolatorType + self.properties.isolatorColor],
                                                           self.properties.crackedIsolatorsDir,
                                                           self.logs)
                    elif self.properties.computeType == ConstValues.computeTypes['generation']:
                        DefectImposeManager.DefectGeneration(isol, ConstValues.sidesForGenerate[side],
                                                             self.properties.paletteSmoothing,
                                                             self.properties.gaussianBlur,
                                                             ConstValues.isolatorsTypes[self.properties.isolatorType + self.properties.isolatorColor],
                                                             self.properties.fillAlgorithm,
                                                             self.properties.crackedIsolatorsDir, self.logs)

                self.incProgressBar.emit(math.floor((crackedIsolatorsCount / self.properties.howIsolatorsToCompute) * 100))
                if crackedIsolatorsCount >= self.properties.howIsolatorsToCompute:
                    break

                self.logs.verticalScrollBar().setValue(self.logs.verticalScrollBar().maximum())

                # Удаляем изолятор перед тем как взять новый
                del isol
            else:
                self.computeStopped.emit("Генерация остановлена!", crackedIsolatorsCount)
                return

        self.computeFinished.emit("Генерация завершена успешно!", self.properties.howIsolatorsToCompute)

    def stop(self):
        self.terminate()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = IsolatorCracker()

    application.show()

    sys.exit(app.exec())
