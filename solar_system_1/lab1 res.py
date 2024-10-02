import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QPixmap
from PyQt5.QtCore import QTimer, QPoint


class CelestialBody(object):
    def __init__(self, color, radius, rot_radius=0, speed=0, angle=0):
        self.color = color
        self.radius = radius  # радиус объекта
        self.rot_radius = rot_radius  # радиус вращения
        self.speed = speed
        self.angle = angle 
        self.x = round(self.rot_radius * math.cos(self.angle))       
        self.y = round(self.rot_radius * math.sin(self.angle)) 
        self.trace = []  # след от объекта

    def move(self):
        self.angle += self.speed
        if self.angle >= 2 * math.pi:
            self.angle -= 2 * math.pi
        elif self.angle <= 0:
            self.angle += 2 * math.pi
        self.x = round(self.rot_radius * math.cos(self.angle))
        self.y = round(self.rot_radius * math.sin(self.angle)) 

        # добавляем новую точку в след
        self.trace.append((self.x, self.y))
        if len(self.trace) > self.rot_radius + self.radius * 10:  
            self.trace.pop(0)  # удаляем лишнии точки, если след слишком большой


class Satellite(CelestialBody):
    def __init__(self,color, planet, radius, rot_radius=0, speed=0, angle=0):   # указать тип planet
        super().__init__(color, radius, rot_radius, speed, angle)
        self.planet = planet  # планета вокруг которой вращается спутник

    def move(self):
        self.angle += self.speed
        if self.angle >= 2 * math.pi:
            self.angle -= 2 * math.pi
        elif self.angle <= 0:
            self.angle += 2 * math.pi
        self.x = round(self.rot_radius * math.cos(self.angle) + self.planet.x)
        self.y = round(self.rot_radius * math.sin(self.angle) + self.planet.y)

        
class SolarSystem(QWidget):
    def __init__(self, window_size_x=1000, window_size_y=1000):  
        super().__init__()
        self.setWindowTitle(" ~ Solar System ~ ") 
        self.setGeometry(1, 80, window_size_x, window_size_y)
        # координаты центра окна
        self.center_x = window_size_x//2
        self.center_y = window_size_y//2

        # устанавливаем картинку для фона
        self.pixmap = QPixmap('Безымянный рисунок.png')
      
        # прозрачность задается 4-ым аргументом в QColor(), от 0 до 255
        # CelestialBody(color, radius, rot_radius=0, speed=0, angle=0)       # RGB
        planet1 = CelestialBody(QColor(176, 196, 222, 255), 10, 70, 0.02)    # Меркурий
        planet2 = CelestialBody(QColor(255, 218, 185, 255), 15, 100, 0.015)  # Венера
        planet3 = CelestialBody(QColor(30, 144, 255, 255), 15, 140, 0.01)    # Земля
        planet4 = CelestialBody(QColor(165, 42, 42, 170), 12, 180, 0.008)    # Марс
        planet5 = CelestialBody(QColor(184, 134, 11, 120), 40, 240, 0.005)   # Юпитер
        planet6 = CelestialBody(QColor(240, 230, 140, 70), 30, 300, 0.004)   # Сатурн
        planet7 = CelestialBody(QColor(0, 191, 255, 50), 20, 360, 0.003)     # Уран
        planet8 = CelestialBody(QColor(65, 105, 225, 150), 18, 420, 0.002)   # Нептун

        moon = Satellite(QColor(255, 250, 205, 200), planet3, 5, 25, 0.04)
        phobos = Satellite(QColor(255, 250, 205, 180), planet4, 4, 25, 0.02, angle=0.5)  
        deimos = Satellite(QColor(255, 250, 205, 190), planet4, 4, 25, 0.023)

        self.celestial_bodies = [planet1, planet2, planet3, planet4, planet5, planet6, planet7, planet8, moon, phobos, deimos]
        self.sun = CelestialBody(QColor(255, 255, 0), 30)  # Солнце

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) 

        # рисуем картинку фона
        painter.drawPixmap(self.rect(), self.pixmap)
        
        # рисуем солнце
        painter.setBrush(QBrush(self.sun.color))
        painter.setPen(QPen(QColor('black'), 3))
        painter.drawEllipse(self.sun.x - self.sun.radius + self.center_x, self.sun.y - self.sun.radius + self.center_y, 2 * self.sun.radius, 2 * self.sun.radius)

        # рисуем планеты и спутники
        for body in self.celestial_bodies:
            painter.setBrush(QBrush(body.color))
            painter.setPen(QPen(QColor('black'), 3))
            painter.drawEllipse(body.x - body.radius + self.center_x, body.y - body.radius + self.center_y, 2 * body.radius, 2 * body.radius)
            
            # рисуем след от планеты
            if len(body.trace) > body.radius+2:
                painter.setPen(QPen(body.color, 2))
                qpoints = [QPoint(x + self.center_x, y + self.center_y) for x, y in body.trace[:-body.radius]]  # Преобразуем кортежи в QPoint для drawPolyline
                painter.drawPolyline(*qpoints)

            body.move()

        
if __name__ == "__main__": 
    app = QApplication(sys.argv) 
    sol_system = SolarSystem()

    sol_system.timer = QTimer()
    sol_system.timer.setInterval(10) 
    sol_system.timer.timeout.connect(sol_system.update)
    sol_system.timer.start()

    sol_system.show()
    sys.exit(app.exec_())
 