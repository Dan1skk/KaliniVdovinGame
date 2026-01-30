import arcade
import random
import constants
from models import ScoreManager
from character import Player  # Импортируем твой обновленный класс игрока


# --- ЭКРАН ПОБЕДЫ ---
class WinView(arcade.View):
    def __init__(self):
        super().__init__()
        self.score = 0

    def on_show_view(self):
        # Было: arcade.set_background_color(arcade.color.GREEN_CYAN)
        arcade.set_background_color(arcade.color.AMAZON)  # Этот точно есть

    def on_draw(self):
        self.window.clear()
        arcade.draw_text("ПОБЕДА!", constants.SCREEN_WIDTH / 2, 400,
                         arcade.color.WHITE, 40, anchor_x="center")
        arcade.draw_text(f"Ваш счет: {self.score}", constants.SCREEN_WIDTH / 2, 300,
                         arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text("Нажмите ESC для возврата в меню", constants.SCREEN_WIDTH / 2, 200,
                         arcade.color.WHITE, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())


# --- ГЛАВНОЕ МЕНЮ ---
class MenuView(arcade.View):
    def on_show_view(self):
        # Было: arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        arcade.set_background_color(arcade.color.CORNFLOWER_BLUE)

    def on_draw(self):
        self.window.clear()
        arcade.draw_text("PyJourney: Нажми ENTER, чтобы начать", constants.SCREEN_WIDTH / 2, 325,
                         arcade.color.WHITE, 20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)


# --- ИГРОВОЙ ПРОЦЕСС ---
class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.scene = None
        self.player = None
        self.physics = None

        # Камеры в 3.0+
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.score = 0
        self.db = ScoreManager()
        self.explosions = arcade.SpriteList()  # Для частиц (ФТ-5)

        # Звуки
        self.collect_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

    def setup(self):
        self.scene = arcade.Scene()

        # 1. Создаем игрока (используем твой класс из character.py)
        self.player = Player()
        self.player.center_x = 128
        self.player.center_y = 128
        self.scene.add_sprite("Player", self.player)

        # 2. Создаем пол (Walls)
        for x in range(0, 2000, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=0.5)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        # 3. Раскидываем монетки
        for x in range(200, 1800, 256):
            coin = arcade.Sprite(":resources:images/items/coinGold.png", scale=0.5)
            coin.center_x = x
            coin.center_y = 150
            self.scene.add_sprite("Coins", coin)

        # 4. Физика
        self.physics = arcade.PhysicsEnginePlatformer(
            self.player,
            gravity_constant=constants.GRAVITY,
            walls=self.scene["Walls"]
        )

    def on_draw(self):
        self.window.clear()

        # Отрисовка мира с камерой (ФТ-3)
        with self.camera.activate():
            self.scene.draw()
            self.explosions.draw()

        # Отрисовка интерфейса
        with self.gui_camera.activate():
            arcade.draw_text(f"Счет: {self.score}", 20, 600, arcade.color.WHITE, 18)

    def on_update(self, delta_time):
        self.physics.update()
        self.scene.update_animation(delta_time, ["Player"])  # ФТ-4
        self.explosions.update()

        # Слежение камеры (ФТ-3)
        self.camera.position = arcade.math.lerp_2d(self.camera.position, self.player.position, 0.1)

        # Сбор монет и частицы (ФТ-5)
        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Coins"])
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1
            arcade.play_sound(self.collect_sound)
            # Создаем искры
            for _ in range(5):
                particle = arcade.SpriteCircle(3, arcade.color.GOLD)
                particle.center_x, particle.center_y = coin.center_x, coin.center_y
                particle.change_x, particle.change_y = random.uniform(-3, 3), random.uniform(-3, 3)
                self.explosions.append(particle)

        # Проверка победы или падения
        if self.score >= 5:
            win_view = WinView()
            win_view.score = self.score
            self.db.add_score("Player1", self.score, 1)  # Сохраняем в CSV (ФТ-6)
            self.window.show_view(win_view)

        if self.player.center_y < -100:
            self.window.show_view(MenuView())

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics.can_jump():
                self.player.change_y = constants.PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = -constants.PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = constants.PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D]:
            self.player.change_x = 0