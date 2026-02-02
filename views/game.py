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

        # Таймер койота: сколько времени игрок может прыгать после схода с платформы
        self.coyote_timer = 0
        self.COYOTE_DURATION = 1  # Время в секундах

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

        self.gui_sprites.clear()
        self.background_list.clear()

        current_dir = os.path.dirname(__file__)
        assets_path = os.path.normpath(os.path.join(current_dir, "..", "assets", "images"))

        # Иконка монетки (позиция теперь обновится в update_gui_positions)
        self.coin_icon = arcade.Sprite("assets/images/coin.png", 0.08)
        self.gui_sprites.append(self.coin_icon)

        # Фон
        bg_path = "assets/images/background4.jpg"
        if os.path.exists(bg_path):
            self.background = arcade.Sprite(bg_path)
            self.background.width = self.window.width
            self.background.height = self.window.height
            self.background.position = self.window.width / 2, self.window.height / 2
            self.background_list.append(self.background)

        for name in ["Player", "Walls", "Coins", "Enemies", "Portal", "Heals", "Spikes"]:
            self.scene.add_sprite_list(name)

        file_path = os.path.normpath(os.path.join(current_dir, "..", "levels", f"map{self.level}.txt"))

        if os.path.exists(file_path):
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
        """Привязываем элементы GUI к краям экрана динамически"""
        top = self.window.height
        # Сердечки в левом верхнем углу
        for i, heart in enumerate(self.heart_list):
            heart.center_x = 40 + (i * 40)
            heart.center_y = top - 40

        # Монетка под сердечками
        self.coin_icon.center_x = 40
        self.coin_icon.center_y = top - 90

    def on_show_view(self):
        arcade.set_background_color(arcade.color.CORNFLOWER_BLUE)
        self.update_gui_positions()  # Обновляем при входе

        current_player = getattr(self.window, "bg_music_player", None)
        if current_player and current_player.playing:
            return

        music_path = "assets/sounds/background_music.mp3"
        if os.path.exists(music_path):
            music = arcade.load_sound(music_path)
            vol = getattr(self.window, "music_volume", 0.1)
            self.window.bg_music_player = music.play(loop=True, volume=vol)

    def on_draw(self):
        self.clear()
        # Постоянно проверяем позиции GUI на случай ресайза
        self.update_gui_positions()

        with self.gui_camera.activate():
            self.background_list.draw()

        with self.camera.activate():
            self.scene.draw()
            self.explosions.draw()

        with self.gui_camera.activate():
            self.heart_list.draw()
            self.gui_sprites.draw()

            # Текст монет привязан к иконке
            arcade.draw_text(f"x {self.score}", 65, self.coin_icon.center_y - 10,
                             arcade.color.WHITE, 18, bold=True)

            # Таймер по центру сверху
            time_text = f"{self.total_time:.1f}"
            arcade.draw_text(time_text, self.window.width / 2, self.window.height - 50,
                             arcade.color.WHITE, 30, anchor_x="center", bold=True)

    def on_update(self, delta_time):
        self.total_time += delta_time
        self.physics.update()
        self.scene.update_animation(delta_time, ["Player"])

        if self.physics.can_jump():
            self.coyote_timer = self.COYOTE_DURATION
        else:
            self.coyote_timer -= delta_time

        if self.player.invincible_timer > 0:
            self.player.invincible_timer -= delta_time
            self.player.alpha = 150 if int(self.player.invincible_timer * 10) % 2 == 0 else 255
        else:
            self.player.alpha = 255

        enemies = self.scene.get_sprite_list("Enemies")
        walls = self.scene.get_sprite_list("Walls")
        spikes = self.scene.get_sprite_list("Spikes")  # Достаем список шипов

        for enemy in enemies:
            # Передаем и стены, и шипы в метод update слайма
            enemy.update(walls, spikes)

        if self.player.center_y < -100:
            self.handle_damage()

        spike_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Spikes"])
        if spike_hit_list:
            self.handle_damage(spike_hit_list[0])

        enemy_hit_list = arcade.check_for_collision_with_list(self.player, enemies)
        for enemy in enemy_hit_list:
            if self.player.change_y < 0 and self.player.bottom > (enemy.center_y - 10):
                enemy.remove_from_sprite_lists()
                self.player.change_y = constants.PLAYER_JUMP_SPEED / 2
                arcade.play_sound(self.collect_sound)
            else:
                self.handle_damage(enemy)
                break

        heal_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Heals"])
        for heal in heal_hit_list:
            if self.lives < 3:
                self.lives += 1
                self.update_hearts()
                heal.remove_from_sprite_lists()
                arcade.play_sound(self.collect_sound)

        self.camera.position = arcade.math.lerp_2d(self.camera.position, self.player.position, 0.1)

        if self.physics.can_jump():
            self.player.jumps_count = 0

        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Coins"])
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1
            arcade.play_sound(self.collect_sound)

        if arcade.check_for_collision_with_list(self.player, self.scene["Portal"]):
            self.finish_level()

    def handle_damage(self, source_sprite=None):
        if self.player.invincible_timer > 0:
            return
        self.lives -= 1
        self.update_hearts()
        arcade.play_sound(self.death_sound)
        if self.lives <= 0:
            self.window.show_view(GameOverView(self.level))  # Передаем self.level!
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
            # Прыгаем, если мы на земле ИЛИ если таймер койота активен
            if self.physics.can_jump() or self.coyote_timer > 0:
                self.player.change_y = constants.PLAYER_JUMP_SPEED
                self.player.jumps_count = 1
                self.coyote_timer = 0  # Обнуляем, чтобы нельзя было прыгнуть "дважды" в воздухе без двойного прыжка
                arcade.play_sound(self.jump_sound)

            # Двойной прыжок (если он у тебя реализован через jumps_count)
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
            self.window.show_view(PauseView(self))

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D]:
            self.player.change_x = 0

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        # Обновляем камеры, чтобы интерфейс не сжимался
        self.camera.projection = (0, width, 0, height)
        self.gui_camera.projection = (0, width, 0, height)
        if hasattr(self, "background"):
            self.background.width = width
            self.background.height = height
            self.background.position = width / 2, height / 2
        self.update_gui_positions()