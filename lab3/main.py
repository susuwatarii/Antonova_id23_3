import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDialog, QLabel, QSlider, QColorDialog
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QPixmap
from PyQt5.QtCore import QTimer, QPoint, Qt
import json
# не могу прописать гравитационное взаимодействие в зависимости от радиуса и массы для планет, спутников и солнца
# (по заданию они могут друг на друга наезжать)

# условия поедания - масса


class CelestialBody(object):
    def __init__(self, color, radius, rot_radius=0, speed=0, angle=0):
        self.color = color
        self.radius = radius  # радиус объекта
        self.rot_radius = rot_radius  # радиус вращения
        self.speed = speed
        self.angle = angle 
        self.x = self.rot_radius * math.cos(self.angle)     
        self.y = self.rot_radius * math.sin(self.angle)
        self.mass = self.color.alpha() * self.radius**3
        self.trace = []  # след от объекта
        self.dead = False

    def move(self):
        pass

    def get_y(self):
        return round(self.y)
    
    def get_x(self):
        return round(self.x)
    
    def check_collision(self, sel_body):
        if not self.dead and not sel_body.dead:  # для предотвращения ошибки, когда врезается в два объекта или в другой астероид
            if ((self.x - sel_body.x)**2 + (self.y - sel_body.y)**2)**0.5 <= self.radius + sel_body.radius:
                return True
        return False

    def collision(self, sel_body):  # поглощение планеты астероидом
        sel_body.mass += self.mass
        sel_body.radius = round((sel_body.mass / sel_body.color.alpha())**(1/3))
        sel_body.dx = (sel_body.dx*sel_body.mass + self.speed*self.mass) / (sel_body.mass + self.mass)
        sel_body.dy = (sel_body.dy*sel_body.mass + self.speed*self.mass) / (sel_body.mass + self.mass)
        self.dead = True
    

class RotatingSelBody(CelestialBody):
    def __init__(self, color, rot_body, radius, rot_radius, speed, angle=0):  
        super().__init__(color, radius, rot_radius, speed, angle)
        self.rot_body = rot_body 

    def move(self):
        if self.rot_body.dead:
            # если планета спутника исчезла, то вращение вокруг солнца
            self.rot_radius=(self.x**2+self.y**2)**0.5  
            self.speed = self.rot_body.speed
            self.angle = math.atan(self.y/self.x)
            if self.x < 0: # учитываем св-во arctg
                self.angle += math.pi
            self.rot_body =  CelestialBody(QColor(255, 255, 0), 30)

        # изменение угла и позиции планеты    
        self.angle += self.speed
        if self.angle >= 2 * math.pi:
            self.angle -= 2 * math.pi
        elif self.angle <= 0:
            self.angle += 2 * math.pi
        self.x = self.rot_radius * math.cos(self.angle) + self.rot_body.x
        self.y = self.rot_radius * math.sin(self.angle) + self.rot_body.y

        # добавляем новую точку в след
        self.trace.append((self.get_x(), self.get_y()))
        if len(self.trace) > self.rot_radius + self.radius * 10:  
            self.trace.pop(0)  # удаляем лишнии точки, если след слишком большой


class Asteroid(object):
    def __init__(self,  color, coords, speed, mass): 
        self.color = color
        self.mass = mass
        self.speed = speed # модуль скорости
        self.dx = None
        self.dy = None
        self.x = coords[0]   
        self.y = coords[1] 
        self.radius = round((self.mass / self.color.alpha())**(1/3))
        self.targets = []  
        self.trace = []
        self.dead = False

    def move(self): # перемещение астероида на один шаг (если выполнены условия)
        if self.dx is not None and self.dy is not None:
            self.x += self.dx   
            self.y += self.dy  
            for target in self.targets:
                if target.dead:
                    continue 
                self.set_dx_dy(target)
                if target.mass < self.mass and target.check_collision(self):
                    # взаимодействие с меньшим неб объектом
                    target.collision(self)
                    continue # меньший астероид target мертв
                # взаимодействие с бОльшим неб объектом
                if self.check_collision(target):
                    self.collision(target)

    def get_y(self):
        return round(self.y)
    
    def get_x(self):
        return round(self.x)
    
    def check_collision(self, sel_body):  # проверка наличия столкновения
        if not self.dead and not sel_body.dead:  # для предотвращения ошибки, когда врезается в два объекта или в другой астероид
            if ((self.x - sel_body.x)**2 + (self.y - sel_body.y)**2)**0.5 <= self.radius + sel_body.radius:
                return True
        return False

    def collision(self, sel_body): # поглощение астероида планетой
        sel_body.mass += self.mass
        sel_body.radius = round((sel_body.mass / sel_body.color.alpha())**(1/3))
        if isinstance(sel_body, Asteroid):  
            # меняем скорость астероиду
            sel_body.dx = (sel_body.dx*sel_body.mass + self.dx*self.mass) / (sel_body.mass + self.mass)
            sel_body.dy = (sel_body.dy*sel_body.mass + self.dy*self.mass) / (sel_body.mass + self.mass)
        self.dead = True

    def acceleration(self, sel_body):  # получение ускорения астероида
        distance2 = ((self.x - sel_body.x)**2 + (self.y - sel_body.y)**2)
        if  distance2 != 0:
            return self.mass * sel_body.mass / distance2 / 5_000_000_000
        else:
            return self.mass * sel_body.mass / 5_000_000_000
    
    def get_angle(self, sel_body):  # угол для понимания в какую сторону двигаться астероиду к др объекту
        if self.x == sel_body.x and self.y > sel_body.y:
            angle = math.pi/2
        elif self.x == sel_body.x and self.y < sel_body.y:
            angle = math.pi*3/2
        else:
            angle = math.atan((self.y-sel_body.y) / (self.x-sel_body.x))
            if  (self.x-sel_body.x) < 0: # учитываем св-во arctg
                angle += math.pi
        return angle

    def set_dx_dy(self, sel_body):  # изменить скорость астероида
        acc = self.acceleration(sel_body)
        self.dx -= acc*math.cos(self.get_angle(sel_body))
        self.dy -= acc*math.sin(self.get_angle(sel_body))


class SettingsDialog(QDialog): # диалоговое окно для задания параметров и создания астероида; связь наследованием с MainWindow
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Asteroid parameters")
        #                 x    y  width height
        self.setGeometry(300, 200, 250, 150)
 
        self.ast_color = QColor(220, 220, 220) # цвет астероида по умолчанию
        # кнопка цвета
        self.color_button = QPushButton("Choose Color", self)
        self.color_button.setGeometry(10, 10, 100, 20)
        self.color_button.clicked.connect(self.choose_color)

        # подпись рядом с кнопкой
        self.mass_label = QLabel("Mass:", self)
        self.mass_label.setGeometry(10, 40, 50, 20)

        # слайдер для задания массы
        self.mass_slider = QSlider(Qt.Horizontal, self)
        self.mass_slider.setGeometry(70, 40, 150, 20)
        # ограниечения значений массы:
        self.mass_slider.setMinimum(10_000)
        self.mass_slider.setMaximum(1_000_000)
        self.mass_slider.setValue(300_000) # Значение массы по умолчанию

        # подпись рядом с кнопкой
        self.speed_slider = QLabel("Speed:", self)
        self.speed_slider.setGeometry(10, 60, 50, 20) 

        # слайдер для скорости
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setGeometry(70, 60, 150, 20)
        # ограниечения значений массы:
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(20) # Значение spped по умолчанию

        # кнопка подтверждения изменений
        self.ok_button = QPushButton("OK", self)
        self.ok_button.setGeometry(80, 90, 50, 20)
        self.ok_button.clicked.connect(self.accept)

        # кнопка отмены изменений
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setGeometry(150, 90, 50, 20)
        self.cancel_button.clicked.connect(self.reject)

    def choose_color(self): # выбор цвета астероида (третье окно)
        color = QColorDialog.getColor(Qt.blue, self)
        if color.isValid():
            self.ast_color = color

    def get_ast_parameters(self): # возврат цвета (Qcolor), массы (int) астероида и модуля скорости
        return self.ast_color, self.mass_slider.value(), self.speed_slider.value() / 10


class SolarSystem(QWidget):  # MyWidget
    def __init__(self, window_size_x=1000, window_size_y=1000):  
        super().__init__()
        self.paused = False 
        self.ast_created = None # наличие созданного астероида без заданного направления
        self.setWindowTitle(" ~ Solar System ~ ") 
        self.setGeometry(1, 80, window_size_x, window_size_y)
        # координаты центра окна
        self.center_x = window_size_x//2
        self.center_y = window_size_y//2

        # устанавливаем картинку для фона
        self.pixmap = QPixmap('Безымянный рисунок.png')        # заменить на беззвездное небо

        # создание пазы и продолжения выполнение
        self.pause_button = QPushButton("Stop", self)
        self.continue_button = QPushButton("Go", self)
        self.pause_button.setGeometry(10, 10, 50, 20)
        self.continue_button.setGeometry(65, 10, 50, 20)
        self.pause_button.clicked.connect(self.pause)
        self.continue_button.clicked.connect(self.continue_execution)

        # создание небесных объектов:
        # загрузка данных об исходных состояниях планет
        with open("data.json", "r") as f:
            planet_data = json.load(f)

        # Солнце
        self.sun = CelestialBody(QColor(255, 255, 0), 30)  
        # планеты
        self.celestial_bodies = [RotatingSelBody(QColor(*data['color']), self.sun,  data['radius'], data['rot_radius'], data['speed'], data['angle'],) for data in planet_data]
        # спутники
        moon = RotatingSelBody(QColor(176, 196, 222, 255), self.celestial_bodies[2], 4, 25, 0.02)
        phobos = RotatingSelBody(QColor(220, 200, 222, 100), self.celestial_bodies[3], 4, 20, 0.035)
        deimos = RotatingSelBody(QColor(200, 196, 222, 200), self.celestial_bodies[3], 4, 20, 0.02)
        self.celestial_bodies.append(moon)
        self.celestial_bodies.append(phobos)
        self.celestial_bodies.append(deimos)

    def pause(self):  # обработка паузы
        self.paused = True
        self.pause_button.setEnabled(False)
        self.continue_button.setEnabled(True)

    def continue_execution(self):  # обработка запуска после паузы
        self.paused = False
        self.pause_button.setEnabled(True)
        self.continue_button.setEnabled(False)

    def draw_sel_body(self, painter, sel_body):  # рисуем след от неб. тела
        painter.setBrush(QBrush(sel_body.color))
        painter.setPen(QPen(QColor('black'), 3))
        painter.drawEllipse(sel_body.get_x() - sel_body.radius + self.center_x, sel_body.get_y() - sel_body.radius + self.center_y, 2 * sel_body.radius, 2 * sel_body.radius)
        
        if len(sel_body.trace) > sel_body.radius:
            painter.setPen(QPen(sel_body.color, 2))
            qpoints = [QPoint(x + self.center_x, y + self.center_y) for x, y in sel_body.trace]  # Преобразуем кортежи в QPoint для drawPolyline
            painter.drawPolyline(*qpoints)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) 
        # рисуем картинку фона
        painter.drawPixmap(self.rect(), self.pixmap)
        
        # рисуем солнце
        self.draw_sel_body(painter, self.sun)
        # рисуем неб. тела
        for body in self.celestial_bodies:
            self.draw_sel_body(painter, body)
            if not self.paused:
                body.move()
                if body.dead:  # проверка столкновения как результата перемещения
                    self.celestial_bodies.remove(body)  # удаляем умершее небесное тело
                    self.refresh_ast_targets() # обновляем targets для астероидов

    def refresh_ast_targets(self):  # обновление списка объектов влияющих на астероид
        asteroids_lst = [body for body in self.celestial_bodies if isinstance(body, Asteroid)] # список всех астероидов
        for asteroid in asteroids_lst:
            # список всех объекто за исключением самого астероида
            asteroid.targets = [target for target in self.celestial_bodies]
            asteroid.targets.remove(asteroid) 
            asteroid.targets.append(self.sun)

    def mousePressEvent(self, event): 
        if event.button() == Qt.RightButton:
            if self.ast_created is not None: 
                # если уже создан астероид и ему нужно задать скорость
                direction_x = event.pos().x() - self.center_x
                direction_y = event.pos().y() - self.center_y
                if direction_y == self.ast_created.get_y():  
                    # случай dx=0; избешаем деления на 0, dx = speed
                    self.ast_created.dx = self.ast_created.speed 
                    self.ast_created.dy = 0
                else:
                    # разложение скорости по x, y
                    dif_x = direction_x - self.ast_created.get_x()
                    dif_y = direction_y - self.ast_created.get_y()
                    coef = dif_x / dif_y
                    self.ast_created.dx = (self.ast_created.speed**2 / (coef**2 + 1) * coef**2)**0.5 * math.copysign(1, dif_x)
                    self.ast_created.dy = (self.ast_created.speed**2 / (coef**2 + 1))**0.5 * math.copysign(1, dif_y)

                self.ast_created = None
            else: 
                # астероид не создан, создаем
                dialog = SettingsDialog(self)
                if self.exec_settings_dialog(dialog) == 1:# если кликнули - всплывает окно
                    x = event.pos().x()
                    y = event.pos().y()
                    color, mass, speed = dialog.get_ast_parameters()  # получем значения из диалогового окна
                    ast = Asteroid(color, (x-self.center_x, y-self.center_y), speed, mass) # speed as module
                    self.celestial_bodies.append(ast)
                    self.refresh_ast_targets()
                    self.ast_created = ast

    def exec_settings_dialog(self, dialog): # создание и запуск диалогового окна
        return dialog.exec_() 
    

if __name__ == "__main__": 
    app = QApplication(sys.argv) 
    sol_system = SolarSystem()

    sol_system.timer = QTimer()
    sol_system.timer.timeout.connect(sol_system.update)
    sol_system.timer.start()

    sol_system.show()

    sys.exit(app.exec_())
 
 