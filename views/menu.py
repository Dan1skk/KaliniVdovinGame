import arcade
import os
import constants
from views.game import GameView
from views.settings import SettingsView


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        # 1. АВТО-ПОИСК УРОВНЕЙ
        self.levels = []
        self.scan_levels()

        self.tiles = []
        self.settings_btn = {}
        self.exit_btn = {}

        self.background_list = arcade.SpriteList()
        self.bg_sprite = arcade.Sprite("assets/images/background4.jpg")
        self.bg_sprite.color = (200, 200, 200)
        self.background_list.append(self.bg_sprite)

        self.reposition_elements()

    def scan_levels(self):
        """Ищет все файлы mapX.txt в папке levels и добавляет их в список"""
        self.levels = []
        if os.path.exists("levels"):
            files = os.listdir("levels")
            for f in files:
                if f.startswith("map") and f.endswith(".txt"):
                    try:
                        # Достаем число из имени файла 'map1.txt' -> 1
                        num = int(f.replace("map", "").replace(".txt", ""))
                        self.levels.append(num)
                    except ValueError:
                        continue
            self.levels.sort()  # Чтобы шли по порядку: 1, 2, 3...

        # Если папка пуста, создаем хотя бы один
        if not self.levels:
            self.levels = [1]

    def reposition_elements(self):
        width, height = self.window.width, self.window.height
        self.bg_sprite.width, self.bg_sprite.height = width, height
        self.bg_sprite.position = width / 2, height / 2

        # Динамическая сетка плиток (теперь их может быть много)
        w, h, margin = 120, 90, 20
        # Считаем, сколько плиток влезет в один ряд (например, максимум 5)
        max_cols = 5

        self.tiles = []
        for i, lvl in enumerate(self.levels):
            row = i // max_cols
            col = i % max_cols

            # Центрируем ряды
            row_count = min(len(self.levels) - row * max_cols, max_cols)
            row_w = row_count * (w + margin) - margin
            start_x = (width - row_w) / 2 + (w / 2)

            self.tiles.append({
                "x": start_x + col * (w + margin),
                "y": height - 250 - row * (h + margin),
                "w": w, "h": h, "lvl": lvl
            })

        self.settings_btn = {"x": width / 2, "y": 120, "w": 200, "h": 40}
        self.exit_btn = {"x": width / 2, "y": 65, "w": 200, "h": 40}

    def on_show_view(self):
        self.window.ctx.projection_2d = 0, self.window.width, 0, self.window.height
        self.scan_levels()  # Пересканируем, если добавили файл на лету
        self.reposition_elements()

    def on_draw(self):
        self.clear()
        self.background_list.draw()
        arcade.draw_text("ВЫБОР УРОВНЯ", self.window.width / 2, self.window.height - 100,
                         arcade.color.WHITE, 35, anchor_x="center", bold=True)

        for t in self.tiles:
            arcade.draw_rect_filled(arcade.XYWH(t["x"], t["y"], t["w"], t["h"]), (44, 62, 80))
            arcade.draw_rect_outline(arcade.XYWH(t["x"], t["y"], t["w"], t["h"]), arcade.color.WHITE, 2)
            arcade.draw_text(f"{t['lvl']}", t["x"], t["y"],
                             arcade.color.WHITE, 24, anchor_x="center", anchor_y="center", bold=True)

        # Кнопки
        arcade.draw_rect_filled(arcade.XYWH(self.settings_btn["x"], self.settings_btn["y"], 200, 40), (100, 100, 100))
        arcade.draw_text("НАСТРОЙКИ", self.settings_btn["x"], self.settings_btn["y"], arcade.color.WHITE, 14,
                         anchor_x="center", anchor_y="center")

        arcade.draw_rect_filled(arcade.XYWH(self.exit_btn["x"], self.exit_btn["y"], 200, 40), (150, 50, 50))
        arcade.draw_text("ВЫХОД", self.exit_btn["x"], self.exit_btn["y"], arcade.color.WHITE, 14, anchor_x="center",
                         anchor_y="center")

    def on_mouse_press(self, x, y, button, modifiers):
        for t in self.tiles:
            if abs(x - t["x"]) < t["w"] / 2 and abs(y - t["y"]) < t["h"] / 2:
                game = GameView()
                game.level = t["lvl"]
                game.setup()
                self.window.show_view(game)
                return
        if abs(x - self.settings_btn["x"]) < 100 and abs(y - self.settings_btn["y"]) < 20:
            self.window.show_view(SettingsView(self))
        elif abs(x - self.exit_btn["x"]) < 100 and abs(y - self.exit_btn["y"]) < 20:
            arcade.exit()