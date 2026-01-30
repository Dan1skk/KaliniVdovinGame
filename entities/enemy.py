import arcade

class Enemy(arcade.Sprite):
    def __init__(self, x, y):
        # Используем стандартный ресурс слизня
        super().__init__(":resources:images/enemies/slimeBlue.png", scale=0.5)
        self.center_x = x
        self.center_y = y
        self.change_x = 2 # Скорость движения

    def update(self):
        # Движение по горизонтали
        self.center_x += self.change_x

    def reverse_direction(self):
        self.change_x *= -1
        # Отражаем спрайт, чтобы он смотрел в сторону движения
        self.flipped_horizontally = self.change_x < 0