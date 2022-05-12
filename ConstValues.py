import os

# region Values
minCrackScale = 6
currentCrackScale = 7
maxCrackScale = 8

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

# region Directories
isolatorDirectory = "./Resources/isolators/"     # Директория со стеклянными изоляторами
maskDirectory = "./Resources/masks/"             # Директория с масками стеклянных изоляторов

leftEdgeCrackDirectory = "./Resources/cracks/edge/left/"   # Директория трещин для левого края изолятора
rightEdgeCrackDirectory = "./Resources/cracks/edge/right/"   # Директория трещин для правого края изолятора
middleCrackDirectory = "./Resources/cracks/middle/"   # Директория трещин посреди изолятора

crackedCeramicIsolDirectory = "./Resources/ceramic cracked isolators/"   # Дириктория для треснувших изоляторов
# crackedGlassIsolDirectory = os.getcwd().replace('\\', '/') + "/Resources/cracked isolators"  # Директория изоляторов с трещинами
crackedGlassIsolDirectory = "D:/Учёба/ScrapAdd/Resources/cracked isolators"  # Директория изоляторов с трещинами

ceramicBrownIsolDirectory = "./Resources/ceramic isolators/brown/"   # Директория с коричневыми изоляторами
ceramicWhiteIsolDirectory = "./Resources/ceramic isolators/white/"   # Директория с белыми изоляторами

ceramicBrownMaskDirectory = "./Resources/ceramic masks/brown/"   # Директория с масками коричневых изоляторов
ceramicWhiteMaskDirectory = "./Resources/ceramic masks/white/"   # Директория с масками белых изоляторов


# endregion

sidesForGenerate = {"left": 0, "middle": 1, "right": 2}
isolatorsTypesDictionary = {"glass": 0, "ceramicbrown": 1, "ceramicwhite": 2}
computeTypes = {"addition": 0, "generation": 1}
