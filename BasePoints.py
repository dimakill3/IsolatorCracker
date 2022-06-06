import random
import numpy as np


class BasePoints:
    leftPointIndex = int
    middlePointIndex = int
    rightPointIndex = int

    leftPoint = None
    middlePoint = None
    rightPoint = None

    dopLeftPoint = None
    dopMiddlePoint = None
    dopRightPoint = None

    def BuildBasePoints(self, contour):
        hightSlice = [point[1] for point in contour]
        self.middlePointIndex = hightSlice.index(max(hightSlice))

        self.leftPointIndex = int(self.middlePointIndex - random.randint(0, int(len(contour) * 0.1)))

        self.rightPointIndex = int(self.middlePointIndex + random.randint(0, int(len(contour) * 0.1)))

        self.middlePoint = contour[self.middlePointIndex]
        self.leftPoint = contour[self.leftPointIndex]
        self.rightPoint = contour[self.rightPointIndex]

        oppositeMiddlePoint = contour[0]

        oppositeLeftPoint = contour[self.leftPointIndex - int(len(contour) / 2)]

        oppositeRightPoint = contour[self.rightPointIndex - int(len(contour) / 2)]

        koef = random.uniform(0.15, 0.25)

        self.dopLeftPoint = np.array([int(self.leftPoint[0] + (abs(self.leftPoint[0] - oppositeLeftPoint[0]) * koef)),
                             int(self.leftPoint[1] - (abs(self.leftPoint[1] - oppositeLeftPoint[1]) * koef))])

        self.dopRightPoint = np.array([int(self.rightPoint[0] - (abs(self.rightPoint[0] - oppositeRightPoint[0]) * koef)),
                              int(self.rightPoint[1] - (abs(self.rightPoint[1] - oppositeRightPoint[1]) * koef))])

        self.dopMiddlePoint = np.array([int(self.middlePoint[0] + (abs(self.leftPoint[0] - self.rightPoint[0]) * koef * random.randint(-1, 1))),
                               int(self.middlePoint[1] - (abs(self.middlePoint[1] - oppositeMiddlePoint[1]) * koef))])
