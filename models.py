import csv
import os

class ScoreManager:
    def __init__(self, file_path="results.csv"):
        self.file_path = file_path
        # если файла нет - создаем заголовки
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["player", "score", "level"])

    def add_score(self, name, score, level):
        # дописываем строчку в конец
        with open(self.file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([name, score, level])