import pygame
import sys
import random
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from player import Player
from vegetable import Vegetable

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.high_score = 0  # ハイスコアの記録
        self.restart_game()

    def restart_game(self):
        self.score = 0
        self.lives = 3
        self.next_life_score = 1000
        self.game_over = False
        self.game_over_start_time = None
        self.player = Player()
        self.enemies = []
        self.knives = []
        self.seeds = []
        self.enemy_spawn_timer = 0
        self.popups = []
        self.last_enemy_killed = None
        self.multiplier = 1

    def spawn_enemy(self):
        # Vegetable インスタンスを生成
        return Vegetable()

    def spawn_seed(self, enemy):
        seed_surface = pygame.Surface((5, 5))
        seed_surface.fill((139, 69, 19))
        seed_rect = seed_surface.get_rect(midtop=enemy.rect.midbottom)
        return {"image": seed_surface, "rect": seed_rect, "speed": 4}

    def spawn_seeds(self, enemy):
        seeds = []
        enemy_center = enemy.rect.center
        player_center = self.player.rect.center
        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        nx = dx / dist
        ny = dy / dist
        base_speed = 4
        def create_seed(offset_angle=0, speed_multiplier=1.0):
            angle = math.atan2(ny, nx) + offset_angle
            vx = math.cos(angle) * base_speed * speed_multiplier
            vy = math.sin(angle) * base_speed * speed_multiplier
            seed_surface = pygame.Surface((5, 5))
            seed_surface.fill((139, 69, 19))
            seed_rect = seed_surface.get_rect(center=enemy.rect.center)
            return {"image": seed_surface, "rect": seed_rect, "velocity": (vx, vy)}
        if enemy.type == "トマト":
            seeds.append(create_seed())
        elif enemy.type == "スイカ":
            seeds.append(create_seed(0))
            seeds.append(create_seed(math.radians(15)))
            seeds.append(create_seed(math.radians(-15)))
        elif enemy.type == "メロン":
            seeds.append(create_seed(math.radians(10)))
            seeds.append(create_seed(math.radians(-10)))
        elif enemy.type == "いちご":
            seeds.append(create_seed(0, speed_multiplier=1.5))
        return seeds

    def throw_knife(self):
        knife_surface = pygame.Surface((10, 30))
        knife_surface.fill((192, 192, 192))
        knife_rect = knife_surface.get_rect(midbottom=self.player.rect.midtop)
        self.knives.append({"image": knife_surface, "rect": knife_rect, "speed": 7})

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            if self.score > self.high_score:
                self.high_score = self.score
            self.game_over = True
            self.game_over_start_time = pygame.time.get_ticks()
        else:
            self.player.rect.centerx = SCREEN_WIDTH // 2
            self.player.rect.bottom = SCREEN_HEIGHT - 50
            self.last_enemy_killed = None
            self.multiplier = 1

    def update_popups(self):
        for popup in self.popups[:]:
            popup["pos"][1] -= 1
            popup["timer"] -= 1
            if popup["timer"] <= 0:
                self.popups.remove(popup)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # ゲームオーバー時、E キーで終了
            if self.game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    pygame.quit()
                    sys.exit()
            if not self.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.throw_knife()
        keys = pygame.key.get_pressed()
        if self.game_over:
            if pygame.time.get_ticks() - self.game_over_start_time >= 5000:
                if keys[pygame.K_SPACE]:
                    self.restart_game()
            return
        self.player.handle_movement(keys)

    def update(self):
        if self.game_over:
            self.update_enemies()
            self.update_seeds()
            self.update_popups()
            return
        for knife in self.knives:
            knife["rect"].y -= knife["speed"]
        self.knives = [k for k in self.knives if k["rect"].bottom > 0]
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer > FPS:
            self.enemies.append(self.spawn_enemy())
            self.enemy_spawn_timer = 0
        self.update_enemies()
        self.update_seeds()
        self.check_collisions()
        self.update_popups()
        if self.score >= self.next_life_score:
            self.lives += 1
            self.next_life_score += 1000

    def update_enemies(self):
        for enemy in self.enemies:
            enemy.update()
            if enemy.category == "fruit":
                if enemy.seed_timer >= enemy.seed_delay:
                    seeds = self.spawn_seeds(enemy)
                    self.seeds.extend(seeds)
                    enemy.seed_timer = 0
        self.enemies = [e for e in self.enemies if not e.is_off_screen(SCREEN_HEIGHT)]

    def update_seeds(self):
        for seed in self.seeds:
            if "velocity" in seed:
                vx, vy = seed["velocity"]
                seed["rect"].x += vx
                seed["rect"].y += vy
            else:
                seed["rect"].y += seed["speed"]
        self.seeds = [s for s in self.seeds if s["rect"].top < SCREEN_HEIGHT]

    def check_collisions(self):
        points_by_type = {
            "大根": 50,
            "にんじん": 100,
            "キャベツ": 50,
            "トマト": 100,
            "スイカ": 50,
            "メロン": 50,
            "いちご": 150
        }
        for knife in self.knives[:]:
            for enemy in self.enemies[:]:
                if knife["rect"].colliderect(enemy.rect):
                    if self.last_enemy_killed == enemy.type:
                        self.multiplier += 1
                    else:
                        self.last_enemy_killed = enemy.type
                        self.multiplier = 1
                    points = points_by_type.get(enemy.type, 50)
                    awarded = points * self.multiplier
                    self.score += awarded
                    popup_text = f"+{awarded}"
                    if self.multiplier > 1:
                        popup_text += f" x{self.multiplier}"
                    self.popups.append({
                        "text": popup_text,
                        "pos": [enemy.rect.centerx, enemy.rect.centery],
                        "timer": 60
                    })
                    self.knives.remove(knife)
                    self.enemies.remove(enemy)
                    break
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.lose_life()
                break
        for seed in self.seeds:
            if self.player.rect.colliderect(seed["rect"]):
                self.lose_life()
                break

    def draw(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 36)
        score_surf = font.render(f"Score: {self.score}", True, (255, 255, 255))
        high_score_surf = font.render(f"High Score: {self.high_score}", True, (255, 255, 255))
        lives_surf = font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(high_score_surf, (10, 50))
        self.screen.blit(lives_surf, (10, 90))
        if self.game_over:
            game_over_font = pygame.font.SysFont(None, 72)
            msg = game_over_font.render("GAME OVER", True, (255, 0, 0))
            msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(msg, msg_rect)
            if pygame.time.get_ticks() - self.game_over_start_time >= 5000:
                restart_msg = font.render("Press SPACE to restart / Press E to exit", True, (255, 255, 255))
                restart_rect = restart_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
                self.screen.blit(restart_msg, restart_rect)
        else:
            self.screen.blit(self.player.image, self.player.rect)
            for knife in self.knives:
                self.screen.blit(knife["image"], knife["rect"])
        for enemy in self.enemies:
            self.screen.blit(enemy.image, enemy.rect)
        for seed in self.seeds:
            self.screen.blit(seed["image"], seed["rect"])
        for popup in self.popups:
            popup_surf = font.render(popup["text"], True, (255, 255, 0))
            popup_rect = popup_surf.get_rect(center=popup["pos"])
            self.screen.blit(popup_surf, popup_rect)