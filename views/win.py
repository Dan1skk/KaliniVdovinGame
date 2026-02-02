import os
import arcade


class WinView(arcade.View):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.final_time = 0
        self.current_level = 1

    def on_draw(self):
        self.clear()
        # Золотой текст для победы
        arcade.draw_text(f"УРОВЕНЬ {self.current_level} ПРОЙДЕН!", self.window.width / 2, 450,
                         arcade.color.GOLD, 40, anchor_x="center", bold=True)

        # Красиво форматируем время до десятых
        arcade.draw_text(f"Счет: {self.score}  |  Время: {self.final_time:.1f}с",
                         self.window.width / 2, 350, arcade.color.WHITE, 24, anchor_x="center")

        arcade.draw_text("Нажми ENTER, чтобы продолжить", self.window.width / 2, 200,
                         arcade.color.WHITE, 18, anchor_x="center")

        arcade.draw_text("Нажми M, чтобы выйти в меню", self.window.width / 2, 160,
                         arcade.color.LIGHT_GRAY, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            import os
            from views.game import GameView

            # 1. Вычисляем номер следующего уровня
            next_level = self.current_level + 1
            file_path = f"levels/map{next_level}.txt"

            # 2. Проверяем, существует ли такой файл
            if os.path.exists(file_path):
                game = GameView()
                game.level = next_level
                game.setup()
                self.window.show_view(game)
            else:
                # Если файлов больше нет — поздравляем, игра пройдена, идем в меню
                from views.menu import MenuView
                self.window.show_view(MenuView())

        elif key == arcade.key.M:
            from views.menu import MenuView
            self.window.show_view(MenuView())

        elif key == arcade.key.M:
            from views.menu import MenuView
            self.window.show_view(MenuView())