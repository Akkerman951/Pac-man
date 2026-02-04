import random
import arcade
from arcade import check_for_collision_with_list

# ------------------ CONSTANTS ------------------
def load_config(filename):
    config = {}
    with open(filename, "r") as file:
        for line in file:
            key, value = line.strip().split("=")

            if value.isdigit():
                config[key] = int(value)
            else:
                config[key] = value

    return config



config = load_config("config.txt")

WINDOW_WIDTH = config["WINDOW_WIDTH"]
WINDOW_HEIGHT = config["WINDOW_HEIGHT"]
TILE_SIZE = config["TILE_SIZE"]
WINDOW_TITLE = config["WINDOW_TITLE"]


def load_level_map(filename):
    level_map = []
    with open(filename, "r") as file:
        for line in file:
            level_map.append(line.strip())
    return level_map


LEVEL_MAP = load_level_map("level1.txt")


# ------------------ SPRITES ------------------
class Pacman(arcade.Sprite):
    def __init__(self):
        texture = arcade.make_circle_texture(TILE_SIZE, arcade.color.YELLOW)
        super().__init__(texture)
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.change_x = 0
        self.change_y = 0
        self.score = 0
        self.speed = 3

    def move(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

    def update(self, *args):
        self.move()

    def stop(self):
        self.change_x = 0
        self.change_y = 0

class Teleport(arcade.Sprite):
    def __init__(self):
        texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.RED, 255, 255)
        super().__init__(texture)
        self.width = TILE_SIZE
        self.height = TILE_SIZE

class Ghost(arcade.Sprite):
    def __init__(self):
        texture = arcade.make_circle_texture(TILE_SIZE, arcade.color.RED)
        super().__init__(texture)
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.change_x = random.choice([-1, 1]) * 4
        self.change_y = 0

    def update(self, delta_time: float = 1 / 60, *args, **kwargs):
        self.move()

    def move(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

class Coin(arcade.Sprite):
    def __init__(self):
        texture = arcade.make_circle_texture(16, arcade.color.YELLOW)
        super().__init__(texture)
        self.value = 300

class Wall(arcade.Sprite):
    def __init__(self):
        texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.BLUE, 255, 255)
        super().__init__(texture)
        self.width = TILE_SIZE
        self.height = TILE_SIZE

# ------------------ GAME ------------------
class PacmanGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.ghost_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.teleport_list = arcade.SpriteList()

        self.player = None
        self.game_over = False
        self.win = False

        self.start_x = 0
        self.start_y = 0

        self.score = 0
        self.lives = 3
        self.max_score = 0

    def setup(self):
        self.wall_list = arcade.SpriteList()
        self.ghost_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.teleport_list = arcade.SpriteList()

        self.game_over = False
        self.win = False
        self.window.background_color = arcade.color.BLACK

        rows = len(LEVEL_MAP)

        for row_idx, row in enumerate(LEVEL_MAP):
            for col_idx, cell in enumerate(row):
                x = col_idx * TILE_SIZE + TILE_SIZE / 2
                y = (rows - row_idx - 1) * TILE_SIZE + TILE_SIZE / 2

                if cell == "W":
                    wall = Wall()
                    wall.center_x = x
                    wall.center_y = y
                    self.wall_list.append(wall)

                elif cell == ".":
                    coin = Coin()
                    coin.center_x = x
                    coin.center_y = y
                    self.coin_list.append(coin)

                elif cell == "G":
                    ghost = Ghost()
                    ghost.center_x = x
                    ghost.center_y = y
                    self.ghost_list.append(ghost)
                    apple = Apple()
                    apple.center_x = x
                    apple.center_y = y
                    self.apple_list.append(apple)

                elif cell == "T":
                    teleport = Teleport()
                    teleport.center_x = x
                    teleport.center_y = y
                    self.teleport_list.append(teleport)

                elif cell == "P":
                    self.player = Pacman()
                    self.player.center_x = x
                    self.player.center_y = y
                    self.start_x = x
                    self.start_y = y
                    self.player_list.append(self.player)

                elif cell == "A":
                    apple = Apple()
                    apple.center_x = x
                    apple.center_y = y
                    self.apple_list.append(apple)

        self.max_score = len(self.coin_list) * 300

    def on_draw(self):
        self.clear()
        self.wall_list.draw()
        self.coin_list.draw()
        self.ghost_list.draw()
        self.player_list.draw()
        self.teleport_list.draw()

        arcade.draw_text(f"Score: {self.player.score}", 10, WINDOW_HEIGHT - 30, arcade.color.WHITE, 16)
        arcade.draw_text(f"Lives: {self.lives}", 10, WINDOW_HEIGHT - 55, arcade.color.WHITE, 16)

        if self.game_over:
            arcade.draw_text("GAME OVER", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2, arcade.color.RED, 32)
        elif self.win:
            arcade.draw_text("YOU WIN!", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2, arcade.color.PINK, 32)

    def on_key_press(self, key: int, modifiers):
        if key == arcade.key.UP:
            self.player.change_x = 0
            self.player.change_y = self.player.speed
        elif key == arcade.key.DOWN:
            self.player.change_x = 0
            self.player.change_y = -self.player.speed
        elif key == arcade.key.RIGHT:
            self.player.change_x = self.player.speed
            self.player.change_y = 0
        elif key == arcade.key.LEFT:
            self.player.change_x = -self.player.speed
            self.player.change_y = 0

    def on_update(self, delta_time):
        if self.game_over or self.win:
            return


        ghosts_hit = check_for_collision_with_list(self.player, self.ghost_list)
        if ghosts_hit:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:

                self.player.center_x = self.start_x
                self.player.center_y = self.start_y
                self.player.change_x = 0
                self.player.change_y = 0


        self.player.move()
        mat_x = self.player.center_x // TILE_SIZE
        mat_y = self.player.center_y // TILE_SIZE
        if arcade.check_for_collision_with_list(self.player, self.wall_list):
            self.player.center_x = mat_x * TILE_SIZE + 16
            self.player.center_y = mat_y * TILE_SIZE + 16


        for ghost in self.ghost_list:
            matr_x = ghost.center_x // TILE_SIZE
            matr_y = ghost.center_y // TILE_SIZE
            ghost.update()
            if arcade.check_for_collision_with_list(ghost, self.wall_list):
                ghost.change_x, ghost.change_y = random.choice(
                    [(2,0),(-2,0),(0,2),(0,-2)]
                )
                ghost.center_x = matr_x * TILE_SIZE + 16
                ghost.center_y = matr_y * TILE_SIZE + 16


        coins_hit = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coins_hit:
            self.player.score += coin.value
            coin.remove_from_sprite_lists()
        tp_hits = arcade.check_for_collision_with_list(self.player, self.teleport_list)
        if tp_hits:
            for tp in self.teleport_list:
                if tp not in tp_hits:
                    self.player.center_x = tp.center_x
                    self.player.center_y = tp.center_y
                break
        apples_hit = arcade.check_for_collision_with_list(self.player, self.apple_list)

        for apple in apples_hit:
            self.player.score += apple.value
            apple.remove_from_sprite_lists()

        if self.player.score >= self.max_score:
            self.win = True


# ------------------ MAIN ------------------
def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = PacmanGame()
    game.setup()
    window.show_view(game)
    arcade.run()

if __name__ == "__main__":
    main()
