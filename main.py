import arcade
import constants
from views.menu import MenuView

def main():
    # создаем окно
    window = arcade.Window(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, constants.SCREEN_TITLE)
    # кидаем в него меню
    window.show_view(MenuView())
    window.bg_music_player = None  # <--- Явно говорим, что музыки пока нет
    arcade.run()

if __name__ == "__main__":
    main()

    # initial commit