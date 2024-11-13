import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import QTimer

class MyWindow(QWidget):
    def __init__(self, speed=0.05):  # cкорость в радианах; положительная - по часовой, отрицательная - против часовой
        super().__init__()
        self.setWindowTitle("Движущаяся точка на окружности")  # добавляем заголовок
        self.setGeometry(1, 80, 600, 600)  # определяем размеры окна: коорд-ты левого верхн угла виджета по оси X, по оси Y и ширина, высота

        # параметры окружности
        self.radius = 200
        self.center = (300, 300)

        # параметры анимации точки
        self.angle = 0
        self.speed = speed

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # добавляем сглаживание

        self.angle += self.speed
        if self.angle >= 2 * math.pi:
            self.angle -= 2 * math.pi
        elif self.angle <= 0:
            self.angle += 2 * math.pi
        
        # отрисовка окружности
        pen = QPen(QColor("olive"), 2)
        painter.setPen(pen)
        painter.drawEllipse(self.center[0] - self.radius, self.center[1] - self.radius, self.radius * 2, self.radius * 2)
        
        # вычисление координат точки
        x = round(self.center[0] + self.radius * math.cos(self.angle))
        y = round(self.center[1] + self.radius * math.sin(self.angle))

        # отрисовка точки
        pen.setWidth(10) 
        painter.setPen(pen)
        painter.drawPoint(x, y)

        
if __name__ == "__main__": 
    app = QApplication(sys.argv)  # после создания автоматически начинает цикл обработки событий, который будет  отслеживать действия пользователя, обновления графического интерфейса, перерисовку элементов ...
    window = MyWindow(speed=0.2)
    
    #установка таймера для перемещения точки
    window.timer = QTimer()
    window.timer.setInterval(10)  # перемещать точку каждые 10 мс
    window.timer.timeout.connect(window.update)  # таймер истекает -> обновление виджета
    window.timer.start()

    window.show()
    sys.exit(app.exec_())  # app.exec_() - запускаем цикл событий, передаем код завершения  обработки событий в sys.exit()