# Исправленный pacman (минимальные изменения, чтобы всё работало)
import random
import os
import json
import arcade
from arcade import check_for_collision_with_list, load_sound, load_texture, play_sound

# ------------------ HELPERS ------------------
def safe_load_sound(path):
    if not path:
        return None
    try:
        return load_sound(path)
    except Exception:
        return None

def safe_load_texture(path):
    if not path:
        return None
    try:
        return load_texture(path)
    except Exception:
        return None

def load_config(filename):
    config = {}
    if not os.path.isfile(filename):
        return config
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip() or line.strip().startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.strip().split("=", 1)
            key = key.strip()
            value = value.strip()
            if value.isdigit():
                config[key] = int(value)
            else:
                config[key] = value
    return config

def load_levels(folder="levels"):
    levels = []
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Folder '{folder}' not found.")
    files = sorted(f for f in os.listdir(folder) if f.endswith(".txt"))
    for fname in files:
        with open(os.path.join(folder, fname), "r", encoding="utf-8") as f:
            level = [line.rstrip("\n") for line in f if line.rstrip("\n") != ""]
            levels.append(level)
    return levels

def load_scores(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    scores = []
    for item in data:
        if isinstance(item, dict) and "name" in item and "time" in item:
            try:
                scores.append({"name": str(item["name"]), "time": float(item["time"])})
            except Exception:
                pass
    return scores

def save_scores(path, scores):
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(scores, file, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ------------------ CONFIG ------------------
config = load_config("config.txt")

WINDOW_WIDTH = int(config.get("WINDOW_WIDTH", 800))
WINDOW_HEIGHT = int(config.get("WINDOW_HEIGHT", 600))
TILE_SIZE = int(config.get("TILE_SIZE", 32))
WINDOW_TITLE = config.get("WINDOW_TITLE", "pacman")
SCORES_PATH = config.get("scores_path", "scores.json")

# safe loads
COIN_SOUND = safe_load_sound(config.get("coin_sound1", ""))
APPLE_SOUND = safe_load_sound(config.get("apple_sound1", ""))
PORTAL_SOUND = safe_load_sound(config.get("portal_sound1", ""))
GHOST_SOUND = safe_load_sound(config.get("ghost_sound1", ""))
WIN_SOUND = safe_load_sound(config.get("win_sound1", ""))
EAT_GHOST_SOUND = safe_load_sound(config.get("eat_ghost_sound1", ""))
PILL_SOUND = safe_load_sound(config.get("pill_sound1", ""))
DEAF_SOUND = safe_load_sound(config.get("def_sound1", ""))
LOGO_SOUND = safe_load_sound(config.get("logo_sound1", ""))
POWER_END_SOUND = safe_load_sound(config.get("power_end_sound1", ""))
PLAY_SOUND = safe_load_sound(config.get("play_sound1", ""))
PAUSE_SOUND = safe_load_sound(config.get("pause_sound1", ""))
DOR_SOUND = safe_load_sound(config.get("dor_sound1", ""))

# textures (safe)
RED_GHOST_PNG_R = safe_load_texture(config.get("red_ghost_png1.r", ""))
RED_GHOST_PNG_L = safe_load_texture(config.get("red_ghost_png1.l", ""))
RED_GHOST_PNG_U = safe_load_texture(config.get("red_ghost_png1.u", ""))
RED_GHOST_PNG_D = safe_load_texture(config.get("red_ghost_png1.d", ""))
RED_GHOST_PNG_R2 = safe_load_texture(config.get("red_ghost_png2.r", ""))
RED_GHOST_PNG_L2 = safe_load_texture(config.get("red_ghost_png2.l", ""))
RED_GHOST_PNG_U2 = safe_load_texture(config.get("red_ghost_png2.u", ""))
RED_GHOST_PNG_D2 = safe_load_texture(config.get("red_ghost_png2.d", ""))
BLUE_PNG = safe_load_texture(config.get("blue_ghost_png1", ""))
GREY_PNG = safe_load_texture(config.get("greu_ghost_png1", ""))

PORTAL_PNG1 = safe_load_texture(config.get("portal_png1", ""))
APPLE_PNG = safe_load_texture(config.get("apple_png1", ""))
PILL_PNG = safe_load_texture(config.get("pill_blue_png1", ""))
SPLASH_PNG = safe_load_texture("texture/starting_screen1.jpg.jpeg")
PACMEN_UP_PNG = safe_load_texture(config.get("pacmen_u_png1", ""))
PACMEN_DOWN_PNG = safe_load_texture(config.get("pacmen_d_png1", ""))
PACMEN_RAIGHT_PNG = safe_load_texture(config.get("pacmen_r_png1", ""))
PACMEN_LEFT_PNG = safe_load_texture(config.get("pacmen_l_png1", ""))
KEY_PNG = safe_load_texture(config.get("key_png1", ""))
GATE_PNG = safe_load_texture(config.get("gate_png1", ""))

# fallback simple textures (if none provided)
FALLBACK_RED = arcade.make_circle_texture(TILE_SIZE, arcade.color.RED)
FALLBACK_BLUE = arcade.make_circle_texture(TILE_SIZE, arcade.color.BLUE)
FALLBACK_GREY = arcade.make_circle_texture(TILE_SIZE, arcade.color.LIGHT_GRAY)

# ensure frames arrays exist and replace None with fallback
def _frame_or_fallback(t):
    return t if t is not None else FALLBACK_RED

RED_GHOST_FRAMES_R = [RED_GHOST_PNG_R or FALLBACK_RED, RED_GHOST_PNG_R2 or FALLBACK_RED]
RED_GHOST_FRAMES_L = [RED_GHOST_PNG_L or FALLBACK_RED, RED_GHOST_PNG_L2 or FALLBACK_RED]
RED_GHOST_FRAMES_U = [RED_GHOST_PNG_U or FALLBACK_RED, RED_GHOST_PNG_U2 or FALLBACK_RED]
RED_GHOST_FRAMES_D = [RED_GHOST_PNG_D or FALLBACK_RED, RED_GHOST_PNG_D2 or FALLBACK_RED]

BLUE_PNG = BLUE_PNG or FALLBACK_BLUE
GREY_PNG = GREY_PNG or FALLBACK_GREY

# Leaderboard & UI constants (keep as in your merged code)
LEADERBOARD_PANEL_LEFT = 5
LEADERBOARD_PANEL_WIDTH = 255
LEADERBOARD_PANEL_BOTTOM = 10
LEADERBOARD_PANEL_TOP_MARGIN = 5
LEADERBOARD_PADDING = 16
LEADERBOARD_TITLE_SIZE = 20
LEADERBOARD_TEXT_SIZE = 18
LEADERBOARD_LINE_HEIGHT = 18
LEADERBOARD_ROW_GAP = 2
LEADERBOARD_SCROLL_STEP = 20
LEADERBOARD_SCROLL_SPEED = 140.0
LEADERBOARD_SCROLL_ACCEL = 600.0
LEADERBOARD_SCROLL_MAX = 800.0
LEADERBOARD_VISIBLE_ROWS = 10
NAME_MAX_LEN = 18
GHOST_ANIM_INTERVAL = 0.12

# ------------------ START SCREEN ------------------
class SplashScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.timer = 0
        self.alpha = -100
        self.fade_speed = 0.7
        self.max_time = 12 * 60

        self.background_sprite = arcade.Sprite()
        if SPLASH_PNG is not None:
            self.background_sprite.texture = SPLASH_PNG
        else:
            # fallback plain color as a texture
            self.background_sprite.texture = arcade.make_soft_square_texture(WINDOW_WIDTH, arcade.color.DARK_SLATE_GRAY, 255, 255)
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
            # sprite has alpha attribute
            self.background_sprite.alpha = int(self.alpha)
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
        texture = PACMEN_UP_PNG if PACMEN_UP_PNG is not None else arcade.make_circle_texture(TILE_SIZE, arcade.color.YELLOW)
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
        self.is_have_key = False

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
        texture = PORTAL_PNG1 if PORTAL_PNG1 is not None else arcade.make_circle_texture(TILE_SIZE, arcade.color.AZURE)
        super().__init__(texture)
        self.width = TILE_SIZE
        self.height = TILE_SIZE

class Ghost(arcade.Sprite):
    def __init__(self):
        initial = RED_GHOST_PNG_R or FALLBACK_RED
        super().__init__(initial)
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        base_speed = 2
        self.change_x = random.choice([-1, 1]) * base_speed
        self.change_y = 0
        self.anim_timer = 0.0
        self.anim_frame = 0
        self.last_dir = "R"

    def update(self, delta_time: float = 1 / 60, *args, **kwargs):
        # move
        self.center_x += self.change_x
        self.center_y += self.change_y

    def advance_animation(self, delta_time: float):
        if self.change_x > 0:
            self.last_dir = "R"
        elif self.change_x < 0:
            self.last_dir = "L"
        elif self.change_y > 0:
            self.last_dir = "U"
        elif self.change_y < 0:
            self.last_dir = "D"

        if self.change_x == 0 and self.change_y == 0:
            return

        self.anim_timer += delta_time
        if self.anim_timer >= GHOST_ANIM_INTERVAL:
            self.anim_timer -= GHOST_ANIM_INTERVAL
            self.anim_frame = (self.anim_frame + 1) % 2

    def get_red_frames(self):
        if self.last_dir == "R":
            return RED_GHOST_FRAMES_R
        if self.last_dir == "L":
            return RED_GHOST_FRAMES_L
        if self.last_dir == "U":
            return RED_GHOST_FRAMES_U
        return RED_GHOST_FRAMES_D

class Coin(arcade.Sprite):
    def __init__(self):
        normal = arcade.make_circle_texture(16, arcade.color.YELLOW)
        power = arcade.make_circle_texture(16, arcade.color.PINK)
        super().__init__(normal)
        self.normal_texture = normal
        self.power_texture = power
        self.value = 5

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
        texture = APPLE_PNG if APPLE_PNG is not None else arcade.make_circle_texture(TILE_SIZE, arcade.color.ORANGE)
        super().__init__(texture)
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.value = 50

class Pill(arcade.Sprite):
    def __init__(self):
        texture = PILL_PNG if PILL_PNG is not None else arcade.make_circle_texture(TILE_SIZE, arcade.color.PURPLE)
        super().__init__(texture)
        self.width = TILE_SIZE
        self.height = TILE_SIZE

class Key(arcade.Sprite):
    def __init__(self):
        texture = KEY_PNG if KEY_PNG is not None else arcade.make_circle_texture(TILE_SIZE, arcade.color.GOLD)
        super().__init__(texture)
        self.width = TILE_SIZE
        self.height = TILE_SIZE

class Gate(arcade.Sprite):
    def __init__(self):
        texture = GATE_PNG if GATE_PNG is not None else arcade.make_soft_square_texture(TILE_SIZE, arcade.color.DARK_GRAY, 255, 255)
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
        self.gate_list = arcade.SpriteList()
        self.key_list = arcade.SpriteList()
        self.levels = load_levels()
        self.current_level = 0

        self.player = None
        self.game_over = False
        self.win = False
        self.power_mode = False
        self.power_timer = 0
        self.speed_up = False
        self.speed_up_timer = 0
        self.white_coin_timer = 5 * 60
        self.counter = 0.0
        self.exit = False
        self.paused_velocity = (0, 0)
        self.show_credits = False
        self.scores = load_scores(SCORES_PATH)
        self.scores_scroll = 0
        self.scroll_dir = 0
        self.scroll_speed = 0.0
        self.name_input = ""
        self.name_entry_active = False
        self.name_saved = False

        self.start_x = 0
        self.start_y = 0
        self.score = 0
        self.lives = 3
        self.max_score = 0

        # offsets (set in setup)
        self.offset_x = 0
        self.offset_y = 0
        self.map_width = 0
        self.map_height = 0

    def setup(self):
        self.wall_list = arcade.SpriteList()
        self.ghost_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.teleport_list = arcade.SpriteList()
        self.pill_list = arcade.SpriteList()
        self.apple_list = arcade.SpriteList()
        self.white_coin_list = arcade.SpriteList()
        self.gate_list = arcade.SpriteList()
        self.key_list = arcade.SpriteList()

        self.game_over = False
        self.win = False
        self.window.background_color = arcade.color.BLACK
        self.power_mode = False
        self.power_timer = 0
        self.speed_up = False
        self.speed_up_timer = 0
        self.white_coin_timer = 5 * 60
        self.scores_scroll = 0
        self.scroll_dir = 0
        self.scroll_speed = 0.0
        self.name_input = ""
        self.name_entry_active = False
        self.name_saved = False

        level = self.levels[self.current_level]
        rows = len(level)
        cols = max(len(r) for r in level)

        # sizes and center offsets
        self.map_width = cols * TILE_SIZE
        self.map_height = rows * TILE_SIZE
        self.offset_x = (WINDOW_WIDTH - self.map_width) // 2
        self.offset_y = (WINDOW_HEIGHT - self.map_height) // 2

        for row_idx, row in enumerate(level):
            for col_idx, cell in enumerate(row):
                x = col_idx * TILE_SIZE + TILE_SIZE / 2 + self.offset_x
                y = (rows - row_idx - 1) * TILE_SIZE + TILE_SIZE / 2 + self.offset_y

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
                elif cell == "K":
                    key = Key()
                    key.center_x = x
                    key.center_y = y
                    self.key_list.append(key)
                elif cell == "E":
                    gate = Gate()
                    gate.center_x = x
                    gate.center_y = y
                    self.gate_list.append(gate)
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
        if not hasattr(self, "levels") or not self.levels:
            return

        level = self.levels[self.current_level]
        rows = len(level)
        cols = max(len(r) for r in level)

        free_positions = []
        for row_idx, row in enumerate(level):
            for col_idx, cell in enumerate(row):
                if cell == "." or cell == "A":
                    x = col_idx * TILE_SIZE + TILE_SIZE / 2 + self.offset_x
                    y = (rows - row_idx - 1) * TILE_SIZE + TILE_SIZE / 2 + self.offset_y
                    collides = any(
                        sprite.center_x == x and sprite.center_y == y
                        for sprite_list in (self.coin_list, self.apple_list, self.white_coin_list)
                        for sprite in sprite_list
                    )
                    if not collides:
                        free_positions.append((x, y))

        if free_positions:
            x, y = random.choice(free_positions)
            coin = WhiteCoin()
            coin.center_x = x
            coin.center_y = y
            self.white_coin_list.append(coin)

    def add_score(self, name, time_spent):
        self.scores.append({"name": name, "time": time_spent})
        self.scores.sort(key=lambda item: item["time"])
        self.scores = self.scores[:100]
        save_scores(SCORES_PATH, self.scores)

    def get_scores_scroll_max(self):
        panel_top = WINDOW_HEIGHT - LEADERBOARD_PANEL_TOP_MARGIN
        list_height = LEADERBOARD_VISIBLE_ROWS * LEADERBOARD_LINE_HEIGHT
        list_top = panel_top - LEADERBOARD_PADDING - LEADERBOARD_TITLE_SIZE - 6
        list_bottom = list_top - list_height
        visible_height = list_top - list_bottom
        row_step = LEADERBOARD_LINE_HEIGHT + LEADERBOARD_ROW_GAP
        return max(0, len(self.scores) * row_step - visible_height)

    def update_scores_scroll(self, delta_time):
        if not (self.game_over or self.win or self.exit):
            return
        if self.name_entry_active:
            return
        if self.scroll_dir == 0:
            self.scroll_speed = 0.0
            return
        self.scroll_speed = min(LEADERBOARD_SCROLL_MAX, self.scroll_speed + LEADERBOARD_SCROLL_ACCEL * delta_time)
        delta = self.scroll_dir * self.scroll_speed * delta_time
        max_scroll = self.get_scores_scroll_max()
        self.scores_scroll = max(0, min(self.scores_scroll + delta, max_scroll))

    def on_draw(self):
        self.clear()
        self.wall_list.draw()
        self.white_coin_list.draw()
        self.coin_list.draw()
        self.apple_list.draw()
        self.teleport_list.draw()
        self.key_list.draw()
        self.pill_list.draw()
        self.ghost_list.draw()
        self.player_list.draw()
        self.gate_list.draw()
        show_leaderboard = self.game_over or self.win or self.exit
        stats_x = 10
        if show_leaderboard:
            panel_left = LEADERBOARD_PANEL_LEFT
            panel_right = LEADERBOARD_PANEL_LEFT + LEADERBOARD_PANEL_WIDTH
            panel_top = WINDOW_HEIGHT - LEADERBOARD_PANEL_TOP_MARGIN
            list_height = LEADERBOARD_VISIBLE_ROWS * LEADERBOARD_LINE_HEIGHT
            panel_bottom = panel_top - (LEADERBOARD_PADDING * 2 + LEADERBOARD_TITLE_SIZE + 6 + list_height)
            list_top = panel_top - LEADERBOARD_PADDING - LEADERBOARD_TITLE_SIZE + 6
            list_bottom = list_top - list_height
            visible_height = list_top - list_bottom
            row_step = LEADERBOARD_LINE_HEIGHT + LEADERBOARD_ROW_GAP
            max_scroll = max(0,len(self.scores) * row_step - visible_height)
            self.scores_scroll = max(0,min(self.scores_scroll,max_scroll))

            arcade.draw_lrbt_rectangle_filled(panel_left,panel_right,panel_bottom,panel_top,arcade.color.DARK_VIOLET)
            arcade.draw_text("TOP:",panel_left + LEADERBOARD_PADDING - 15,
                             panel_top - LEADERBOARD_PADDING - LEADERBOARD_TITLE_SIZE + 15,
                             arcade.color.BONE,LEADERBOARD_TITLE_SIZE)

            y = list_top - LEADERBOARD_LINE_HEIGHT + self.scores_scroll
            for idx,item in enumerate(self.scores,start=1):
                if y < list_bottom - LEADERBOARD_LINE_HEIGHT or y > list_top + LEADERBOARD_LINE_HEIGHT:
                    y -= row_step
                    continue
                name = item["name"]
                time_str = f"{item['time']:.1f}s"
                arcade.draw_text(f"{idx}. {name} - {time_str}",panel_left + LEADERBOARD_PADDING,y,
                                 arcade.color.AQUAMARINE,LEADERBOARD_TEXT_SIZE)
                y -= row_step

            stats_x = panel_right + 10

        # HUD
        if self.player:
            arcade.draw_text(f"Score: {self.player.score}",stats_x,WINDOW_HEIGHT - 45,arcade.color.WHITE,16)
        else:
            arcade.draw_text(f"Score: 0",stats_x,WINDOW_HEIGHT - 45,arcade.color.WHITE,16)
        arcade.draw_text(f"Lives: {self.lives}",stats_x,WINDOW_HEIGHT - 65,arcade.color.WHITE,16)
        arcade.draw_text(f"Time: {round(self.counter)} s",stats_x,WINDOW_HEIGHT - 25,arcade.color.WHITE,16)

        def draw_text_block(text_items,pad=12,border=6,
                            inner_color=arcade.color.INDIGO,
                            outer_color=arcade.color.IMPERIAL_PURPLE):
            text_objs = [arcade.Text(t,x,y,c,s) for t,x,y,c,s in text_items]
            left = float("inf")
            right = float("-inf")
            bottom = float("inf")
            top = float("-inf")
            for obj in text_objs:
                left = min(left,obj.x)
                right = max(right,obj.x + obj.content_width)
                bottom = min(bottom,obj.y)
                top = max(top,obj.y + obj.content_height)
            arcade.draw_lrbt_rectangle_filled(
                left - (pad + border) - 30,
                right + (pad + border) + 5,
                bottom - (pad + border) - 15,
                top + (pad + border) - 6,
                outer_color,
            )
            arcade.draw_lrbt_rectangle_filled(
                left - pad - 25,
                right + pad,
                bottom - pad - 10,
                top + pad - 12,
                inner_color,
            )
            for obj in text_objs:
                obj.draw()

        if self.game_over:
            arcade.draw_text("To see credits press: C",WINDOW_WIDTH - 240,WINDOW_HEIGHT - 25,arcade.color.CHERRY,20)
            draw_text_block([
                ("GAME OVER!",WINDOW_WIDTH / 2 - 100,WINDOW_HEIGHT / 2,arcade.color.RED,32),
                (f"TIME YOU SPENT: {round(self.counter)} s",WINDOW_WIDTH / 2 - 150,WINDOW_HEIGHT / 2 - 40,arcade.color.PINK,
                 32),
            ])
        elif self.win:
            arcade.draw_text("To see credits press: C",WINDOW_WIDTH - 240,WINDOW_HEIGHT - 25,arcade.color.CHERRY,20)
            draw_text_block([
                ("YOU WON!",WINDOW_WIDTH / 2 - 100,WINDOW_HEIGHT / 2,arcade.color.PINK,32),
                (f"TIME YOU SPENT: {round(self.counter)} s",WINDOW_WIDTH / 2 - 150,WINDOW_HEIGHT / 2 - 40,arcade.color.PINK,
                 32),
                (f"LIFES YOU SPENT: {abs(self.lives - 3)}",WINDOW_WIDTH / 2 - 150,WINDOW_HEIGHT / 2 - 80,arcade.color.PINK,
                 32),
            ])
        elif self.exit:
            arcade.draw_text("To see credits press: C",WINDOW_WIDTH - 240,WINDOW_HEIGHT - 25,arcade.color.CHERRY,20)
            draw_text_block([
                ("Are you sure you want to quit?",WINDOW_WIDTH / 2 - 250,WINDOW_HEIGHT / 2 - 10,arcade.color.PINK,32),
                ("To continue press: SPACE",WINDOW_WIDTH / 2 - 200,WINDOW_HEIGHT / 2 - 50,arcade.color.GREEN,32),
                ("To quit press: ESC",WINDOW_WIDTH / 2 - 140,WINDOW_HEIGHT / 2 - 90,arcade.color.RED,32),
            ])

        if self.win and self.name_entry_active:
            prompt = "ENTER YOUR NAME:"
            input_text = f"{self.name_input}_"
            arcade.draw_text(prompt,WINDOW_WIDTH / 2 - 60,WINDOW_HEIGHT / 2 + 220,arcade.color.RED,24)
            arcade.draw_text(input_text,WINDOW_WIDTH / 2 - 60,WINDOW_HEIGHT / 2 + 185,arcade.color.AQUAMARINE,24)

        if self.show_credits and (self.game_over or self.win or self.exit):
            credits = [
                "DEVELOPED BY: DALTON.GAMES",
                " ",
                " ",
                " ",
                " ",
                "Team:",
                "SASHA PERCHIK",
                "MARK DONOV",
                "SEVVA BOGOMOLOV",
                "KIM POLYATSKYI",
                "ANITA KNUAZEVA",
            ]
            size = 45
            line_gap = 8
            total_height = len(credits) * (size + line_gap) - line_gap
            start_y = WINDOW_HEIGHT / 2 + total_height / 2
            max_width = max(arcade.Text(t,0,0,arcade.color.BROWN,size).content_width for t in credits)
            arcade.draw_lrbt_rectangle_filled(0,WINDOW_WIDTH,0,WINDOW_HEIGHT,arcade.color.COOL_BLACK)
            y = start_y - size
            for text in credits:
                arcade.draw_text(text,WINDOW_WIDTH / 2 - max_width / 2,y,arcade.color.BROWN,size)
                y -= size + line_gap

    def on_key_press(self, key: int, modifiers):
        if self.name_entry_active:
            if key == arcade.key.BACKSPACE:
                self.name_input = self.name_input[:-1]
            elif key == arcade.key.ENTER:
                name = self.name_input.strip()
                if name:
                    self.add_score(name,round(self.counter,1))
                self.name_saved = True
                self.name_entry_active = False
            return

        if (self.game_over or self.win or self.exit) and key == arcade.key.C:
            self.show_credits = not self.show_credits
            if PLAY_SOUND:
                play_sound(PLAY_SOUND)
            return
        if (self.game_over or self.win or self.exit) and key in (arcade.key.W,arcade.key.UP):
            self.scroll_dir = -1
            self.scroll_speed = max(self.scroll_speed,LEADERBOARD_SCROLL_SPEED)
            return
        if (self.game_over or self.win or self.exit) and key in (arcade.key.S,arcade.key.DOWN):
            self.scroll_dir = 1
            self.scroll_speed = max(self.scroll_speed,LEADERBOARD_SCROLL_SPEED)
            return
        if self.exit:
            if key == arcade.key.ESCAPE:
                self.window.close()
            elif key == arcade.key.SPACE:
                if PLAY_SOUND:
                    play_sound(PLAY_SOUND)
                self.exit = False
                if self.player:
                    self.player.change_x,self.player.change_y = self.paused_velocity
            return

        if not self.player:
            return

        if key in (arcade.key.UP, arcade.key.W):
            if PACMEN_UP_PNG is not None:
                self.player.texture = PACMEN_UP_PNG
            self.player.height = TILE_SIZE
            self.player.width = TILE_SIZE
            self.player.change_x = 0
            self.player.change_y = self.player.speed

        elif key in (arcade.key.DOWN, arcade.key.S):
            if PACMEN_DOWN_PNG is not None:
                self.player.texture = PACMEN_DOWN_PNG
            self.player.width = TILE_SIZE
            self.player.height = TILE_SIZE
            self.player.change_x = 0
            self.player.change_y = -self.player.speed
        elif key in (arcade.key.RIGHT, arcade.key.D):
            if PACMEN_RAIGHT_PNG is not None:
                self.player.texture = PACMEN_RAIGHT_PNG
            self.player.width = TILE_SIZE
            self.player.height = TILE_SIZE
            self.player.change_x = self.player.speed
            self.player.change_y = 0
        elif key in (arcade.key.LEFT, arcade.key.A):
            if PACMEN_LEFT_PNG is not None:
                self.player.texture = PACMEN_LEFT_PNG
            self.player.width = TILE_SIZE
            self.player.height = TILE_SIZE
            self.player.change_x = -self.player.speed
            self.player.change_y = 0
        elif key == arcade.key.ESCAPE:
            if PAUSE_SOUND:
                play_sound(PAUSE_SOUND)
            self.exit = True
            if self.player:
                self.paused_velocity = (self.player.change_x, self.player.change_y)
                self.player.stop()

    def on_key_release(self, key: int, modifiers):
        if (self.game_over or self.win or self.exit) and key in (arcade.key.W, arcade.key.UP, arcade.key.S, arcade.key.DOWN):
            self.scroll_dir = 0
            self.scroll_speed = 0.0

    def on_text(self, text):
        if self.name_entry_active and len(self.name_input) < NAME_MAX_LEN:
            self.name_input += text

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not (self.game_over or self.win or self.exit):
            return
        if self.name_entry_active:
            return
        if scroll_y != 0:
            max_scroll = self.get_scores_scroll_max()
            self.scores_scroll = max(0, min(self.scores_scroll - scroll_y * LEADERBOARD_SCROLL_STEP, max_scroll))

    def on_update(self, delta_time):
        # if finished or paused -> update leaderboard scroll only
        if self.game_over or self.win or self.exit:
            self.update_scores_scroll(delta_time)
            return

        if self.player and self.player.teleport_cooldown > 0:
            self.player.teleport_cooldown -= 1

        # update time using real delta_time
        self.counter += delta_time

        if self.player:
            self.player.move()

        # PILLS
        pill_hit = arcade.check_for_collision_with_list(self.player, self.pill_list)
        if pill_hit:
            self.speed_up_timer = 5 * 60
            self.speed_up = True
            self.player.speed = self.player.speed_basic + self.player.speed_grader
            for pill in pill_hit:
                pill.remove_from_sprite_lists()
                if PILL_SOUND:
                    play_sound(PILL_SOUND)

        if self.speed_up:
            self.speed_up_timer -= 1
            if self.speed_up_timer <= 0:
                self.speed_up = False
                self.player.speed = self.player.speed_basic

        # GHOST COLLISIONS
        ghosts_hit = arcade.check_for_collision_with_list(self.player, self.ghost_list)
        if ghosts_hit:
            if self.power_mode:
                for ghost in ghosts_hit:
                    ghost.remove_from_sprite_lists()
                    if EAT_GHOST_SOUND:
                        play_sound(EAT_GHOST_SOUND)
                    self.player.score += 250
            else:
                self.lives -= 1
                if GHOST_SOUND:
                    play_sound(GHOST_SOUND)
                if self.lives <= 0:
                    if DEAF_SOUND:
                        play_sound(DEAF_SOUND)
                    self.game_over = True
                else:
                    self.player.center_x = self.start_x
                    self.player.center_y = self.start_y
                    self.player.change_x = 0
                    self.player.change_y = 0

        # MOVE GHOSTS (with robust texture switching & animation)
        for ghost in list(self.ghost_list):
            old_x = ghost.center_x
            old_y = ghost.center_y

            # advance animation timer
            ghost.advance_animation(delta_time)

            # set texture for power mode OR normal frames
            if self.power_mode:
                # make sure we assign a valid texture object
                ghost.texture = BLUE_PNG or GREY_PNG or FALLBACK_BLUE
            else:
                frames = ghost.get_red_frames()
                # frames should be a pair of textures; choose based on anim_frame
                if frames and len(frames) > 0:
                    idx = ghost.anim_frame % len(frames)
                    ghost.texture = frames[idx] or FALLBACK_RED
                else:
                    ghost.texture = FALLBACK_RED

            # move & collision: use ghost.update() which moves according to change_x/change_y
            ghost.update()

            if arcade.check_for_collision_with_list(ghost, self.wall_list):
                # rollback
                ghost.center_x = old_x
                ghost.center_y = old_y
                # choose a new direction with the same magnitude as before (to avoid speed mismatch)
                speed_val = abs(ghost.change_x) if ghost.change_x != 0 else (abs(ghost.change_y) if ghost.change_y != 0 else 2)
                possible = [(speed_val,0),(-speed_val,0),(0,speed_val),(0,-speed_val)]
                ghost.change_x, ghost.change_y = random.choice(possible)

        # COINS
        coins_hit = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coins_hit:
            self.player.score += coin.value
            coin.remove_from_sprite_lists()
            if COIN_SOUND:
                play_sound(COIN_SOUND)

        blink_power = False
        if self.power_mode and self.power_timer <= 2 * 60:
            blink_power = (self.power_timer // 12) % 2 == 0

        for coin in self.coin_list:
            if self.power_mode and self.power_timer <= 2 * 60:
                coin.set_power(blink_power)
            else:
                coin.set_power(self.power_mode)

        # WHITE COIN
        self.white_coin_timer -= 1
        if self.white_coin_timer <= 0:
            self.spawn_white_coin()
            self.white_coin_timer = 5 * 60

        for coin in list(self.white_coin_list):
            coin.timer += 1
            if coin.timer >= coin.duration:
                coin.remove_from_sprite_lists()

        white_hits = arcade.check_for_collision_with_list(self.player, self.white_coin_list)
        for coin in white_hits:
            coin.remove_from_sprite_lists()
            self.white_coin_speed_timer = 5 * 60
            for ghost in self.ghost_list:
                # double movement vector (keep direction)
                if ghost.change_x > 0:
                    ghost.change_x = abs(ghost.change_x) * 2
                elif ghost.change_x < 0:
                    ghost.change_x = -abs(ghost.change_x) * 2
                if ghost.change_y > 0:
                    ghost.change_y = abs(ghost.change_y) * 2
                elif ghost.change_y < 0:
                    ghost.change_y = -abs(ghost.change_y) * 2

        if hasattr(self, "white_coin_speed_timer"):
            self.white_coin_speed_timer -= 1
            if self.white_coin_speed_timer <= 0:
                for ghost in self.ghost_list:
                    # normalize back to base 4 pixels if needed
                    if ghost.change_x > 0:
                        ghost.change_x = 2
                    elif ghost.change_x < 0:
                        ghost.change_x = -2
                    if ghost.change_y > 0:
                        ghost.change_y = 2
                    elif ghost.change_y < 0:
                        ghost.change_y = -2
                del self.white_coin_speed_timer

        # POWER MODE (apples)
        apples_hit = arcade.check_for_collision_with_list(self.player, self.apple_list)
        if apples_hit:
            self.power_mode = True
            self.power_timer = 10 * 60
            if APPLE_SOUND:
                play_sound(APPLE_SOUND)

        if self.power_mode:
            self.power_timer -= 1
            if self.power_timer == 2 * 60:
                if POWER_END_SOUND:
                    play_sound(POWER_END_SOUND)
            if self.power_timer <= 0:
                self.power_mode = False

        for apple in apples_hit:
            self.player.score += apple.value
            apple.remove_from_sprite_lists()

        # TELEPORTS
        tp_hits = arcade.check_for_collision_with_list(self.player, self.teleport_list)
        if tp_hits and self.player.teleport_cooldown == 0:
            current_portal = tp_hits[0]
            other_portals = [p for p in self.teleport_list if p is not current_portal]
            if other_portals:
                dest = random.choice(other_portals)
                self.player.center_x = dest.center_x
                self.player.center_y = dest.center_y
                if PORTAL_SOUND:
                    play_sound(PORTAL_SOUND)
                self.player.teleport_cooldown = 5 * 60

        # WALL collision: snap using offsets
        mat_x = int((self.player.center_x - self.offset_x) // TILE_SIZE)
        mat_y = int((self.player.center_y - self.offset_y) // TILE_SIZE)
        if arcade.check_for_collision_with_list(self.player, self.wall_list):
            self.player.center_x = mat_x * TILE_SIZE + TILE_SIZE / 2 + self.offset_x
            self.player.center_y = mat_y * TILE_SIZE + TILE_SIZE / 2 + self.offset_y
            # stop movement to avoid tunnelling inside wall
            self.player.change_x = 0
            self.player.change_y = 0

        # LEVEL COMPLETE
        if len(self.coin_list) == 0 and len(self.apple_list) == 0:
            self.current_level += 1
            if self.current_level < len(self.levels):
                self.setup()
            else:
                if WIN_SOUND:
                    play_sound(WIN_SOUND)
                self.win = True
                if not self.name_saved:
                    self.name_entry_active = True
                    self.name_input = ""
                    self.scores = load_scores(SCORES_PATH)

        # KEYS & GATES
        key_hits = arcade.check_for_collision_with_list(self.player, self.key_list)
        if key_hits:
            if PILL_SOUND:
                play_sound(PILL_SOUND)
            for k in key_hits:
                k.remove_from_sprite_lists()
            self.player.is_have_key = True

        gate_hits = arcade.check_for_collision_with_list(self.player, self.gate_list)
        if gate_hits and self.player.is_have_key:
            if DOR_SOUND:
                play_sound(DOR_SOUND)
            for g in gate_hits:
                g.remove_from_sprite_lists()
        elif gate_hits and self.player.is_have_key is False:
            mat_x = int((self.player.center_x - self.offset_x) // TILE_SIZE)
            mat_y = int((self.player.center_y - self.offset_y) // TILE_SIZE)
            self.player.center_x = mat_x * TILE_SIZE + TILE_SIZE / 2 + self.offset_x
            self.player.center_y = mat_y * TILE_SIZE + TILE_SIZE / 2 + self.offset_y
            self.player.change_x = 0
            self.player.change_y = 0

# ------------------ MAIN ------------------
def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    start = SplashScreen()
    window.show_view(start)
    if LOGO_SOUND:
        play_sound(LOGO_SOUND)
    arcade.run()

if __name__ == "__main__":
    main()
