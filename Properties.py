class Properties:
    def __init__(self, isolatorsDir = "", masksDir = "", crackScale = 0, whiteLimit = 0,
                 gaussianBlur = 0, isolatorType = "", isolatorColor = "", computeType = 0):
        self.isolatorsDir = isolatorsDir
        self.masksDir = masksDir
        self.crackScale = crackScale
        self.whiteLimit = whiteLimit
        self.gaussianBlur = gaussianBlur
        self.sidesForGenerate = []
        self.isolatorType = isolatorType
        self.isolatorColor = isolatorColor
        self.computeType = computeType

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

    def addSideForGenerate(self, side: int):
        self.sidesForGenerate.append(side)

    def setIsolatorType(self, value: str):
        self.isolatorType = value

    def setIsolatorColor(self, value: str):
        self.isolatorColor = value
