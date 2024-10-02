import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QPixmap
from PyQt5.QtCore import QTimer, QPoint
import json


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

        
class SolarSystem(QWidget):  # MyWidget
    def __init__(self, window_size_x=1000, window_size_y=1000):  
        super().__init__()
        self.setWindowTitle(" ~ Solar System ~ ") 
        self.setGeometry(1, 80, window_size_x, window_size_y)
        # координаты центра окна
        self.center_x = window_size_x//2
        self.center_y = window_size_y//2

        # устанавливаем картинку для фона
        self.pixmap = QPixmap('Безымянный рисунок.png')

        with open("data.json", "r") as f:
            planet_data = json.load(f)

        self.celestial_bodies = [CelestialBody(QColor(*data['color']), data['radius'], data['rot_radius'], data['speed'], data['angle'],) for data in planet_data]
        moon = Satellite(QColor(176, 196, 222, 255), self.celestial_bodies[2], 4, 25, 0.02)
        phobos = Satellite(QColor(220, 200, 222, 100), self.celestial_bodies[3], 4, 20, 0.035)
        deimos = Satellite(QColor(200, 196, 222, 200), self.celestial_bodies[3], 4, 20, 0.02)
        self.celestial_bodies.append(moon)
        self.celestial_bodies.append(phobos)
        self.celestial_bodies.append(deimos)
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

        # рисуем планеты
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
 