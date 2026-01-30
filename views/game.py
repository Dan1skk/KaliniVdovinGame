import arcade
import time
import constants
from models import ScoreManager
from entities.player import Player
from entities.enemy import Enemy
from views.win import WinView
from views.game_over import GameOverView

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.scene = None
        self.player = None
        self.physics = None
        self.level = 1  # Начинаем с первого уровня

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.score = 0
        self.lives = 3  # Добавляем 3 жизни
        self.start_time = 0  # Время начала
        self.total_time = 0  # Итоговое время

        self.db = ScoreManager()
        self.explosions = arcade.SpriteList()

        self.death_sound = arcade.load_sound(":resources:sounds/lose1.wav")
        self.collect_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

    def setup(self):
        self.start_time = time.time()  # Засекаем время
        self.scene = arcade.Scene()
        # Добавляем пустые списки заранее, чтобы не было KeyError
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls")
        self.scene.add_sprite_list("Coins")
        self.scene.add_sprite_list("Enemies")  # Вот это должно быть тут!
        self.scene.add_sprite_list("Portal")

        # 1. Формируем путь к папке levels
        map_path = f"levels/map{self.level}.txt"

        # 2. ОДИН цикл загрузки вместо двух
        try:
            with open(map_path, "r") as map_file:
                lines = map_file.readlines()
                for row_index, line in enumerate(reversed(lines)):
                    for col_index, char in enumerate(line.strip()):
                        x, y = col_index * 64, row_index * 64

                        if char == "G":
                            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=0.5)
                            wall.center_x, wall.center_y = x, y
                            self.scene.add_sprite("Walls", wall)
                        elif char == "W":
                            wall = arcade.Sprite(":resources:images/tiles/brickBrown.png", scale=0.5)
                            wall.center_x, wall.center_y = x, y
                            self.scene.add_sprite("Walls", wall)
                        elif char == "C":
                            coin = arcade.Sprite(":resources:images/items/coinGold.png", scale=0.5)
                            coin.center_x, coin.center_y = x, y
                            self.scene.add_sprite("Coins", coin)
                        elif char == "E":
                            portal = arcade.Sprite(":resources:images/items/gemBlue.png", scale=0.8)
                            portal.center_x, portal.center_y = x, y
                            self.scene.add_sprite("Portal", portal)
                        elif char == "S":
                            enemy = Enemy(x, y)
                            self.scene.add_sprite("Enemies", enemy)
        except FileNotFoundError:
            print(f"Критическая ошибка: Файл {map_path} не найден!")
            return  # Выходим из метода, чтобы не упасть дальше


        self.player = Player()
        self.player.center_x, self.player.center_y = 128, 128
        self.scene.add_sprite("Player", self.player)

        self.physics = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=constants.GRAVITY, walls=self.scene["Walls"]
        )


    def on_draw(self):
        self.window.clear()
        with self.camera.activate():
            self.scene.draw()
            self.explosions.draw()

        with self.gui_camera.activate():
            current_elapsed = time.time() - self.start_time
            # Добавляем отображение жизней
            display_text = f"Монеты: {self.score}  |  Время: {current_elapsed:.1f}с  |  Жизни: {self.lives}"
            arcade.draw_text(display_text, 20, 580, arcade.color.WHITE, 16)

    def on_update(self, delta_time):
        self.physics.update()
        self.scene.update_animation(delta_time, ["Player"])

        # Логика врагов (патруль)
        enemies = self.scene.get_sprite_list("Enemies")
        walls = self.scene.get_sprite_list("Walls")  # Достаем стены

        for enemy in enemies:
            # Передаем стены врагу, чтобы он не упал
            enemy.update(walls)

            # Старая проверка столкновения со стенами (чтобы разворачивался от препятствий)
            if arcade.check_for_collision_with_list(enemy, walls):
                enemy.reverse_direction()

        # --- ОБНОВЛЕННАЯ ПРОВЕРКА СМЕРТИ ---
        # Если коснулись врага ИЛИ упали в яму
        if arcade.check_for_collision_with_list(self.player, enemies) or self.player.center_y < -100:
            self.lives -= 1
            arcade.play_sound(self.death_sound)

            if self.lives > 0:
                # Еще есть попытки — просто возвращаем на старт
                self.player.center_x = 128
                self.player.center_y = 128
                self.player.change_x = 0
                self.player.change_y = 0
            else:
                # ВОТ ТУТ СОБАКА ЗАРЫТА:
                # Вместо self.setup() вызываем экран смерти
                death_view = GameOverView()
                self.window.show_view(death_view)


        self.explosions.update()
        self.camera.position = arcade.math.lerp_2d(self.camera.position, self.player.position, 0.1)

        # ОБНУЛЯЕМ СЧЕТЧИК, когда коснулись земли
        if self.physics.can_jump():
            self.player.jumps_count = 0


        # 1. Сбор монет (Здесь только монеты!)
        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Coins"])
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1
            arcade.play_sound(self.collect_sound)

        # 2. КАСАНИЕ ПОРТАЛА (Теперь это отдельный блок, вне цикла!)
        if arcade.check_for_collision_with_list(self.player, self.scene["Portal"]):
            self.total_time = round(time.time() - self.start_time, 2)

            # Сохраняем результат в БД
            self.db.add_score(f"Игрок (Ур. {self.level})", self.score, self.total_time)

            from views.win import WinView
            win_view = WinView()
            win_view.score = self.score
            win_view.final_time = self.total_time
            win_view.current_level = self.level
            self.window.show_view(win_view)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            # ПЕРВЫЙ ПРЫЖОК (с земли)
            if self.physics.can_jump():
                self.player.change_y = constants.PLAYER_JUMP_SPEED
                self.player.jumps_count = 1  # Отмечаем, что один прыжок сделан
                arcade.play_sound(self.jump_sound)

            # ВТОРОЙ ПРЫЖОК (в воздухе)
            elif self.player.jumps_count == 1:
                self.player.change_y = constants.PLAYER_JUMP_SPEED
                self.player.jumps_count = 2  # Потратили второй прыжок
                arcade.play_sound(self.jump_sound)
        elif key in [arcade.key.LEFT, arcade.key.A]:
            self.player.change_x = -constants.PLAYER_MOVEMENT_SPEED
        elif key in [arcade.key.RIGHT, arcade.key.D]:
            self.player.change_x = constants.PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D]:
            self.player.change_x = 0

    def on_show_view(self):
        # Возвращаем нормальный цвет неба, когда заходим в игру
        arcade.set_background_color(arcade.color.CORNFLOWER_BLUE)
