import arcade
import random
import constants
from models import ScoreManager


class MenuView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_BLUE)
        self.title_text = arcade.Text("PyJourney", constants.SCREEN_WIDTH / 2, 400,
                                      arcade.color.WHITE, 50, anchor_x="center")
        self.sub_text = arcade.Text("Жми ENTER и погнали", constants.SCREEN_WIDTH / 2, 300,
                                    arcade.color.WHITE, 20, anchor_x="center")

    def on_draw(self):
        self.window.clear()
        self.title_text.draw()
        self.sub_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.scene = None
        self.player = None
        self.physics = None
        self.camera = None
        self.score = 0
        self.db = ScoreManager()
        self.explosions = arcade.SpriteList()
        self.score_text = None

    def setup(self):
        # Камера в 3.0 теперь работает проще
        self.camera = arcade.camera.Camera2D()
        self.scene = arcade.Scene()

        self.score_text = arcade.Text(f"Счет: {self.score}", 0, 0, arcade.color.WHITE, 20)

        img = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        self.player = arcade.Sprite(img, constants.SPRITE_SCALING)
        self.player.center_x = 100
        self.player.center_y = 150
        self.scene.add_sprite("Player", self.player)

        # Рисуем землю
        for x in range(0, 3000, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", 0.5)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        # Раскидываем монетки
        self.scene.add_sprite_list("Coins")
        for i in range(15):
            coin = arcade.Sprite(":resources:images/items/gold_1.png", 0.4)
            coin.center_x = random.randrange(300, 2800)
            coin.center_y = 150
            self.scene.add_sprite("Coins", coin)

        self.physics = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=constants.GRAVITY, walls=self.scene["Walls"]
        )

    def on_draw(self):
        self.window.clear()

        # Используем камеру для игрового мира
        self.camera.use()
        self.scene.draw()
        self.explosions.draw()

        # Чтобы текст счета не прыгал, рисуем его через GUI-камеру (стандартное окно)
        # Но для простоты привяжем к координатам игрока, как ты хотел
        self.score_text.value = f"Счет: {self.score}"
        self.score_text.x = self.player.center_x - 450
        self.score_text.y = self.player.center_y + 250
        self.score_text.draw()

    def on_update(self, delta_time):
        self.physics.update()
        self.explosions.update()

        # Движение (чтобы точно ходил)
        if self.player.change_x != 0:
            self.player.center_x += self.player.change_x

        # ЦЕНТРОВКА В ARCADE 3.0
        # Просто передаем центр игрока, камера сама поймет масштаб
        self.camera.position = self.player.position

        # Монетки
        coins_hit = arcade.check_for_collision_with_list(self.player, self.scene["Coins"])
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.score += 1

        # Смерть
        if self.player.center_y < -200:
            self.db.add_score("Player1", self.score, 1)
            self.window.show_view(MenuView())

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics.can_jump():
                self.player.change_y = constants.PLAYER_JUMP_SPEED
                for _ in range(5):
                    p = arcade.SpriteCircle(3, arcade.color.WHITE)
                    p.center_x, p.center_y = self.player.center_x, self.player.bottom
                    p.change_x, p.change_y = random.uniform(-2, 2), random.uniform(-1, -3)
                    self.explosions.append(p)

        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = -constants.PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = constants.PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D]:
            self.player.change_x = 0