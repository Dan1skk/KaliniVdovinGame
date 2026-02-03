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

        # Камеры
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        # Состояние игры
        self.score = 0
        self.lives = 3

        # --- ОПТИМИЗАЦИЯ ТЕКСТА ---
        # Создаем объекты один раз, чтобы не нагружать CPU в on_draw
        self.score_label = arcade.Text("", 65, 0, arcade.color.WHITE, 18, bold=True)
        self.timer_label = arcade.Text("", 0, 0, arcade.color.WHITE, 30, anchor_x="center", bold=True)

        # Coyote Time
        self.coyote_timer = 0
        self.COYOTE_DURATION = 0.15

        self.db = ScoreManager()

        # Списки спрайтов
        self.heart_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.gui_sprites = arcade.SpriteList()

        # Звуки
        self.death_sound = arcade.load_sound(":resources:sounds/lose1.wav")
        self.collect_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

    def setup(self):
        self.scene = arcade.Scene()
        self.gui_sprites.clear()
        self.background_list.clear()

        # Иконка монетки
        self.coin_icon = arcade.Sprite("assets/images/coin.png", 0.08)
        self.gui_sprites.append(self.coin_icon)

        # Фон (SpriteList работает быстрее одиночного спрайта)
        bg_path = "assets/images/background4.jpg"
        if os.path.exists(bg_path):
            self.background = arcade.Sprite(bg_path)
            self.background_list.append(self.background)

        # Инициализация слоев (spatial_hash=True ускоряет коллизии на слабых ПК)
        for name in ["Player", "Walls", "Coins", "Enemies", "Portal", "Heals", "Spikes"]:
            self.scene.add_sprite_list(name, use_spatial_hash=True)

        # Загрузка карты
        current_dir = os.path.dirname(__file__)
        assets_path = os.path.normpath(os.path.join(current_dir, "..", "assets", "images"))
        file_path = os.path.normpath(os.path.join(current_dir, "..", "levels", f"map{self.level}.txt"))

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                for row_index, line in enumerate(reversed(lines)):
                    for col_index, char in enumerate(line):
                        x, y = col_index * 64 + 32, row_index * 64 + 32
                        if char == "G":
                            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", constants.TILE_SCALING)
                            wall.position = (x, y);
                            self.scene.add_sprite("Walls", wall)
                        elif char == "W":
                            wall = arcade.Sprite(":resources:images/tiles/brickBrown.png", constants.TILE_SCALING)
                            wall.position = (x, y);
                            self.scene.add_sprite("Walls", wall)
                        elif char == "C":
                            coin = arcade.Sprite("assets/images/coin.png", scale=0.1)
                            coin.position = (x, y);
                            self.scene.add_sprite("Coins", coin)
                        elif char == "E":
                            portal = arcade.Sprite(":resources:images/items/gemBlue.png", 0.8)
                            portal.position = (x, y);
                            self.scene.add_sprite("Portal", portal)
                        elif char == "S":
                            enemy = Enemy(x, y);
                            self.scene.add_sprite("Enemies", enemy)
                        elif char == "H":
                            health = arcade.Sprite(os.path.join(assets_path, "heal.png"), 0.20)
                            health.position = (x, y);
                            self.scene.add_sprite("Heals", health)
                        elif char == "X":
                            spike = arcade.Sprite(os.path.join(assets_path, "shipi.png"))
                            spike.width, spike.height = 64, 20
                            spike.center_x, spike.bottom = x, y - 32
                            self.scene.add_sprite("Spikes", spike)

        self.player = Player()
        self.player.center_x, self.player.center_y = 128, 128
        self.scene.add_sprite("Player", self.player)

        self.physics = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=constants.GRAVITY, walls=self.scene["Walls"]
        )

        self.update_hearts()
        self.update_gui_positions()

    def update_hearts(self):
        self.heart_list.clear()
        for i in range(self.lives):
            heart = arcade.Sprite("assets/images/heart.png", 0.2)
            self.heart_list.append(heart)
        self.update_gui_positions()

    def update_gui_positions(self):
        """Вызывается только при ресайзе или старте, а не каждый кадр!"""
        w, h = self.window.width, self.window.height

        for i, heart in enumerate(self.heart_list):
            heart.center_x = 40 + (i * 40)
            heart.center_y = h - 40

        self.coin_icon.center_x = 40
        self.coin_icon.center_y = h - 90

        if hasattr(self, "background"):
            self.background.width, self.background.height = w, h
            self.background.position = w / 2, h / 2

        # Обновляем координаты статичных текстовых блоков
        self.timer_label.x = w / 2
        self.timer_label.y = h - 50

    def on_show_view(self):
        arcade.set_background_color(arcade.color.CORNFLOWER_BLUE)
        self.update_gui_positions()

        cur_player = getattr(self.window, "bg_music_player", None)
        if cur_player and cur_player.playing:
            return

        music_path = "assets/sounds/background_music.mp3"
        if os.path.exists(music_path):
            music = arcade.load_sound(music_path)
            vol = getattr(self.window, "music_volume", 0.1)
            self.window.bg_music_player = music.play(loop=True, volume=vol)

    def on_draw(self):
        self.clear()

        # Фон
        with self.gui_camera.activate():
            self.background_list.draw()

        # Игровой мир
        with self.camera.activate():
            self.scene.draw()

        # Интерфейс
        with self.gui_camera.activate():
            self.heart_list.draw()
            self.gui_sprites.draw()
            # Рисуем предзагруженный текст (в разы быстрее draw_text)
            self.score_label.draw()
            self.timer_label.draw()

    def on_update(self, delta_time):
        self.total_time += delta_time
        self.physics.update()
        self.scene.update_animation(delta_time, ["Player"])

        # Обновляем только данные в тексте, не пересоздавая его
        self.score_label.text = f"x {self.score}"
        self.score_label.y = self.coin_icon.center_y - 10
        self.timer_label.text = f"{self.total_time:.1f}"

        # Coyote Time
        if self.physics.can_jump():
            self.coyote_timer = self.COYOTE_DURATION
        else:
            self.coyote_timer -= delta_time

        # Инвиз при уроне
        if self.player.invincible_timer > 0:
            self.player.invincible_timer -= delta_time
            self.player.alpha = 150 if int(self.player.invincible_timer * 10) % 2 == 0 else 255
        else:
            self.player.alpha = 255

        # Логика врагов
        walls = self.scene["Walls"]
        spikes = self.scene["Spikes"]
        for enemy in self.scene["Enemies"]:
            enemy.update(walls, spikes)

        # Смерть от падения
        if self.player.center_y < -100:
            self.handle_damage()

        # Коллизии с шипами
        spike_hit = arcade.check_for_collision_with_list(self.player, spikes)
        if spike_hit:
            self.handle_damage(spike_hit[0])

        # Коллизии с врагами
        enemy_hit = arcade.check_for_collision_with_list(self.player, self.scene["Enemies"])
        for enemy in enemy_hit:
            if self.player.change_y < 0 and self.player.bottom > (enemy.center_y - 10):
                enemy.remove_from_sprite_lists()
                self.player.change_y = constants.PLAYER_JUMP_SPEED / 2
                arcade.play_sound(self.collect_sound)
            else:
                self.handle_damage(enemy)
                break

        # Монеты
        coin_hit = arcade.check_for_collision_with_list(self.player, self.scene["Coins"])
        for coin in coin_hit:
            coin.remove_from_sprite_lists()
            self.score += 1
            arcade.play_sound(self.collect_sound)

        # Портал
        if arcade.check_for_collision_with_list(self.player, self.scene["Portal"]):
            self.finish_level()

        # Камера (плавное следование)
        self.camera.position = arcade.math.lerp_2d(self.camera.position, self.player.position, 0.1)

        # Сброс прыжков
        if self.physics.can_jump():
            self.player.jumps_count = 0

    def handle_damage(self, source_sprite=None):
        if self.player.invincible_timer > 0:
            return
        self.lives -= 1
        self.update_hearts()
        arcade.play_sound(self.death_sound)

        if self.lives <= 0:
            self.window.show_view(GameOverView(self.level))
            return

        self.player.invincible_timer = 1.0
        if source_sprite:
            direction = 1 if self.player.center_x > source_sprite.center_x else -1
            self.player.change_x = direction * 5
            self.player.change_y = 6
        else:
            self.player.center_x, self.player.center_y = 128, 128

    def finish_level(self):
        self.db.add_score(f"Игрок (Ур. {self.level})", self.score, round(self.total_time, 2))
        win_view = WinView()
        win_view.score = self.score
        win_view.final_time = self.total_time
        win_view.current_level = self.level
        self.window.show_view(win_view)

    def on_key_press(self, key, modifiers):
        if key in [arcade.key.UP, arcade.key.W]:
            if self.physics.can_jump() or self.coyote_timer > 0:
                self.player.change_y = constants.PLAYER_JUMP_SPEED
                self.player.jumps_count = 1
                self.coyote_timer = 0
                arcade.play_sound(self.jump_sound)
            elif getattr(self.player, 'jumps_count', 0) == 1:
                self.player.change_y = constants.PLAYER_JUMP_SPEED
                self.player.jumps_count = 2
                arcade.play_sound(self.jump_sound)
        elif key in [arcade.key.LEFT, arcade.key.A]:
            self.player.change_x = -constants.PLAYER_MOVEMENT_SPEED
        elif key in [arcade.key.RIGHT, arcade.key.D]:
            self.player.change_x = constants.PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.ESCAPE:
            if self.window.bg_music_player:
                self.window.bg_music_player.pause()
            self.window.show_view(PauseView(self))

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D]:
            self.player.change_x = 0

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.camera.projection = (0, width, 0, height)
        self.gui_camera.projection = (0, width, 0, height)
        self.update_gui_positions()