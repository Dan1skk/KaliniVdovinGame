import arcade
import constants
import json
import os
from views.menu import MenuView


def main():
    # Настройки по умолчанию
    fullscreen = False
    volume = 0.1

    # Загружаем настройки, если файл существует
    if os.path.exists("settings.json"):
        try:
            with open("settings.json", "r") as f:
                data = json.load(f)
                fullscreen = data.get("fullscreen", False)
                volume = data.get("volume", 0.1)
        except Exception:
            pass

    # Создаем окно с учетом загруженного фуллскрина
    window = arcade.Window(
        constants.SCREEN_WIDTH,
        constants.SCREEN_HEIGHT,
        constants.SCREEN_TITLE,
        fullscreen=fullscreen
    )

    # Сохраняем значения в объект окна
    window.music_volume = volume
    window.bg_music_player = None

    window.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()