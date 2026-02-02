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
        self.total_time = 0  # тут будем хранить реально набежавшее время

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.score = 0
        self.lives = 3
        self.start_time = 0
        self.total_time = 0

        self.db = ScoreManager()
        self.explosions = arcade.SpriteList()
        self.heart_list = arcade.SpriteList()

        self.death_sound = arcade.load_sound(":resources:sounds/lose1.wav")
        self.collect_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

    def setup(self):
        self.start_time = time.time()
        self.scene = arcade.Scene()

        # создаем список для иконок интерфейса
        self.gui_sprites = arcade.SpriteList()

        self.coin_icon = arcade.Sprite("assets/images/coin.png", 0.1)
        self.coin_icon.center_x = 40
        self.coin_icon.center_y = 560

        # добавляем иконку в список
        self.gui_sprites.append(self.coin_icon)


        current_dir = os.path.dirname(__file__)
        assets_path = os.path.normpath(os.path.join(current_dir, "..", "assets", "images"))

        for name in ["Player", "Walls", "Coins", "Enemies", "Portal", "Heals", "Spikes"]:
            self.scene.add_sprite_list(name)

        file_path = os.path.normpath(os.path.join(current_dir, "..", "levels", f"map{self.level}.txt"))

        if not os.path.exists(file_path):
            print(f"файл карты не найден: {file_path}")
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
                        coin = arcade.Sprite("assets/images/coin.png", scale= 0.1)
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
        # инициализируем таймер неуязвимости у игрока
        self.player.invincible_timer = 0
        self.scene.add_sprite("Player", self.player)

        self.physics = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=constants.GRAVITY, walls=self.scene["Walls"]
        )

        self.update_hearts()

        # Иконка монетки для GUI
        self.coin_icon = arcade.Sprite("assets/images/coin.png", 0.35)
        self.coin_icon.center_x = 40
        self.coin_icon.center_y = 560  # Сразу под сердечками

    def update_hearts(self):
        # обновляем иконки жизней в интерфейсе
        self.heart_list.clear()
        for i in range(self.lives):
            heart = arcade.Sprite("assets/images/heart.png", 0.2)
            heart.center_x = 40 + (i * 40)
            heart.center_y = 600
            self.heart_list.append(heart)

    def on_draw(self):
        self.window.clear()

        with self.camera.activate():
            self.scene.draw()
            self.explosions.draw()

        with self.gui_camera.activate():
            # рисуем жизни
            self.heart_list.draw()

            # ТУТ ИСПРАВЛЕНО: рисуем список спрайтов интерфейса
            self.gui_sprites.draw()

            # число монет рядом
            arcade.draw_text(f"x {self.score}", 65, 550, arcade.color.WHITE, 18, bold=True)

            # 3. ТАЙМЕР ПО ЦЕНТРУ (с эффектом обводки)
            time_text = f"{self.total_time:.1f}"
            screen_center_x = self.window.width / 2
            y_pos = 600
            f_size = 30

            # Рисуем черную "тень/обводку"
            arcade.draw_text(time_text, screen_center_x + 2, y_pos - 2, arcade.color.BLACK, f_size, anchor_x="center",
                             bold=True)
            # Рисуем основной белый текст
            arcade.draw_text(time_text, screen_center_x, y_pos, arcade.color.WHITE, f_size, anchor_x="center",
                             bold=True)

    def on_update(self, delta_time):
        self.total_time += delta_time  # прибавляем время кадра
        self.physics.update()
        self.scene.update_animation(delta_time, ["Player"])

        # обработка таймера неуязвимости и мигания
        if self.player.invincible_timer > 0:
            self.player.invincible_timer -= delta_time
            self.player.alpha = 150 if int(self.player.invincible_timer * 10) % 2 == 0 else 255
        else:
            self.player.alpha = 255

        # движение врагов
        enemies = self.scene.get_sprite_list("Enemies")
        walls = self.scene.get_sprite_list("Walls")
        for enemy in enemies:
            enemy.update(walls)
            if arcade.check_for_collision_with_list(enemy, walls):
                enemy.reverse_direction()

        # проверка падения в яму
        if self.player.center_y < -100:
            self.handle_damage()  # тут без аргументов, сработает ТП на старт

        # проверка наступания на шипы
        spike_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Spikes"])
        if spike_hit_list:
            self.handle_damage(spike_hit_list[0])  # передаем шип, чтобы от него отпрыгнуть

        # столкновение с врагами (теперь вне блока ямы)
        enemy_hit_list = arcade.check_for_collision_with_list(self.player, enemies)
        for enemy in enemy_hit_list:
            # если падаем сверху - убиваем врага
            if self.player.change_y < 0 and self.player.bottom > (enemy.center_y - 10):
                enemy.remove_from_sprite_lists()
                self.player.change_y = constants.PLAYER_JUMP_SPEED / 2
                arcade.play_sound(self.collect_sound)
            else:
                # иначе получаем урон и отлетаем
                self.handle_damage(enemy)
                break

        # сбор аптечек
        heal_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Heals"])
        for heal in heal_hit_list:
            if self.lives < 3:
                self.lives += 1
                self.update_hearts()
                heal.remove_from_sprite_lists()
                arcade.play_sound(self.collect_sound)

        # плавное следование камеры
        self.camera.position = arcade.math.lerp_2d(self.camera.position, self.player.position, 0.1)

        if self.physics.can_jump():
            self.player.jumps_count = 0

        # сбор монет
        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Coins"])
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1
            arcade.play_sound(self.collect_sound)

        # переход в портал
        if arcade.check_for_collision_with_list(self.player, self.scene["Portal"]):
            self.finish_level()

    def handle_damage(self, source_sprite=None):
        # если еще мигаем, то урон игнорим
        if self.player.invincible_timer > 0:
            return

        self.lives -= 1
        self.update_hearts()
        arcade.play_sound(self.death_sound)

        if self.lives <= 0:
            self.window.show_view(GameOverView())
            return

        # включаем неуязвимость на 1 секунду
        self.player.invincible_timer = 1.0

        if source_sprite:
            # если это враг или шипы — даем легкий пинок
            # определяем направление отскока (от центра объекта)
            direction = 1 if self.player.center_x > source_sprite.center_x else -1
            self.player.change_x = direction * 5  # легкий толчок вбок
            self.player.change_y = 6  # подскок вверх чуть выше, чтобы выпрыгнуть из шипов
        else:
            # это только для падения в бездну
            self.player.center_x, self.player.center_y = 128, 128
            self.player.change_x, self.player.change_y = 0, 0

    def finish_level(self):
        self.total_time = round(time.time() - self.start_time, 2)
        self.db.add_score(f"Игрок (Ур. {self.level})", self.score, self.total_time)
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
        elif key == arcade.key.ESCAPE:
            # создаем экран паузы и передаем ему "себя" (self)
            pause_view = PauseView(self)
            self.window.show_view(pause_view)

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D]:
            self.player.change_x = 0

    def on_show_view(self):
        arcade.set_background_color(arcade.color.CORNFLOWER_BLUE)