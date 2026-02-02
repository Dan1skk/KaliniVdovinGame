import arcade
import constants
import os
import sys


def safe_load(path):
    """Загружает текстуру и делает зеркальную копию. Если файла нет — создает красный круг."""
    try:
        texture = arcade.load_texture(path)
        return [texture, texture.flip_left_right()]
    except Exception as e:
        print(f"Не удалось загрузить: {path}")
        # Заглушка, чтобы игра не вылетала
        tex = arcade.make_soft_circle_texture(32, arcade.color.RED)
        return [tex, tex]


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.character_face_direction = 0
        self.cur_texture = 0
        self.scale = constants.SPRITE_SCALING

        # Находим путь к роботу в твоем .venv
        venv_path = os.path.dirname(os.path.dirname(sys.executable))
        base = os.path.join(venv_path, "Lib", "site-packages", "arcade", "resources", "assets", "images",
                            "animated_characters", "robot", "robot")

        # Загружаем анимации робота
        self.idle_texture_pair = safe_load(f"{base}_idle.png")
        self.jump_texture_pair = safe_load(f"{base}_jump.png")
        self.fall_texture_pair = safe_load(f"{base}_fall.png")

        # У робота обычно 8 кадров ходьбы
        self.walk_textures = [safe_load(f"{base}_walk{i}.png") for i in range(8)]

        # Устанавливаем начальную текстуру
        self.texture = self.idle_texture_pair[0]

    def update_animation(self, delta_time: float = 1 / 60):
        # Куда идем, туда и смотрим
        if self.change_x < 0 and self.character_face_direction == 0:
            self.character_face_direction = 1
        elif self.change_x > 0 and self.character_face_direction == 1:
            self.character_face_direction = 0

        # Анимация прыжка
        if self.change_y > 0:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        # Анимация падения
        elif self.change_y < 0:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        # Если стоим
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Анимация ходьбы
        self.cur_texture += 1
        if self.cur_texture > 7 * constants.UPDATES_PER_FRAME:
            self.cur_texture = 0

        frame = self.cur_texture // constants.UPDATES_PER_FRAME
        self.texture = self.walk_textures[frame][self.character_face_direction]