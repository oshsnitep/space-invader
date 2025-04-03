import pygame
import random
import math
from settings import SCREEN_WIDTH

class Vegetable:
    def __init__(self, enemy_type=None):
        # enemy_type が指定されなければ、ランダムに種類を選ぶ
        enemy_types = [
            {"type": "大根", "color": (255, 255, 255), "speed": 2, "category": "vegetable"},
            {"type": "にんじん", "color": (255, 165, 0), "speed": 3, "category": "vegetable"},
            {"type": "キャベツ", "color": (34, 139, 34), "speed": 1, "category": "vegetable"},
            {"type": "トマト", "color": (255, 99, 71), "speed": 2, "category": "fruit"},
            {"type": "スイカ", "color": (0, 128, 0), "speed": 1, "category": "fruit"},
            {"type": "メロン", "color": (144, 238, 144), "speed": 1, "category": "fruit"},
            {"type": "いちご", "color": (255, 105, 180), "speed": 3, "category": "fruit"}
        ]
        self.type_data = enemy_type if enemy_type else random.choice(enemy_types)
        self.type = self.type_data["type"]
        self.category = self.type_data["category"]
        self.speed = self.type_data["speed"]
        self.image = pygame.Surface((50, 50))
        self.image.fill(self.type_data["color"])
        x_pos = random.randint(50, SCREEN_WIDTH - 50)
        self.rect = self.image.get_rect(midtop=(x_pos, 0))
        # 野菜（vegetable）の場合、動作の特徴を追加
        if self.category == "vegetable":
            if self.type == "大根":
                self.drift = random.uniform(-1.5, 1.5)
            elif self.type == "にんじん":
                self.direction = 1
                self.amplitude = random.randint(1, 3)
                self.inertia = 0
            elif self.type == "キャベツ":
                self.wobble_phase = random.uniform(0, 2 * math.pi)
        # 果物はタネ撒き用のタイマーを初期化
        elif self.category == "fruit":
            self.seed_timer = 0
            self.seed_delay = 60  # 60 フレーム
    def update(self):
        current_time = pygame.time.get_ticks() / 1000  # 秒単位
        if self.category == "vegetable":
            if self.type == "大根":
                self.rect.y += self.speed
                self.rect.x += self.drift
            elif self.type == "にんじん":
                self.inertia += 0.05
                self.rect.y += self.speed + self.inertia
                self.rect.x += self.speed * self.direction * self.amplitude
                if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                    self.direction *= -1
            elif self.type == "キャベツ":
                self.rect.y += self.speed
                offset = 5 * math.sin(current_time + self.wobble_phase)
                self.rect.x += int(offset)
        elif self.category == "fruit":
            self.rect.y += self.speed
            self.seed_timer += 1

    def is_off_screen(self, screen_height):
        return self.rect.top >= screen_height