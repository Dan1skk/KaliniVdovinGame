import arcade
import time
import constants
from models import ScoreManager
from entities.player import Player
from entities.enemy import Enemy

# 1. Сначала МЕНЮ (так как main.py ищет его первым)
class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.title_text = arcade.Text(
            "PyJourney: Нажми ENTER, чтобы начать",
            constants.SCREEN_WIDTH / 2,
            constants.SCREEN_HEIGHT / 2,
            arcade.color.WHITE,
            20,
            anchor_x="center"
        )

    def on_show_view(self):
        arcade.set_background_color(arcade.color.CORNFLOWER_BLUE)

    def on_draw(self):
        self.window.clear()
        self.title_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)



# 2. Потом ЭКРАН ПОБЕДЫ
class WinView(arcade.View):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.final_time = 0

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.window.clear()
        arcade.draw_text("УРОВЕНЬ ПРОЙДЕН!", constants.SCREEN_WIDTH/2, 450, arcade.color.WHITE, 30, anchor_x="center")
        arcade.draw_text(f"Монеты: {self.score}", constants.SCREEN_WIDTH/2, 350, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text(f"Время: {self.final_time} сек.", constants.SCREEN_WIDTH/2, 300, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Нажми ESC для выхода", constants.SCREEN_WIDTH/2, 150, arcade.color.WHITE, 14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.exit()



class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.scene = None
        self.player = None
        self.physics = None

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.score = 0
        self.start_time = 0  # Время начала
        self.total_time = 0  # Итоговое время

        self.db = ScoreManager()
        self.explosions = arcade.SpriteList()

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

        with open("map.txt", "r") as map_file:
            lines = map_file.readlines()
            for row_index, line in enumerate(reversed(lines)):
                for col_index, char in enumerate(line.strip()):
                    x, y = col_index * 64, row_index * 64

                    # --- ЭТО СПАВН СУЩНОСТЕЙ ПО БУКВАМ УКАЗАННЫМ В МАПЕ ---
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
                    elif char == "E":  # ПОРТАЛ
                        portal = arcade.Sprite(":resources:images/items/gemBlue.png", scale=0.8)
                        portal.center_x, portal.center_y = x, y
                        self.scene.add_sprite("Portal", portal)
                    # --- ДОБАВЛЯЕМ ЭТОТ БЛОК ---
                    elif char == "S":  # ВРАГ
                        enemy = Enemy(x, y)
                        self.scene.add_sprite("Enemies", enemy)

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
            # Показываем счет и время на экране
            current_elapsed = time.time() - self.start_time
            arcade.draw_text(f"Монеты: {self.score}  |  Время: {current_elapsed:.1f}с",
                             20, 580, arcade.color.WHITE, 16)

    def on_update(self, delta_time):
        self.physics.update()
        self.scene.update_animation(delta_time, ["Player"])

        # Логика врагов
        enemies = self.scene.get_sprite_list("Enemies")
        for enemy in enemies:
            enemy.update()

            # Проверка столкновения со стенами для разворота
            if arcade.check_for_collision_with_list(enemy, self.scene["Walls"]):
                enemy.reverse_direction()

        # Проверка смерти игрока
        if arcade.check_for_collision_with_list(self.player, enemies):
            # Рестарт уровня или вызов экрана смерти
            self.setup()


        self.explosions.update()
        self.camera.position = arcade.math.lerp_2d(self.camera.position, self.player.position, 0.1)

        # ОБНУЛЯЕМ СЧЕТЧИК, когда коснулись земли
        if self.physics.can_jump():
            self.player.jumps_count = 0
        # Сбор монет
        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Coins"])
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1
            arcade.play_sound(self.collect_sound)

        # КАСАНИЕ ПОРТАЛА (Конец игры)
        if arcade.check_for_collision_with_list(self.player, self.scene["Portal"]):
            self.total_time = round(time.time() - self.start_time, 2)
            # Записываем в рекорды: Имя, Монеты, Время
            self.db.add_score("Игрок", self.score, self.total_time)

            win_view = WinView()
            win_view.score = self.score
            win_view.final_time = self.total_time
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
