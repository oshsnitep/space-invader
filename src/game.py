import pygame
import sys
import random
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from player import Player
from vegetable import Vegetable

class Game:
    """ゲームのメインロジックを管理するクラス"""
    def __init__(self, screen):
        """初期化処理。画面初期化やゲームリセットを実施する"""
        self.screen = screen
        self.high_score = 0  # ハイスコアの記録
        self.restart_game()

    def restart_game(self):
        """ゲームの状態を初期化する"""
        self.score = 0
        self.lives = 3
        self.next_life_score = 1000
        self.game_over = False
        self.game_over_start_time = None
        self.player = Player()
        # 新規追加: プレイヤーのサイズを2/3に縮小
        orig_size = self.player.image.get_size()
        new_size = (int(orig_size[0] * 2/3), int(orig_size[1] * 2/3))
        self.player.image = pygame.transform.scale(self.player.image, new_size)
        # ゲーム内オブジェクトのリセット
        self.enemies = []
        self.knives = []
        self.seeds = []
        self.enemy_spawn_timer = 0
        self.popups = []
        self.last_enemy_killed = None
        self.multiplier = 1
        # 新規追加: リスポーン状態の初期化
        self.respawning = False
        self.respawn_start_time = None
        # 新規追加: プレイヤー爆発状態フラグ
        self.player_exploded = False

    def spawn_enemy(self):
        """Vegetable のインスタンスを生成する"""
        # 敵オブジェクト生成処理（必要に応じて拡張可）
        return Vegetable()

    def spawn_seed(self, enemy):
        """単一のシードを生成する"""
        # シードの外観、初期位置設定
        seed_surface = pygame.Surface((5, 5))
        seed_surface.fill((139, 69, 19))
        seed_rect = seed_surface.get_rect(midtop=enemy.rect.midbottom)
        return {"image": seed_surface, "rect": seed_rect, "speed": 4}

    def spawn_seeds(self, enemy):
        """敵の種類に応じて複数のシードを生成する"""
        seeds = []
        # プレイヤーとの相対位置計算
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
            """内部関数: シードを生成する"""
            angle = math.atan2(ny, nx) + offset_angle
            vx = math.cos(angle) * base_speed * speed_multiplier
            vy = math.sin(angle) * base_speed * speed_multiplier
            seed_surface = pygame.Surface((5, 5))
            seed_surface.fill((139, 69, 19))
            seed_rect = seed_surface.get_rect(center=enemy.rect.center)
            return {"image": seed_surface, "rect": seed_rect, "velocity": (vx, vy)}

        # 敵の種類に合わせたシードの生成
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
        """プレイヤーがナイフを投げる処理"""
        knife_surface = pygame.Surface((10, 30))
        knife_surface.fill((192, 192, 192))
        knife_rect = knife_surface.get_rect(midbottom=self.player.rect.midtop)
        self.knives.append({"image": knife_surface, "rect": knife_rect, "speed": 7})

    def lose_life(self):
        """プレイヤーのライフ減少およびゲームオーバー処理"""
        self.lives -= 1
        if self.lives <= 0:
            # ライフが尽きた場合、ハイスコア更新とゲームオーバーフラグの設定
            if self.score > self.high_score:
                self.high_score = self.score
            self.game_over = True
            self.game_over_start_time = pygame.time.get_ticks()
        else:
            # 新規変更: プレイヤー爆発→非表示にし、respawning 状態へ移行
            self.respawning = True
            self.respawn_start_time = pygame.time.get_ticks()
            self.player_exploded = True
            self.last_enemy_killed = None
            self.multiplier = 1
            # オプション: 投げたナイフをクリア
            self.knives = []

    def update_popups(self):
        """ポップアップメッセージの位置とタイマーを更新する"""
        for popup in self.popups[:]:
            popup["pos"][1] -= 1  # ポップアップを上方向に移動
            popup["timer"] -= 1  # 表示時間の減少
            if popup["timer"] <= 0:
                self.popups.remove(popup)

    def handle_events(self):
        """ユーザーのイベントを処理する"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # ゲームオーバー時、Eキーで終了
            if self.game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    pygame.quit()
                    sys.exit()
            if self.respawning:
                continue
            if not self.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.throw_knife()
        keys = pygame.key.get_pressed()
        if self.game_over:
            # ゲームオーバー後、一定時間経過で再スタート可能
            if pygame.time.get_ticks() - self.game_over_start_time >= 5000:
                if keys[pygame.K_SPACE]:
                    self.restart_game()
            return
        if not self.respawning:
            # 通常時、プレイヤーの移動処理
            self.player.handle_movement(keys)

    def update(self):
        """ゲーム内オブジェクトと状態の更新"""
        if self.game_over:
            self.update_enemies()
            self.update_seeds()
            self.update_popups()
            return
        # 新規変更: リスポーン中は敵を下方向へ移動させ5秒後にプレイヤー位置をリセット
        if self.respawning:
            for enemy in self.enemies:
                enemy.rect.y += 5  # 少しずつ下に移動
            if pygame.time.get_ticks() - self.respawn_start_time >= 5000:
                self.respawning = False
                self.player_exploded = False
                self.enemies = [e for e in self.enemies if e.is_off_screen(SCREEN_HEIGHT)]
                self.player.rect.centerx = SCREEN_WIDTH // 2
                self.player.rect.bottom = SCREEN_HEIGHT - 50
            self.update_enemies()
            self.update_seeds()
            self.update_popups()
            return
        # ナイフの移動
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
        # 指定スコアに達すると残機を追加
        if self.score >= self.next_life_score:
            self.lives += 1
            self.next_life_score += 1000

    def update_enemies(self):
        """敵の更新とシード発生タイミングの管理"""
        for enemy in self.enemies:
            enemy.update()
            if enemy.category == "fruit":
                if enemy.seed_timer >= enemy.seed_delay:
                    seeds = self.spawn_seeds(enemy)
                    self.seeds.extend(seeds)
                    enemy.seed_timer = 0
        self.enemies = [e for e in self.enemies if not e.is_off_screen(SCREEN_HEIGHT)]

    def update_seeds(self):
        """シードの位置更新と画面外削除"""
        for seed in self.seeds:
            if "velocity" in seed:
                vx, vy = seed["velocity"]
                seed["rect"].x += vx
                seed["rect"].y += vy
            else:
                seed["rect"].y += seed["speed"]
        self.seeds = [s for s in self.seeds if s["rect"].top < SCREEN_HEIGHT]

    def check_collisions(self):
        """衝突判定を行い、スコア加算やライフ減少処理を行う"""
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
                    # 衝突時ポップアップ生成
                    self.popups.append({
                        "text": popup_text,
                        "pos": [enemy.rect.centerx, enemy.rect.centery],
                        "timer": 60
                    })
                    self.knives.remove(knife)
                    self.enemies.remove(enemy)
                    break
        # プレイヤーと敵、シードの衝突判定
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.lose_life()
                break
        for seed in self.seeds:
            if self.player.rect.colliderect(seed["rect"]):
                self.lose_life()
                break

    def draw(self):
        """画面への描画処理"""
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 36)
        score_surf = font.render(f"Score: {self.score}", True, (255, 255, 255))
        high_score_surf = font.render(f"High Score: {self.high_score}", True, (255, 255, 255))
        lives_surf = font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        # UI 表示
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
        elif self.respawning:
            # 新規変更: respawning 中はプレイヤー非表示＋カウントダウン表示
            current_time = pygame.time.get_ticks()
            remaining = max(0, 5 - int((current_time - self.respawn_start_time) / 1000))
            countdown_font = pygame.font.SysFont(None, 72)
            countdown_msg = countdown_font.render(str(remaining), True, (255, 255, 255))
            countdown_rect = countdown_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(countdown_msg, countdown_rect)
        else:
            # プレイヤーとナイフの描画
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