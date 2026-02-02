import arcade


class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_draw(self):
        # Рисуем игру на заднем плане, чтобы игрок видел, где остановился
        self.game_view.on_draw()

        # Затемняющий фильтр (используем Rect для Arcade 3.0+)
        arcade.draw_rect_filled(
            arcade.XYWH(self.window.width / 2, self.window.height / 2,
                        self.window.width, self.window.height),
            (0, 0, 0, 150)
        )

        arcade.draw_text("ПАУЗА", self.window.width / 2, self.window.height / 2 + 50,
                         arcade.color.WHITE, 50, anchor_x="center")

        arcade.draw_text("Нажми ESC, чтобы продолжить", self.window.width / 2, self.window.height / 2 - 20,
                         arcade.color.WHITE, 20, anchor_x="center")

        arcade.draw_text("Нажми M, чтобы выйти в меню", self.window.width / 2, self.window.height / 2 - 60,
                         arcade.color.LIGHT_GRAY, 18, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            # Возвращаемся в текущую игру
            self.window.show_view(self.game_view)

        elif key == arcade.key.M:
            # Выходим в главное меню
            from views.menu import MenuView
            menu_view = MenuView()
            self.window.show_view(menu_view)