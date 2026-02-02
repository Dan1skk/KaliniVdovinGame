import arcade
import constants
from views.game import GameView
from views.settings import SettingsView
import json
import os


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.levels = [1, 2]
        self.tiles = []
        self.settings_btn = {}

        # Создаем список спрайтов для фона
        self.background_list = arcade.SpriteList()
        self.bg_sprite = arcade.Sprite("assets/images/background4.jpg")
        self.bg_sprite.color = (100, 100, 100)
        self.background_list.append(self.bg_sprite)

        # Рассчитываем позиции элементов первый раз
        self.reposition_elements()

    def reposition_elements(self):
        """Динамически пересчитывает координаты всех элементов под текущий размер окна"""
        width = self.window.width
        height = self.window.height

        # 1. Растягиваем фон на всё окно
        self.bg_sprite.width = width
        self.bg_sprite.height = height
        self.bg_sprite.position = width / 2, height / 2

        # 2. Плитки выбора уровней
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

        # 3. Кнопка настроек (всегда внизу по центру)
        self.settings_btn = {"x": width / 2, "y": 80, "w": 200, "h": 50}

    def on_show_view(self):
        """Вызывается при переключении на это вью"""
        # В Arcade 3.0+ вместо set_viewport используем обновление проекции окна
        self.window.ctx.projection_2d = 0, self.window.width, 0, self.window.height
        self.reposition_elements()

    def on_resize(self, width: int, height: int):
        """Вызывается автоматически при изменении размера окна или Fullscreen"""
        super().on_resize(width, height)
        self.reposition_elements()

    def on_draw(self):
        self.clear()

        # Рисуем фон
        self.background_list.draw()

        # Заголовок (динамически по центру сверху)
        arcade.draw_text("ВЫБОР УРОВНЯ", self.window.width / 2, self.window.height - 130,
                         arcade.color.WHITE, 35, anchor_x="center", bold=True)

        # Рисуем плитки уровней
        for t in self.tiles:
            # Тело плитки
            arcade.draw_rect_filled(
                arcade.XYWH(t["x"], t["y"], t["w"], t["h"]),
                (44, 62, 80)
            )
            # Рамка
            arcade.draw_rect_outline(
                arcade.XYWH(t["x"], t["y"], t["w"], t["h"]),
                arcade.color.WHITE, 2
            )
            # Текст уровня
            arcade.draw_text(f"УРОВЕНЬ {t['lvl']}", t["x"], t["y"],
                             arcade.color.WHITE, 18, anchor_x="center", anchor_y="center", bold=True)

        # Текст-подсказка
        arcade.draw_text("Нажми на плитку, чтобы начать", self.window.width / 2, 180,
                         arcade.color.LIGHT_GRAY, 14, anchor_x="center")

        # Кнопка настроек
        arcade.draw_rect_filled(
            arcade.XYWH(self.settings_btn["x"], self.settings_btn["y"],
                        self.settings_btn["w"], self.settings_btn["h"]),
            (100, 100, 100)
        )
        arcade.draw_text("НАСТРОЙКИ", self.settings_btn["x"], self.settings_btn["y"],
                         arcade.color.WHITE, 16, anchor_x="center", anchor_y="center")

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатий мыши"""
        # Проверяем клик по плиткам уровней
        for t in self.tiles:
            if abs(x - t["x"]) < t["w"] / 2 and abs(y - t["y"]) < t["h"] / 2:
                game = GameView()
                game.level = t["lvl"]
                game.setup()
                self.window.show_view(game)
                return

        # Проверяем клик по кнопке настроек
        if abs(x - self.settings_btn["x"]) < self.settings_btn["w"] / 2 and \
                abs(y - self.settings_btn["y"]) < self.settings_btn["h"] / 2:
            self.window.show_view(SettingsView(self))