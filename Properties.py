class Properties:
    def __init__(self, isolatorType="", isolatorColor="", isolatorsDir="", masksDir="", crackedIsolatorsDir="",
                 crackScale=0, whiteLimit=0, gaussianBlur=0, paletteSmoothing=0, computeType=0, fillAlgorithm=0, howIsolatorsToCompute=1):
        self.isolatorType = isolatorType
        self.isolatorColor = isolatorColor

        self.crackedIsolatorsDir = crackedIsolatorsDir
        self.isolatorsDir = isolatorsDir
        self.masksDir = masksDir

        self.sidesForGenerate = []
        self.crackScale = crackScale
        self.whiteLimit = whiteLimit
        self.gaussianBlur = gaussianBlur
        self.paletteSmoothing = paletteSmoothing
        self.fillAlgorithm = fillAlgorithm
        self.computeType = computeType
        self.howIsolatorsToCompute = howIsolatorsToCompute

    def setIsolatorDir(self, directory: str):
        self.isolatorsDir = directory

    def setMasksDir(self, directory: str):
        self.masksDir = directory

    def setCrackScale(self, value: int):
        self.crackScale = value

    def setWhiteLimit(self, value: int):
        self.whiteLimit = value

    def setGaussianBlur(self, value: int):
        self.gaussianBlur = value

    def addSideForGenerate(self, side: str):
        self.sidesForGenerate.append(side)

    def setIsolatorType(self, value: str):
        self.isolatorType = value

    def setIsolatorColor(self, value: str):
        self.isolatorColor = value

    def setPaletteSmoothing(self, value: int):
        self.paletteSmoothing = value

    def setComputeType(self, value: int):
        self.computeType = value

    def setFillAlgorithm(self, value: int):
        self.fillAlgorithm = value

    def setCrackedIsolatorsDir(self, value: str):
        self.crackedIsolatorsDir = value

    def setHowIsolatorsToCompute(self, value: int):
        self.howIsolatorsToCompute = value
