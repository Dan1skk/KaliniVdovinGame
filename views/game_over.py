import arcade

class GameOverView(arcade.View):
    def __init__(self, failed_level):
        super().__init__()
        self.failed_level = failed_level # Запоминаем, на каком уровне слились

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text("ИГРА ОКОНЧЕНА", self.window.width / 2, self.window.height / 2 + 50,
                         arcade.color.RED, 50, anchor_x="center", bold=True)

        arcade.draw_text(f"Уровень {self.failed_level} не пройден", self.window.width / 2, self.window.height / 2,
                         arcade.color.WHITE, 20, anchor_x="center")

        arcade.draw_text("Нажми R, чтобы попробовать снова", self.window.width / 2, self.window.height / 2 - 50,
                         arcade.color.WHITE, 18, anchor_x="center")

        arcade.draw_text("Нажми M, чтобы выйти в меню", self.window.width / 2, self.window.height / 2 - 90,
                         arcade.color.LIGHT_GRAY, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            from views.game import GameView
            game = GameView()
            game.level = self.failed_level # Запускаем именно тот же уровень
            game.setup()
            self.window.show_view(game)
        elif key == arcade.key.M:
            from views.menu import MenuView
            self.window.show_view(MenuView())