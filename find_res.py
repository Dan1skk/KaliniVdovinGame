import arcade.resources
import os

# Пробуем найти корень картинок
try:
    path = arcade.resources.resolve(":resources:images")
    print(f"--- РЕСУРСЫ НАЙДЕНЫ ТУТ: {path} ---")

    # Давай посмотрим, какие папки есть внутри
    if os.path.exists(path):
        subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        print(f"Папки в images: {subdirs}")

        anim_path = os.path.join(path, "animated_characters")
        if os.path.exists(anim_path):
            characters = os.listdir(anim_path)
            print(f"Доступные персонажи: {characters}")
        else:
            print("Папка animated_characters ОТСУТСТВУЕТ!")
except Exception as e:
    print(f"Ошибка при поиске: {e}")