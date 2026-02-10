import random
import arcade
from arcade import check_for_collision_with_list, load_sound, load_texture

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

COIN_SOUND = load_sound(config["coin_sound1"])
APPLE_SOUND = load_sound(config["apple_sound1"])
PORTAL_SOUND = load_sound(config["portal_sound1"])
GHOST_SOUND = load_sound(config["ghost_sound1"])
WIN_SOUND = load_sound(config["win_sound1"])
EAT_GHOST_SOUND = load_sound(config["eat_ghost_sound1"])
PILL_SOUND = load_sound(config["pill_sound1"])

RED_GHOST_PNG_R = load_texture(config["red_ghost_png1.r"])
PORTAL_PNG1 = load_texture(config["portal_png1"])
APPLE_PNG = load_texture(config["apple_png1"])
PILL_PNG =  load_texture(config["pill_blue_png1"])
SPLASH_PNG = load_texture("texture/starting_screen1.jpg.jpeg")

def load_level_map(filename):
    level_map = []
    with open(filename, "r") as file:
        for line in file:
            level_map.append(line.strip())
    return level_map

LEVEL_MAP = load_level_map("level1.txt")

# ------------------ START SCREEN ------------------
class SplashScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.timer = 0
        self.alpha = -100
        self.fade_speed = 0.5
        self.max_time = 12 * 60

        self.background_sprite = arcade.Sprite()
        self.background_sprite.texture = SPLASH_PNG
        self.background_sprite.center_x = WINDOW_WIDTH / 2
        self.background_sprite.center_y = WINDOW_HEIGHT / 2
        self.background_sprite.width = WINDOW_WIDTH
        self.background_sprite.height = WINDOW_HEIGHT

        self.background_list = arcade.SpriteList()
        self.background_list.append(self.background_sprite)

    def on_draw(self):
        self.clear()
        self.background_list.draw()

    def on_update(self, delta_time):
        self.timer += 1
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed)
            self.background_sprite.alpha = self.alpha
        if self.timer >= self.max_time:
            self.start_game()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.start_game()

    def start_game(self):
        game = PacmanGame()
        game.setup()
        self.window.show_view(game)

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
        self.speed_basic = 2.4
        self.speed_grader = 1
        self.speed = self.speed_basic
        self.teleport_cooldown = 0

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
        texture = PORTAL_PNG1
        super().__init__(texture)
        self.width = TILE_SIZE
        self.height = TILE_SIZE

class Ghost(arcade.Sprite):
    def __init__(self):
        texture = RED_GHOST_PNG_R
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
        self.normal_texture = arcade.make_circle_texture(16, arcade.color.YELLOW)
        self.power_texture = arcade.make_circle_texture(16, arcade.color.PINK)
        super().__init__(self.normal_texture)
        self.value = 300

    def set_power(self, power: bool):
        self.texture = self.power_texture if power else self.normal_texture

class WhiteCoin(arcade.Sprite):
    def __init__(self):
        texture = arcade.make_circle_texture(16, arcade.color.WHITE)
        super().__init__(texture)
        self.timer = 0
        self.duration = 10 * 60

class Wall(arcade.Sprite):
    def __init__(self):
        texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.BLUE, 255, 255)
        super().__init__(texture)
        self.width = TILE_SIZE
        self.height = TILE_SIZE

class Apple(arcade.Sprite):
    def __init__(self):
        texture = APPLE_PNG
        super().__init__(texture)
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.value = 500

class Pill(arcade.Sprite):
    def __init__(self):
        texture = PILL_PNG
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
        self.pill_list = arcade.SpriteList()
        self.apple_list = arcade.SpriteList()
        self.white_coin_list = arcade.SpriteList()

        self.player = None
        self.game_over = False
        self.win = False
        self.power_mode = False
        self.power_timer = 0
        self.speed_up = False
        self.speed_up_timer = 0
        self.white_coin_timer = 5 * 60
        self.counter = 0
        self.exit = False
        self.paused_velocity = (0, 0)

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
        self.pill_list = arcade.SpriteList()
        self.apple_list = arcade.SpriteList()
        self.white_coin_list = arcade.SpriteList()

        self.game_over = False
        self.win = False
        self.window.background_color = arcade.color.BLACK
        self.power_mode = False
        self.power_timer = 0
        self.speed_up = False
        self.speed_up_timer = 0
        self.white_coin_timer = 5 * 60

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
                    for i in range(4):
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
                elif cell == "D":
                    pill = Pill()
                    pill.center_x = x
                    pill.center_y = y
                    self.pill_list.append(pill)

        self.max_score = len(self.coin_list) * 300 + len(self.apple_list) * 500 + 4 * 1000

    def spawn_white_coin(self):
        if len(self.white_coin_list) > 0:
            return

        free_positions = []
        rows = len(LEVEL_MAP)
        cols = len(LEVEL_MAP[0])
        for row_idx,row in enumerate(LEVEL_MAP):
            for col_idx,cell in enumerate(row):
                if cell == "." or cell == "A":
                    x = col_idx * TILE_SIZE + TILE_SIZE / 2
                    y = (rows - row_idx - 1) * TILE_SIZE + TILE_SIZE / 2
                    collides = any(sprite.center_x == x and sprite.center_y == y
                                   for sprite_list in (self.coin_list,self.apple_list,self.white_coin_list)
                                   for sprite in sprite_list)
                    if not collides:
                        free_positions.append((x,y))
        if free_positions:
            x,y = random.choice(free_positions)
            coin = WhiteCoin()
            coin.center_x = x
            coin.center_y = y
            self.white_coin_list.append(coin)

    def on_draw(self):
        self.clear()
        self.wall_list.draw()
        self.white_coin_list.draw()
        self.coin_list.draw()
        self.apple_list.draw()
        self.teleport_list.draw()
        self.ghost_list.draw()
        self.player_list.draw()
        self.pill_list.draw()

        arcade.draw_text(f"Score: {self.player.score}", 10, WINDOW_HEIGHT - 45, arcade.color.WHITE, 16)
        arcade.draw_text(f"Lives: {self.lives}", 10, WINDOW_HEIGHT - 65, arcade.color.WHITE, 16)
        arcade.draw_text(f"Time: {round(self.counter)} s", 10, WINDOW_HEIGHT - 25 , arcade.color.WHITE, 16)

        if self.game_over:
            arcade.draw_text("GAME OVER!", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2, arcade.color.RED, 32)
            arcade.draw_text(f"TIME YOU SPENT: {round(self.counter)} s",WINDOW_WIDTH / 2 - 150,WINDOW_HEIGHT / 2 - 40, arcade.color.PINK,32)
        elif self.win:
            arcade.draw_text("YOU WIN!", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2, arcade.color.PINK, 32)
            arcade.draw_text(f"TIME YOU SPENT: {round(self.counter)} s", WINDOW_WIDTH / 2 - 150, WINDOW_HEIGHT / 2 - 40, arcade.color.PINK, 32)
            arcade.draw_text(f"LIFES YOU SPENT: {abs(self.lives - 3)}", WINDOW_WIDTH / 2 - 150, WINDOW_HEIGHT / 2 - 80, arcade.color.PINK, 32)
        elif self.exit:
            arcade.draw_text("Are you sure you want to quit?",WINDOW_WIDTH / 2 - 250,WINDOW_HEIGHT / 2 - 10, arcade.color.PINK, 32)
            arcade.draw_text("To continue press SPACE",WINDOW_WIDTH / 2 - 180,WINDOW_HEIGHT / 2 - 50,arcade.color.GREEN,32)
            arcade.draw_text("To quit press ESC",WINDOW_WIDTH / 2 - 120,WINDOW_HEIGHT / 2 - 90, arcade.color.RED, 32)

    def on_key_press(self, key: int, modifiers):
        if self.exit:
            if key == arcade.key.ESCAPE:
                self.window.close()
            elif key == arcade.key.SPACE:
                self.exit = False
                if self.player:
                    self.player.change_x, self.player.change_y = self.paused_velocity
            return
        if key in (arcade.key.UP, arcade.key.W):
            self.player.change_x = 0
            self.player.change_y = self.player.speed
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.player.change_x = 0
            self.player.change_y = -self.player.speed
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.player.change_x = self.player.speed
            self.player.change_y = 0
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.player.change_x = -self.player.speed
            self.player.change_y = 0
        elif key == arcade.key.ESCAPE:
            self.exit = True
            if self.player:
                self.paused_velocity = (self.player.change_x, self.player.change_y)
                self.player.stop()

    def on_update(self, delta_time):
        if self.game_over or self.win:
            return
        if self.exit:
            return
        if self.player and self.player.teleport_cooldown > 0:
            self.player.teleport_cooldown -= 1
        self.counter += 1 / 60
        self.player.move()

        # ------------------ Pill ------------------
        pill_hit = arcade.check_for_collision_with_list(self.player, self.pill_list)
        if pill_hit:
            self.speed_up_timer = 5 * 60
            self.speed_up = True
            self.player.speed = self.player.speed_basic + self.player.speed_grader
            for pill in pill_hit:
                pill.remove_from_sprite_lists()
                arcade.play_sound(PILL_SOUND)

        if self.speed_up:
            self.speed_up_timer -= 1
            if self.speed_up_timer <= 0:
                self.speed_up = False
                self.player.speed = self.player.speed_basic

        # ------------------ Ghost collision ------------------
        ghosts_hit = arcade.check_for_collision_with_list(self.player, self.ghost_list)
        if ghosts_hit:
            if self.power_mode:
                for ghost in ghosts_hit:
                    ghost.remove_from_sprite_lists()
                    arcade.play_sound(EAT_GHOST_SOUND, 10)
                    self.player.score += 1000
            else:
                self.lives -= 1
                arcade.play_sound(GHOST_SOUND, 20)
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.player.center_x = self.start_x
                    self.player.center_y = self.start_y
                    self.player.change_x = 0
                    self.player.change_y = 0

        # ------------------ Move ghosts ------------------
        for ghost in self.ghost_list:
            matr_x = ghost.center_x // TILE_SIZE
            matr_y = ghost.center_y // TILE_SIZE
            ghost.update()
            if arcade.check_for_collision_with_list(ghost, self.wall_list):
                ghost.change_x, ghost.change_y = random.choice([(2,0),(-2,0),(0,2),(0,-2)])
                ghost.center_x = matr_x * TILE_SIZE + 16
                ghost.center_y = matr_y * TILE_SIZE + 16

        # ------------------ Coins ------------------
        coins_hit = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coins_hit:
            self.player.score += coin.value
            coin.remove_from_sprite_lists()
            arcade.play_sound(COIN_SOUND)

        blink_power = False
        if self.power_mode and self.power_timer <= 2 * 60:
            blink_power = (self.power_timer // 12) % 2 == 0

        for coin in self.coin_list:
            if self.power_mode and self.power_timer <= 2 * 60:
                coin.set_power(blink_power)
                #put here sound of 2 last sec of power mode!!!
            else:
                coin.set_power(self.power_mode)

        # ------------------ White Coin ------------------
        self.white_coin_timer -= 1
        if self.white_coin_timer <= 0:
            self.spawn_white_coin()
            self.white_coin_timer = 5 * 60

        for coin in self.white_coin_list:
            coin.timer += 1
            if coin.timer >= coin.duration:
                coin.remove_from_sprite_lists()

        white_hits = arcade.check_for_collision_with_list(self.player,self.white_coin_list)
        for coin in white_hits:
            coin.remove_from_sprite_lists()
            self.white_coin_speed_timer = 5 * 60
            for ghost in self.ghost_list:

                ghost.change_x *= 2
                ghost.change_y *= 2

        if hasattr(self,"white_coin_speed_timer"):
            self.white_coin_speed_timer -= 1
            if self.white_coin_speed_timer <= 0:
                for ghost in self.ghost_list:

                    ghost.change_x = (ghost.change_x // abs(ghost.change_x) if ghost.change_x != 0 else 0) * 4
                    ghost.change_y = (ghost.change_y // abs(ghost.change_y) if ghost.change_y != 0 else 0) * 4
                del self.white_coin_speed_timer

        # ------------------ Power mode ------------------
        apples_hit = arcade.check_for_collision_with_list(self.player, self.apple_list)
        if apples_hit:
            self.power_mode = True
            self.power_timer = 10 * 60
            arcade.play_sound(APPLE_SOUND, 10)

        if self.power_mode:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_mode = False

        for apple in apples_hit:
            self.player.score += apple.value
            apple.remove_from_sprite_lists()

        # ------------------ Teleports ------------------
        tp_hits = arcade.check_for_collision_with_list(self.player, self.teleport_list)
        if tp_hits and self.player.teleport_cooldown == 0:
            current_portal = tp_hits[0]
            other_portals = [p for p in self.teleport_list if p is not current_portal]
            if other_portals:
                dest = random.choice(other_portals)
                self.player.center_x = dest.center_x
                self.player.center_y = dest.center_y
                arcade.play_sound(PORTAL_SOUND)
                self.player.teleport_cooldown = 5 * 60

        # ------------------ Walls ------------------
        mat_x = self.player.center_x // TILE_SIZE
        mat_y = self.player.center_y // TILE_SIZE
        if arcade.check_for_collision_with_list(self.player, self.wall_list):
            self.player.center_x = mat_x * TILE_SIZE + 16
            self.player.center_y = mat_y * TILE_SIZE + 16

        if self.player.score >= self.max_score:
            arcade.play_sound(WIN_SOUND, 20)
            self.win = True

        if self.game_over:
            #put sound of lose here!!!
            pass

# ------------------ MAIN ------------------
def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.show_view(SplashScreen())
    #put sound of starting screen here!!!
    arcade.run()

if __name__ == "__main__":
    main()
