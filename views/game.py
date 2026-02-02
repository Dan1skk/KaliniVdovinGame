import arcade
import time
import constants
from models import ScoreManager
from entities.player import Player
from entities.enemy import Enemy
from views.win import WinView
from views.game_over import GameOverView
import os

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
        self.start_time = time.time()
        self.scene = arcade.Scene()

        # пути в фотачкам
        current_dir = os.path.dirname(__file__)
        assets_path = os.path.normpath(os.path.join(current_dir, "..", "assets", "images"))


        # 1. Инициализируем ВСЕ списки сразу
        for name in ["Player", "Walls", "Coins", "Enemies", "Portal", "Heals", "Spikes"]:
            self.scene.add_sprite_list(name)

        # 2. Формируем путь к карте
        current_dir = os.path.dirname(__file__)
        file_path = os.path.normpath(os.path.join(current_dir, "..", "levels", f"map{self.level}.txt"))

        # 3. Читаем и парсим карту
        if not os.path.exists(file_path):
            print(f"ОШИБКА: Файл {file_path} реально не существует!")
            return

        with open(file_path, "r") as f:
            lines = f.readlines()
            # Инвертируем список строк, чтобы y=0 был внизу
            lines = [line.strip() for line in lines if line.strip()]
            for row_index, line in enumerate(reversed(lines)):
                for col_index, char in enumerate(line):
                    # Стандартная сетка: центр объекта = индекс * 64 + половина (32)
                    x = col_index * 64 + 32
                    y = row_index * 64 + 32

                    if char == "G":
                        wall = arcade.Sprite(":resources:images/tiles/grassMid.png", constants.TILE_SCALING)
                        wall.position = (x, y)
                        self.scene.add_sprite("Walls", wall)

                    elif char == "W":
                        wall = arcade.Sprite(":resources:images/tiles/brickBrown.png", constants.TILE_SCALING)
                        wall.position = (x, y)
                        self.scene.add_sprite("Walls", wall)

                    elif char == "C":
                        coin = arcade.Sprite(":resources:images/items/coinGold.png", constants.COIN_SCALING)
                        coin.position = (x, y)
                        self.scene.add_sprite("Coins", coin)

                    elif char == "E":
                        portal = arcade.Sprite(":resources:images/items/gemBlue.png", 0.8)
                        portal.position = (x, y)
                        self.scene.add_sprite("Portal", portal)

                    elif char == "S":
                        enemy = Enemy(x, y)
                        self.scene.add_sprite("Enemies", enemy)

                    elif char == "H":  # ХИЛКА
                        heart_file = os.path.join(assets_path, "heal.png")
                        health = arcade.Sprite(heart_file, scale=0.20)
                        health.position = (x, y)
                        self.scene.add_sprite("Heals", health)

                    elif char == "X":  # ШИПЫ
                        spike_file = os.path.join(assets_path, "shipi.png")
                        spike = arcade.Sprite(spike_file)
                        spike.width = 64
                        spike.height = 20
                        spike.center_x = x
                        spike.bottom = y - 32
                        self.scene.add_sprite("Spikes", spike)

        # 4. Игрок и физика
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

        # --- ЛОГИКА ВРАГОВ (ДВИЖЕНИЕ) ---
        enemies = self.scene.get_sprite_list("Enemies")
        walls = self.scene.get_sprite_list("Walls")

        for enemy in enemies:
            enemy.update(walls)
            # Если враг врезался в стену (не край), тоже разворачиваем
            if arcade.check_for_collision_with_list(enemy, walls):
                enemy.reverse_direction()

        # --- ПРОВЕРКА СТОЛКНОВЕНИЙ ИГРОКА ---

        # 1. Падение в яму
        if self.player.center_y < -100:
            self.lives -= 1
            arcade.play_sound(self.death_sound)
            if self.lives > 0:
                self.player.center_x, self.player.center_y = 128, 128
                self.player.change_x, self.player.change_y = 0, 0
            else:
                self.window.show_view(GameOverView())

        # 2. Столкновение с врагами
        # Сначала получаем список ВСЕХ врагов, которых коснулись
        enemy_hit_list = arcade.check_for_collision_with_list(self.player, enemies)

        for enemy in enemy_hit_list:
            # Считаем, что мы прыгнули сверху, если:
            # 1. Мы падаем (change_y < 0)
            # 2. Низ игрока выше, чем центр врага (с запасом 10 пикселей для отзывчивости)
            if self.player.change_y < 0 and self.player.bottom > (enemy.center_y - 10):
                enemy.remove_from_sprite_lists()
                self.player.change_y = constants.PLAYER_JUMP_SPEED / 2
                arcade.play_sound(self.collect_sound)
            else:
                # В любом другом случае (идем в лоб, прыгаем снизу) — это урон
                self.lives -= 1
                arcade.play_sound(self.death_sound)
                if self.lives > 0:
                    self.player.center_x, self.player.center_y = 128, 128
                    self.player.change_x, self.player.change_y = 0, 0
                else:
                    self.window.show_view(GameOverView())
                # Прерываем цикл, чтобы одна коллизия не отняла все жизни сразу
                break

        # --- ЛОГИКА ШИПОВ ---
        if arcade.check_for_collision_with_list(self.player, self.scene["Spikes"]):
            self.lives -= 1
            arcade.play_sound(self.death_sound)
            if self.lives > 0:
                # Отбрасываем на старт при уколе
                self.player.center_x, self.player.center_y = 128, 128
                self.player.change_x, self.player.change_y = 0, 0
            else:
                self.window.show_view(GameOverView())

        # --- ЛОГИКА ХИЛОК ---
        heal_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Heals"])
        for heal in heal_hit_list:
            if self.lives < 3:  # Например, максимум 5 жизней
                self.lives += 1
                heal.remove_from_sprite_lists()
                arcade.play_sound(self.collect_sound)



        # --- ОСТАЛЬНОЙ КОД (КАМЕРА, МОНЕТЫ, ПОРТАЛ) ---
        self.explosions.update()
        self.camera.position = arcade.math.lerp_2d(self.camera.position, self.player.position, 0.1)

        if self.physics.can_jump():
            self.player.jumps_count = 0

        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Coins"])
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1
            arcade.play_sound(self.collect_sound)

        if arcade.check_for_collision_with_list(self.player, self.scene["Portal"]):
            self.total_time = round(time.time() - self.start_time, 2)
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
