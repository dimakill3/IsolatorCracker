# region Values
realizedDefectTypes = 2
minCrackScale = 5
currentCrackScale = 7
maxCrackScale = 15

minWhiteLimit = 0
currentWhiteLimit = 200
maxWhiteLimit = 255

minGaussianBlur = 1
currentGaussianBlur = 3
maxGaussianBlur = 5

minPaletteSmoothing = 3
currentPaletteSmoothing = 7
maxPaletteSmoothing = 9
# endregion


class OptimalValues:
    def __init__(self, ):
        self.optimalCrackScale = 7
        self.optimalWhiteLimit = 200
        self.optimalGaussianBlur = 3
        self.optimalPaletteSmoothing = 7

    def getModeSettings(self, mode):
        if mode == isolatorsTypes['glass']:
            return self.getGlassModeSettings()
        if mode == isolatorsTypes['ceramicbrown']:
            return self.getBrownCeramicModeSettings()
        if mode == isolatorsTypes['ceramicwhite']:
            return self.getWhiteCeramicModeSettings()

        return self

    def getGlassModeSettings(self):
        self.optimalCrackScale = 7
        self.optimalWhiteLimit = 220
        self.optimalGaussianBlur = 3
        self.optimalPaletteSmoothing = 7
        return self

    def getBrownCeramicModeSettings(self):
        self.optimalCrackScale = 5
        self.optimalWhiteLimit = 220
        self.optimalGaussianBlur = 3
        self.optimalPaletteSmoothing = 7
        return self

    def getWhiteCeramicModeSettings(self):
        self.optimalCrackScale = 6
        self.optimalWhiteLimit = 255
        self.optimalGaussianBlur = 3
        self.optimalPaletteSmoothing = 7
        return self


# region Directories
isolatorDirectory = "./Resources/isolators/"     # Директория со стеклянными изоляторами
maskDirectory = "./Resources/masks/"             # Директория с масками стеклянных изоляторов

leftEdgeCrackDirectory = "./Resources/cracks/edge/left/"   # Директория трещин для левого края изолятора
rightEdgeCrackDirectory = "./Resources/cracks/edge/right/"   # Директория трещин для правого края изолятора
middleCrackDirectory = "./Resources/cracks/middle/"   # Директория трещин посреди изолятора

crackedCeramicIsolDirectory = "./Resources/ceramic cracked isolators/"   # Дириктория для треснувших изоляторов
crackedGlassIsolDirectory = "D:/Учёба/ScrapAdd/Resources/cracked isolators"  # Директория изоляторов с трещинами

ceramicBrownIsolDirectory = "./Resources/ceramic isolators/brown/"   # Директория с коричневыми изоляторами
ceramicWhiteIsolDirectory = "./Resources/ceramic isolators/white/"   # Директория с белыми изоляторами

ceramicBrownMaskDirectory = "./Resources/ceramic masks/brown/"   # Директория с масками коричневых изоляторов
ceramicWhiteMaskDirectory = "./Resources/ceramic masks/white/"   # Директория с масками белых изоляторов


# endregion

sidesForGenerate = {"left": 0, "middle": 1, "right": 2}
isolatorsTypes = {"glass": 0, "ceramicbrown": 1, "ceramicwhite": 2}
computeTypes = {"addition": 0, "generation": 1}
defectTypes = {"straight": 0, "round": 1}
fillAlgorithms = {"voronoi": 0, "perlin": 1, "range": 2}
cracksDirectories = {0: "./Resources/cracks/edge/left/", 1: "./Resources/cracks/middle/", 2: "./Resources/cracks/edge/right/"}
