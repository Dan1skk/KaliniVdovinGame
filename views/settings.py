import arcade
import constants


class SettingsView(arcade.View):
    def __init__(self, prev_view):
        super().__init__()
        self.prev_view = prev_view

        # Проверяем наличие громкости в окне, иначе ставим дефолт
        if not hasattr(self.window, "music_volume"):
            self.window.music_volume = 0.1  # Можешь заменить на constants.DEFAULT_MUSIC_VOLUME

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        # Для Arcade 3.0+
        self.window.ctx.projection_2d = 0, width, 0, height

    def on_draw(self):
        self.clear()

        # Центрируем всё относительно текущего размера окна
        cx = self.window.width / 2
        cy = self.window.height / 2

        arcade.draw_text("НАСТРОЙКИ", cx, cy + 150,
                         arcade.color.WHITE, 35, anchor_x="center", bold=True)

        # Статус фуллскрина
        fs_status = "ВКЛ" if self.window.fullscreen else "ВЫКЛ"
        arcade.draw_text(f"Полный экран (F): {fs_status}", cx, cy + 50,
                         arcade.color.WHITE, 20, anchor_x="center")

        # Громкость музыки
        vol_percent = int(self.window.music_volume * 100)
        arcade.draw_text(f"Громкость музыки (+/-): {vol_percent}%",
                         cx, cy - 30, arcade.color.WHITE, 20, anchor_x="center")

        arcade.draw_text("Нажми ESC или M, чтобы вернуться", cx, 100,
                         arcade.color.LIGHT_GRAY, 14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)
            # Обновляем проекцию сразу после переключения
            self.window.ctx.projection_2d = 0, self.window.width, 0, self.window.height

        # Управление громкостью
        elif key == arcade.key.EQUAL:  # Клавиша '+' (обычно EQUAL без Shift)
            self.window.music_volume = min(1.0, self.window.music_volume + 0.1)
            self.update_music_volume()

        elif key == arcade.key.MINUS:  # Клавиша '-'
            self.window.music_volume = max(0.0, self.window.music_volume - 0.1)
            self.update_music_volume()

        # Возврат в предыдущее меню (MenuView)
        elif key == arcade.key.ESCAPE or key == arcade.key.M:
            self.window.show_view(self.prev_view)

    def update_music_volume(self):
        """Применяет громкость к активному плееру сразу"""
        if hasattr(self.window, "bg_music_player") and self.window.bg_music_player:
            self.window.bg_music_player.volume = self.window.music_volume