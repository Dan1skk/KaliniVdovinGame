import arcade
import constants


class Enemy(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(":resources:images/enemies/slimeBlue.png", constants.TILE_SCALING)
        self.center_x = x
        self.center_y = y
        self.change_x = 2  # Скорость движения
        self.should_reverse = False

    def update(self, wall_list, spike_list=None):
        """Обновление движения врага"""
        self.center_x += self.change_x

        # 1. Проверка столкновения со стенами (чтобы не проходил сквозь блоки)
        if arcade.check_for_collision_with_list(self, wall_list):
            self.change_x *= -1
            self.center_x += self.change_x  # Отталкиваемся чуть-чуть

        # 2. Проверка столкновения с шипами (чтобы разворачивался перед ними)
        if spike_list and arcade.check_for_collision_with_list(self, spike_list):
            self.change_x *= -1
            self.center_x += self.change_x

        # 3. Логика разворота у края платформы
        # Проверяем точку чуть впереди снизу (под ногами по направлению движения)
        check_x = self.center_x + (self.width / 2 if self.change_x > 0 else -self.width / 2)
        check_y = self.bottom - 5

        # Если под этой точкой нет стены — значит впереди обрыв
        is_over_ground = False
        for wall in wall_list:
            if wall.collides_with_point((check_x, check_y)):
                is_over_ground = True
                break

        if not is_over_ground:
            self.change_x *= -1