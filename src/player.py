import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Player:
    def __init__(self):
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.speed = 5

    def handle_movement(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_DOWN]:
            dy += self.speed
        # 両方向入力の場合は 1/√2 倍に調整
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        self.rect.x += dx
        self.rect.y += dy
        # 画面外に出ないよう制限
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT