import csv
import os

class ScoreManager:
    def __init__(self):
        self.file_path = "scores.csv"
        # Создаем файл с заголовками, если его нет
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Score", "Level"])

    def add_score(self, name, score, level):
        """Метод, который требует views.py"""
        with open(self.file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([name, score, level])