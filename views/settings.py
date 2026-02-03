import arcade
import json
import os


class SettingsView(arcade.View):
    def __init__(self, prev_view):
        super().__init__()
        self.prev_view = prev_view
        self.settings_file = os.path.join("data", "settings.json")

    def save_settings(self):
        data = {
            "fullscreen": self.window.fullscreen,
            "volume": self.window.music_volume
        }
        with open(self.settings_file, "w") as f:
            json.dump(data, f)

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.window.ctx.projection_2d = 0, width, 0, height

    def on_draw(self):
        self.clear()
        cx, cy = self.window.width / 2, self.window.height / 2

        arcade.draw_text("НАСТРОЙКИ", cx, cy + 150,
                         arcade.color.WHITE, 35, anchor_x="center", bold=True)

        fs_status = "ВКЛ" if self.window.fullscreen else "ВЫКЛ"
        arcade.draw_text(f"Полный экран (F): {fs_status}", cx, cy + 50,
                         arcade.color.WHITE, 20, anchor_x="center")

        vol_percent = int(self.window.music_volume * 100)
        arcade.draw_text(f"Громкость музыки (+/-): {vol_percent}%",
                         cx, cy - 30, arcade.color.WHITE, 20, anchor_x="center")

        arcade.draw_text("Нажми ESC или M для выхода", cx, 100,
                         arcade.color.LIGHT_GRAY, 14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)
            self.window.ctx.projection_2d = 0, self.window.width, 0, self.window.height
            self.save_settings()

        elif key == arcade.key.EQUAL:
            self.window.music_volume = min(1.0, self.window.music_volume + 0.1)
            self.update_music()
            self.save_settings()

        elif key == arcade.key.MINUS:
            self.window.music_volume = max(0.0, self.window.music_volume - 0.1)
            self.update_music()
            self.save_settings()

        elif key == arcade.key.ESCAPE or key == arcade.key.M:
            self.window.show_view(self.prev_view)

    def update_music(self):
        if self.window.bg_music_player:
            self.window.bg_music_player.volume = self.window.music_volume