import cv2 as cv


# Класс изображения
class Image:
    image = None    # Изображение

    height = int    # Высота
    weight = int    # Ширина
    imageName = str # Имя изображенния

    def ReadImage(self, imagePath=str):
        """Считать изображение с диска

        :param imagePath: Путь до изображения на диске
        """
        try:
            self.image = cv.imread(imagePath)

            self.height = self.image.shape[0]
            self.weight = self.image.shape[1]
            self.imageName = imagePath.split('/')[-1]
        except FileNotFoundError and FileExistsError:
            print("Указан неверный путь!")
            exit(-1)


    def ShowImage(self, name: str):
        cv.imshow(name, self.image)
        cv.waitKey()
