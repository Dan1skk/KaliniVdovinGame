import arcade
import constants

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
            from views.game import GameView  # Импорт внутри, чтобы не было ошибки
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)