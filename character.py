import arcade
import constants


def load_pair(filename):
    """Вспомогательная функция для загрузки пары текстур"""
    texture = arcade.load_texture(filename)
    # Метод .flip_left_right() — самый надежный в версии 3.0+
    mirrored = texture.flip_left_right()
    return [texture, mirrored]


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.character_face_direction = 0
        self.cur_texture = 0
        self.scale = constants.SPRITE_SCALING

        main_path = ":resources:images/animated_characters/female_adventurer/femaleAdventurer"

        # Загружаем через нашу функцию
        self.idle_texture_pair = load_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = load_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_pair(f"{main_path}_fall.png")

        self.walk_textures = []
        for i in range(8):
            self.walk_textures.append(load_pair(f"{main_path}_walk{i}.png"))

        self.texture = self.idle_texture_pair[0]

    def update_animation(self, delta_time: float = 1 / 60):
        # Логика поворота
        if self.change_x < 0 and self.character_face_direction == 0:
            self.character_face_direction = 1
        elif self.change_x > 0 and self.character_face_direction == 1:
            self.character_face_direction = 0

        # Прыжок / Падение
        if self.change_y > 0:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        # Покой
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Анимация ходьбы
        self.cur_texture += 1
        if self.cur_texture > 7 * 5:
            self.cur_texture = 0
        frame = self.cur_texture // 5
        self.texture = self.walk_textures[frame][self.character_face_direction]