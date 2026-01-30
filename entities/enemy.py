#
import arcade

class Enemy(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(":resources:images/enemies/slimeBlue.png", scale=0.5)
        self.center_x = x
        self.center_y = y
        self.change_x = 2

    def update(self, wall_list): # Добавляем wall_list как аргумент
        # Двигаемся
        self.center_x += self.change_x

        # Проверка края платформы
        # Вычисляем точку "перед ногами"
        # Если идем вправо, смотрим чуть правее центра, если влево — чуть левее
        check_x = self.center_x + (self.width // 2 if self.change_x > 0 else -self.width // 2)
        check_y = self.bottom - 5 # Чуть ниже уровня ног

        # Ищем, есть ли под этой точкой хоть какая-то стена
        is_on_edge = not arcade.get_sprites_at_point((check_x, check_y), wall_list)

        if is_on_edge:
            self.reverse_direction()

    def reverse_direction(self):
        self.change_x *= -1
        self.flipped_horizontally = self.change_x < 0