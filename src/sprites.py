class Player:
    def __init__(self, x, y):
        self.image = "assets/images/player.png"
        self.x = x
        self.y = y
        self.width = 50  # プレイヤーの幅
        self.height = 50  # プレイヤーの高さ

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def draw(self, screen):
        # ここでプレイヤーの画像を描画する処理を追加
        pass


class Enemy:
    def __init__(self, x, y):
        self.image = "assets/images/enemy.png"
        self.x = x
        self.y = y
        self.width = 50  # 敵の幅
        self.height = 50  # 敵の高さ

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def draw(self, screen):
        # ここで敵の画像を描画する処理を追加
        pass