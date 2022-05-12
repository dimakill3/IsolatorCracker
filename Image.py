import cv2 as cv


# Класс изображения
class Image:
    image = None    # Изображение

    height = int    # Высота
    weight = int    # Ширина

    def ReadImage(self, imagePath=str):
        """Считать изображение с диска

        :param imagePath: Путь до изображения на диске
        """
        try:
            self.image = cv.imread(imagePath)

            self.height = self.image.shape[0]
            self.weight = self.image.shape[1]
        except FileNotFoundError and FileExistsError:
            print("Указан неверный путь!")
            exit(-1)
