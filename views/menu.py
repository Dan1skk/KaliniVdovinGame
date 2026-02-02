import arcade
import constants
from views.game import GameView


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.levels = [1, 2]
        self.tiles = []
        self.settings_tile = {"x": constants.SCREEN_WIDTH / 2, "y": 100, "w": 200, "h": 50}

        # Параметры плиток
        w, h, margin = 160, 110, 40
        total_w = (w + margin) * len(self.levels) - margin
        start_x = (constants.SCREEN_WIDTH - total_w) / 2 + (w / 2)

        for i, lvl in enumerate(self.levels):
            self.tiles.append({
                "x": start_x + i * (w + margin),
                "y": constants.SCREEN_HEIGHT / 2,
                "w": w, "h": h, "lvl": lvl
            })

        # Создаем список для фона (в Arcade 3.0 это самый надежный способ)
        self.background_list = arcade.SpriteList()
        background = arcade.Sprite("assets/images/background4.jpg")
        background.width = constants.SCREEN_WIDTH
        background.height = constants.SCREEN_HEIGHT
        background.position = constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2
        background.color = (100, 100, 100)
        self.background_list.append(background)

    def on_draw(self):
        self.clear()

        # Рисуем список с фоном
        self.background_list.draw()

        arcade.draw_text("ВЫБОР УРОВНЯ", constants.SCREEN_WIDTH / 2, 520,
                         arcade.color.WHITE, 35, anchor_x="center", bold=True)

        for t in self.tiles:
            # Плитки (используем draw_rect_filled для 3.0+)
            arcade.draw_rect_filled(
                arcade.XYWH(t["x"], t["y"], t["w"], t["h"]),
                (44, 62, 80)
            )
            arcade.draw_rect_outline(
                arcade.XYWH(t["x"], t["y"], t["w"], t["h"]),
                arcade.color.WHITE, 2
            )

            arcade.draw_text(f"УРОВЕНЬ {t['lvl']}", t["x"], t["y"],
                             arcade.color.WHITE, 18, anchor_x="center", anchor_y="center", bold=True)

        arcade.draw_text("Нажми на плитку, чтобы начать", constants.SCREEN_WIDTH / 2, 180,
                         arcade.color.LIGHT_GRAY, 14, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        for t in self.tiles:
            if abs(x - t["x"]) < t["w"] / 2 and abs(y - t["y"]) < t["h"] / 2:
                game = GameView()
                game.level = t["lvl"]
                game.setup()
                self.window.show_view(game)