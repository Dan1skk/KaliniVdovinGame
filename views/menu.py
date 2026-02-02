import arcade
import constants
from views.game import GameView
from views.settings import SettingsView


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.levels = [1, 2]
        self.tiles = []
        self.settings_btn = {}
        self.exit_btn = {}

        self.background_list = arcade.SpriteList()
        self.bg_sprite = arcade.Sprite("assets/images/background4.jpg")
        self.bg_sprite.color = (100, 100, 100)
        self.background_list.append(self.bg_sprite)

        self.reposition_elements()

    def reposition_elements(self):
        width = self.window.width
        height = self.window.height

        self.bg_sprite.width = width
        self.bg_sprite.height = height
        self.bg_sprite.position = width / 2, height / 2

        w, h, margin = 160, 110, 40
        total_w = (w + margin) * len(self.levels) - margin
        start_x = (width - total_w) / 2 + (w / 2)

        self.tiles = []
        for i, lvl in enumerate(self.levels):
            self.tiles.append({
                "x": start_x + i * (w + margin),
                "y": height / 2,
                "w": w, "h": h, "lvl": lvl
            })

        # Кнопка настроек
        self.settings_btn = {"x": width / 2, "y": 130, "w": 200, "h": 50}
        # Кнопка выхода
        self.exit_btn = {"x": width / 2, "y": 60, "w": 200, "h": 50}

    def on_show_view(self):
        self.window.ctx.projection_2d = 0, self.window.width, 0, self.window.height
        self.reposition_elements()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.reposition_elements()

    def on_draw(self):
        self.clear()
        self.background_list.draw()

        arcade.draw_text("ВЫБОР УРОВНЯ", self.window.width / 2, self.window.height - 130,
                         arcade.color.WHITE, 35, anchor_x="center", bold=True)

        for t in self.tiles:
            arcade.draw_rect_filled(arcade.XYWH(t["x"], t["y"], t["w"], t["h"]), (44, 62, 80))
            arcade.draw_rect_outline(arcade.XYWH(t["x"], t["y"], t["w"], t["h"]), arcade.color.WHITE, 2)
            arcade.draw_text(f"УРОВЕНЬ {t['lvl']}", t["x"], t["y"],
                             arcade.color.WHITE, 18, anchor_x="center", anchor_y="center", bold=True)

        # Кнопка настроек
        arcade.draw_rect_filled(arcade.XYWH(self.settings_btn["x"], self.settings_btn["y"],
                                            self.settings_btn["w"], self.settings_btn["h"]), (100, 100, 100))
        arcade.draw_text("НАСТРОЙКИ", self.settings_btn["x"], self.settings_btn["y"],
                         arcade.color.WHITE, 16, anchor_x="center", anchor_y="center")

        # Кнопка выхода (красная)
        arcade.draw_rect_filled(arcade.XYWH(self.exit_btn["x"], self.exit_btn["y"],
                                            self.exit_btn["w"], self.exit_btn["h"]), (150, 50, 50))
        arcade.draw_text("ВЫХОД", self.exit_btn["x"], self.exit_btn["y"],
                         arcade.color.WHITE, 16, anchor_x="center", anchor_y="center")

    def on_mouse_press(self, x, y, button, modifiers):
        for t in self.tiles:
            if abs(x - t["x"]) < t["w"] / 2 and abs(y - t["y"]) < t["h"] / 2:
                game = GameView()
                game.level = t["lvl"]
                game.setup()
                self.window.show_view(game)
                return

        if abs(x - self.settings_btn["x"]) < self.settings_btn["w"] / 2 and \
                abs(y - self.settings_btn["y"]) < self.settings_btn["h"] / 2:
            self.window.show_view(SettingsView(self))
            return

        if abs(x - self.exit_btn["x"]) < self.exit_btn["w"] / 2 and \
                abs(y - self.exit_btn["y"]) < self.exit_btn["h"] / 2:
            arcade.exit()