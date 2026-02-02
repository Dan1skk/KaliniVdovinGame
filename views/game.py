import arcade
import time
import constants
from models import ScoreManager
from entities.player import Player
from entities.enemy import Enemy
from views.pause import PauseView
from views.win import WinView
from views.game_over import GameOverView
import os


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.scene = None
        self.player = None
        self.physics = None
        self.level = 1
        self.total_time = 0

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.score = 0
        self.lives = 3
        self.start_time = 0

        self.db = ScoreManager()
        self.explosions = arcade.SpriteList()
        self.heart_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.gui_sprites = arcade.SpriteList()

        self.death_sound = arcade.load_sound(":resources:sounds/lose1.wav")
        self.collect_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

    def setup(self):
        self.start_time = time.time()
        self.scene = arcade.Scene()

        # Очищаем старые списки перед новым уровнем
        self.gui_sprites.clear()
        self.background_list.clear()

        # Настройка путей
        current_dir = os.path.dirname(__file__)
        assets_path = os.path.normpath(os.path.join(current_dir, "..", "assets", "images"))

        # 1. Иконка монетки для GUI (добавляем в список для отрисовки)
        self.coin_icon = arcade.Sprite("assets/images/coin.png", 0.08)
        self.coin_icon.center_x = 40
        self.coin_icon.center_y = 550
        self.gui_sprites.append(self.coin_icon)

        # 2. Фон
        bg_path = "assets/images/background4.jpg"
        if os.path.exists(bg_path):
            self.background = arcade.Sprite(bg_path)
            self.background.center_x = self.window.width / 2
            self.background.center_y = self.window.height / 2

            # ПРИНУДИТЕЛЬНО РАСТЯГИВАЕМ:
            self.background.width = self.window.width
            self.background.height = self.window.height

            #self.background.color = (100, 100, 100)
            self.background_list.append(self.background)

        # 3. Загрузка карты
        for name in ["Player", "Walls", "Coins", "Enemies", "Portal", "Heals", "Spikes"]:
            self.scene.add_sprite_list(name)

        file_path = os.path.normpath(os.path.join(current_dir, "..", "levels", f"map{self.level}.txt"))

        if not os.path.exists(file_path):
            print(f"Файл карты не найден: {file_path}")
            return

        with open(file_path, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            for row_index, line in enumerate(reversed(lines)):
                for col_index, char in enumerate(line):
                    x, y = col_index * 64 + 32, row_index * 64 + 32

                    if char == "G":
                        wall = arcade.Sprite(":resources:images/tiles/grassMid.png", constants.TILE_SCALING)
                        wall.position = (x, y)
                        self.scene.add_sprite("Walls", wall)
                    elif char == "W":
                        wall = arcade.Sprite(":resources:images/tiles/brickBrown.png", constants.TILE_SCALING)
                        wall.position = (x, y)
                        self.scene.add_sprite("Walls", wall)
                    elif char == "C":
                        coin = arcade.Sprite("assets/images/coin.png", scale=0.1)
                        coin.position = (x, y)
                        self.scene.add_sprite("Coins", coin)
                    elif char == "E":
                        portal = arcade.Sprite(":resources:images/items/gemBlue.png", 0.8)
                        portal.position = (x, y)
                        self.scene.add_sprite("Portal", portal)
                    elif char == "S":
                        enemy = Enemy(x, y)
                        self.scene.add_sprite("Enemies", enemy)
                    elif char == "H":
                        health = arcade.Sprite(os.path.join(assets_path, "heal.png"), 0.20)
                        health.position = (x, y)
                        self.scene.add_sprite("Heals", health)
                    elif char == "X":
                        spike = arcade.Sprite(os.path.join(assets_path, "shipi.png"))
                        spike.width, spike.height = 64, 20
                        spike.center_x, spike.bottom = x, y - 32
                        self.scene.add_sprite("Spikes", spike)

        # 4. Игрок и физика
        self.player = Player()
        self.player.center_x, self.player.center_y = 128, 128
        self.player.invincible_timer = 0
        self.scene.add_sprite("Player", self.player)

        self.physics = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=constants.GRAVITY, walls=self.scene["Walls"]
        )

        self.update_hearts()

    def update_hearts(self):
        self.heart_list.clear()
        for i in range(self.lives):
            heart = arcade.Sprite("assets/images/heart.png", 0.2)
            heart.center_x = 40 + (i * 40)
            heart.center_y = 600
            self.heart_list.append(heart)

    def on_show_view(self):
        """Метод вызывается при каждом переключении на этот экран"""
        arcade.set_background_color(arcade.color.CORNFLOWER_BLUE)

        # Проверяем, существует ли плеер и ИГРАЕТ ли он сейчас
        current_player = getattr(self.window, "bg_music_player", None)

        # Если плеер есть и он уже играет (playing == True), ничего не делаем!
        if current_player and current_player.playing:
            return

        # Если мы здесь, значит музыка не играет (первый запуск или после стопа)
        music_path = "assets/sounds/background_music.mp3"
        if os.path.exists(music_path):
            music = arcade.load_sound(music_path)
            self.window.bg_music_player = music.play(loop=True, volume=0.1)

    def on_hide_view(self):
        """
        Удаляем отсюда self.window.bg_music_player.stop(),
        чтобы музыка НЕ ПРЕРЫВАЛАСЬ при переходе на паузу или экран победы.
        """
        pass

    def on_draw(self):
        self.window.clear()

        # Сначала фон
        with self.gui_camera.activate():
            self.background_list.draw()

        # Затем игровой мир
        with self.camera.activate():
            self.scene.draw()
            self.explosions.draw()

        # Затем интерфейс (GUI)
        with self.gui_camera.activate():
            self.heart_list.draw()
            self.gui_sprites.draw()

            # Монетки
            arcade.draw_text(f"x {self.score}", 65, 540, arcade.color.WHITE, 18, bold=True)

            # Таймер по центру с обводкой
            time_text = f"{self.total_time:.1f}"
            screen_center_x = self.window.width / 2
            y_pos = 590

            arcade.draw_text(time_text, screen_center_x + 2, y_pos - 2, arcade.color.BLACK, 30, anchor_x="center",
                             bold=True)
            arcade.draw_text(time_text, screen_center_x, y_pos, arcade.color.WHITE, 30, anchor_x="center", bold=True)

    def on_update(self, delta_time):
        self.total_time += delta_time
        self.physics.update()
        self.scene.update_animation(delta_time, ["Player"])

        # Таймер неуязвимости
        if self.player.invincible_timer > 0:
            self.player.invincible_timer -= delta_time
            self.player.alpha = 150 if int(self.player.invincible_timer * 10) % 2 == 0 else 255
        else:
            self.player.alpha = 255

        # Враги
        enemies = self.scene.get_sprite_list("Enemies")
        walls = self.scene.get_sprite_list("Walls")
        for enemy in enemies:
            enemy.update(walls)
            if arcade.check_for_collision_with_list(enemy, walls):
                enemy.reverse_direction()

        # Урон от падения
        if self.player.center_y < -100:
            self.handle_damage()

        # Шипы
        spike_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Spikes"])
        if spike_hit_list:
            self.handle_damage(spike_hit_list[0])

        # Столкновение с врагами
        enemy_hit_list = arcade.check_for_collision_with_list(self.player, enemies)
        for enemy in enemy_hit_list:
            if self.player.change_y < 0 and self.player.bottom > (enemy.center_y - 10):
                enemy.remove_from_sprite_lists()
                self.player.change_y = constants.PLAYER_JUMP_SPEED / 2
                arcade.play_sound(self.collect_sound)
            else:
                self.handle_damage(enemy)
                break

        # Аптечки
        heal_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Heals"])
        for heal in heal_hit_list:
            if self.lives < 3:
                self.lives += 1
                self.update_hearts()
                heal.remove_from_sprite_lists()
                arcade.play_sound(self.collect_sound)

        # Камера
        self.camera.position = arcade.math.lerp_2d(self.camera.position, self.player.position, 0.1)

        if self.physics.can_jump():
            self.player.jumps_count = 0

        # Сбор монет
        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Coins"])
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1
            arcade.play_sound(self.collect_sound)

        # Портал
        if arcade.check_for_collision_with_list(self.player, self.scene["Portal"]):
            self.finish_level()

    def handle_damage(self, source_sprite=None):
        if self.player.invincible_timer > 0:
            return

        self.lives -= 1
        self.update_hearts()
        arcade.play_sound(self.death_sound)

        if self.lives <= 0:
            self.window.show_view(GameOverView())
            return

        self.player.invincible_timer = 1.0

        if source_sprite:
            direction = 1 if self.player.center_x > source_sprite.center_x else -1
            self.player.change_x = direction * 5
            self.player.change_y = 6
        else:
            self.player.center_x, self.player.center_y = 128, 128
            self.player.change_x, self.player.change_y = 0, 0

    def finish_level(self):
        self.db.add_score(f"Игрок (Ур. {self.level})", self.score, round(self.total_time, 2))
        win_view = WinView()
        win_view.score = self.score
        win_view.final_time = self.total_time
        win_view.current_level = self.level
        self.window.show_view(win_view)

    def on_key_press(self, key, modifiers):
        if key in [arcade.key.UP, arcade.key.W]:
            if self.physics.can_jump():
                self.player.change_y = constants.PLAYER_JUMP_SPEED
                self.player.jumps_count = 1
                arcade.play_sound(self.jump_sound)
            elif getattr(self.player, 'jumps_count', 0) == 1:
                self.player.change_y = constants.PLAYER_JUMP_SPEED
                self.player.jumps_count = 2
                arcade.play_sound(self.jump_sound)

        elif key in [arcade.key.LEFT, arcade.key.A]:
            self.player.change_x = -constants.PLAYER_MOVEMENT_SPEED
        elif key in [arcade.key.RIGHT, arcade.key.D]:
            self.player.change_x = constants.PLAYER_MOVEMENT_SPEED

        if key == arcade.key.ESCAPE:
            if self.window.bg_music_player:
                self.window.bg_music_player.pause()
            pause = PauseView(self)
            self.window.show_view(pause)

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D]:
            self.player.change_x = 0