import arcade


class GameOverView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text("ИГРА ОКОНЧЕНА", self.window.width / 2, self.window.height / 2 + 50,
                         arcade.color.RED, 50, anchor_x="center")

        arcade.draw_text("Нажми R, чтобы начать заново", self.window.width / 2, self.window.height / 2 - 20,
                         arcade.color.WHITE, 20, anchor_x="center")

        arcade.draw_text("Нажми M, чтобы выйти в меню", self.window.width / 2, self.window.height / 2 - 60,
                         arcade.color.LIGHT_GRAY, 18, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            from views.game import GameView
            game = GameView()
            game.setup()
            self.window.show_view(game)
        elif key == arcade.key.M:
            from views.menu import MenuView
            self.window.show_view(MenuView())