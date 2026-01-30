import arcade
import constants
# УБИРАЕМ импорт GameView отсюда!

class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.window.clear()
        arcade.draw_text("GAME OVER", constants.SCREEN_WIDTH/2, 400,
                         arcade.color.RED, 50, anchor_x="center")
        arcade.draw_text("Ты проиграл все 3 жизни, бро...", constants.SCREEN_WIDTH/2, 300,
                         arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Нажми ENTER, чтобы начать заново", constants.SCREEN_WIDTH/2, 200,
                         arcade.color.GRAY, 16, anchor_x="center")
        arcade.draw_text("Нажми ESC для выхода", constants.SCREEN_WIDTH/2, 150,
                         arcade.color.GRAY, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            # ИМПОРТИРУЕМ ПРЯМО ЗДЕСЬ
            from views.game import GameView
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.ESCAPE:
            arcade.exit()