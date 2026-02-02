import arcade
import constants


#
class WinView(arcade.View):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.final_time = 0
        self.current_level = 1  # Новое поле

    def on_draw(self):
        self.window.clear()
        arcade.draw_text(f"УРОВЕНЬ {self.current_level} ПРОЙДЕН!", constants.SCREEN_WIDTH / 2, 450,
                         arcade.color.GOLD, 40, anchor_x="center")
        arcade.draw_text(f"Счет: {self.score} | Время: {self.final_time:.1f}с", constants.SCREEN_WIDTH / 2, 350,
                         arcade.color.WHITE, 20, anchor_x="center")

        # Текст подсказки
        hint = "Нажми ENTER, чтобы идти дальше" if self.current_level < 2 else "Ты прошел всю игру! Нажми ENTER для меню"
        arcade.draw_text(hint, constants.SCREEN_WIDTH / 2, 200, arcade.color.WHITE, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            if self.current_level < 2:
                from views.game import GameView
                next_game = GameView()
                next_game.level = self.current_level + 1  # Ставим следующий лвл
                next_game.setup()
                self.window.show_view(next_game)
            else:
                from views.menu import MenuView
                self.window.show_view(MenuView())
