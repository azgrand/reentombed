import sys
import os
import random
import math
import array
from typing import List, Tuple, Dict
import pygame

# Import language literals
from assets.lang import TEXTS

# --- Game & Mechanics Constants ---
TILE_SIZE = 20
UI_HEIGHT = 40

# --- Feature Configuration ---
# You can change these values to spawn more or fewer special tiles!
NUM_TELEPORTERS = 10  # Must be an even number or >= 2 to link properly
NUM_TRAPS = 5  # Number of gray tiles that paralyze the player

# Colors (RGB format)
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
GREEN = (0, 255, 0)  # Player
RED = (255, 50, 50)  # Goal
GRAY = (50, 50, 50)  # UI separator line
TRAIL_COLOR = (50, 150, 200)  # Cyan/blue trail

# New tile colors
PURPLE = (150, 50, 200)  # Teleporters (Tile ID: 3)
TRAP_COLOR = (120, 120, 120)  # Stun traps (Tile ID: 4)


def generate_synthetic_sound(frequency: float, duration: float, volume: float = 0.1) -> pygame.mixer.Sound:
    """
    Generates a simple synthetic sine wave sound from scratch for short SFX.
    """
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    max_amplitude = 32767

    for i in range(n_samples):
        time = i / sample_rate
        sample = int(volume * max_amplitude * math.sin(2 * math.pi * frequency * time))
        buf.append(sample)
        buf.append(sample)

    return pygame.mixer.Sound(buffer=buf)


def generate_maze(cols: int, rows: int) -> List[List[int]]:
    """
    Generates a random maze using Randomized Depth-First Search.
    Tile Legend:
    0 = Path, 1 = Wall, 2 = Goal, 3 = Teleporter, 4 = Trap
    """
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]

    def carve_passages(cx: int, cy: int) -> None:
        """Recursively carves paths through the grid."""
        maze[cy][cx] = 0
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 < nx < cols - 1 and 0 < ny < rows - 1:
                if maze[ny][nx] == 1:
                    maze[cy + dy // 2][cx + dx // 2] = 0
                    carve_passages(nx, ny)

    carve_passages(1, 1)

    # Place the goal (2) at the furthest available path from the bottom-right
    goal_placed = False
    for y in range(rows - 2, 0, -1):
        for x in range(cols - 2, 0, -1):
            if maze[y][x] == 0:
                maze[y][x] = 2
                goal_placed = True
                break
        if goal_placed:
            break

    # Find dead ends and regular paths to place our special tiles
    dead_ends = []
    regular_paths = []

    for y in range(1, rows - 1):
        for x in range(1, cols - 1):
            if maze[y][x] == 0:
                wall_count = 0
                for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    if maze[y + dy][x + dx] == 1:
                        wall_count += 1

                if not (x == 1 and y == 1):
                    if wall_count >= 3:
                        dead_ends.append((x, y))
                    else:
                        regular_paths.append((x, y))

    random.shuffle(dead_ends)
    random.shuffle(regular_paths)

    available_spots = dead_ends + regular_paths

    actual_teleporters = min(NUM_TELEPORTERS, len(available_spots))
    if actual_teleporters == 1:
        actual_teleporters = 0

    for _ in range(actual_teleporters):
        tx, ty = available_spots.pop(0)
        maze[ty][tx] = 3

    actual_traps = min(NUM_TRAPS, len(available_spots))
    for _ in range(actual_traps):
        tx, ty = available_spots.pop(0)
        maze[ty][tx] = 4

    return maze


def show_game_over_screen(screen: pygame.Surface, score: int) -> None:
    """
    Displays the final score and waits for the player to restart or quit.
    """
    width = screen.get_width()
    height = screen.get_height()

    large_font = pygame.font.SysFont(None, 64)
    small_font = pygame.font.SysFont(None, 36)

    score_string = TEXTS["final_score"].format(score=score)
    restart_string = TEXTS["restart_prompt"]

    score_text = large_font.render(score_string, True, GREEN)
    restart_text = small_font.render(restart_string, True, WHITE)

    score_rect = score_text.get_rect(center=(width // 2, height // 2 - 30))
    restart_rect = restart_text.get_rect(center=(width // 2, height // 2 + 40))

    overlay = pygame.Surface((width, height))
    overlay.set_alpha(220)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    screen.blit(score_text, score_rect)
    screen.blit(restart_text, restart_rect)
    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    waiting_for_input = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def run_game() -> None:
    """Main execution function handling the game loop and logic."""
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2)

    # Synthesize SFX
    move_sfx = generate_synthetic_sound(frequency=600.0, duration=0.03, volume=0.05)
    win_sfx = generate_synthetic_sound(frequency=1046.50, duration=0.8, volume=0.2)
    trap_sfx = generate_synthetic_sound(frequency=150.0, duration=0.5, volume=0.1)
    teleport_sfx = generate_synthetic_sound(frequency=800.0, duration=0.2, volume=0.1)

    # Load external background music
    music_path = os.path.join("assets", "music", "music.ogg")
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.3)  # Adjust volume between 0.0 and 1.0
        # -1 means loop indefinitely
        pygame.mixer.music.play(loops=-1)
    except pygame.error as e:
        print(f"Warning: Could not load background music from {music_path}. Running without music. Error: {e}")

    display_info = pygame.display.Info()
    initial_width = int(display_info.current_w * 0.8)
    initial_height = int(display_info.current_h * 0.8)

    screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)
    pygame.display.set_caption(TEXTS["window_title"])
    clock = pygame.time.Clock()
    ui_font = pygame.font.SysFont(None, 40)

    running = True

    while running:
        current_w = screen.get_width()
        current_h = screen.get_height()

        maze_cols = max(5, current_w // TILE_SIZE)
        maze_rows = max(5, (current_h - UI_HEIGHT) // TILE_SIZE)

        if maze_cols % 2 == 0: maze_cols -= 1
        if maze_rows % 2 == 0: maze_rows -= 1

        maze = generate_maze(maze_cols, maze_rows)
        player_x, player_y = 1, 1

        teleporters: List[Tuple[int, int]] = []
        for y in range(maze_rows):
            for x in range(maze_cols):
                if maze[y][x] == 3:
                    teleporters.append((x, y))

        teleport_links: Dict[Tuple[int, int], Tuple[int, int]] = {}
        if len(teleporters) >= 2:
            for i in range(len(teleporters)):
                teleport_links[teleporters[i]] = teleporters[(i + 1) % len(teleporters)]

        game_state = "playing"
        has_moved = False
        auto_mode = False
        start_time = 0
        score = 0
        elapsed_seconds = 0

        stun_until = 0
        just_teleported = False

        trail = set()
        trail.add((player_x, player_y))
        last_ai_move = (0, 0)

        # Make sure music restarts on new levels if it was stopped
        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.play(loops=-1)
            except pygame.error:
                pass

        while game_state == "playing":
            current_w = screen.get_width()
            current_h = screen.get_height()
            current_time = pygame.time.get_ticks()

            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    pass
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a and not has_moved:
                        auto_mode = True
                        has_moved = True
                        start_time = pygame.time.get_ticks()

                    if not auto_mode and current_time >= stun_until:
                        moved_now = False
                        if event.key == pygame.K_UP and maze[player_y - 1][player_x] != 1:
                            player_y -= 1
                            moved_now = True
                        elif event.key == pygame.K_DOWN and maze[player_y + 1][player_x] != 1:
                            player_y += 1
                            moved_now = True
                        elif event.key == pygame.K_LEFT and maze[player_y][player_x - 1] != 1:
                            player_x -= 1
                            moved_now = True
                        elif event.key == pygame.K_RIGHT and maze[player_y][player_x + 1] != 1:
                            player_x += 1
                            moved_now = True

                        if moved_now:
                            move_sfx.play()
                            trail.add((player_x, player_y))

                            if not has_moved:
                                has_moved = True
                                start_time = pygame.time.get_ticks()

                            if maze[player_y][player_x] == 4:
                                trap_sfx.play()
                                stun_until = current_time + 2000
                            elif maze[player_y][player_x] == 3:
                                if not just_teleported and (player_x, player_y) in teleport_links:
                                    teleport_sfx.play()
                                    player_x, player_y = teleport_links[(player_x, player_y)]
                                    just_teleported = True
                                    trail.add((player_x, player_y))
                            else:
                                just_teleported = False

                                # --- Crazy AI Logic ---
            if auto_mode and current_time >= stun_until:
                for _ in range(5):
                    if maze[player_y][player_x] == 2:
                        break

                    possible_moves = []
                    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

                    for dx, dy in directions:
                        if maze[player_y + dy][player_x + dx] != 1:
                            possible_moves.append((dx, dy))

                    if len(possible_moves) > 1 and random.random() > 0.10:
                        opposite_move = (-last_ai_move[0], -last_ai_move[1])
                        if opposite_move in possible_moves:
                            possible_moves.remove(opposite_move)

                    dx, dy = random.choice(possible_moves)
                    player_x += dx
                    player_y += dy
                    trail.add((player_x, player_y))
                    last_ai_move = (dx, dy)

                    if maze[player_y][player_x] == 4:
                        trap_sfx.play()
                        stun_until = pygame.time.get_ticks() + 2000
                        break

                    elif maze[player_y][player_x] == 3:
                        if not just_teleported and (player_x, player_y) in teleport_links:
                            teleport_sfx.play()
                            player_x, player_y = teleport_links[(player_x, player_y)]
                            just_teleported = True
                            trail.add((player_x, player_y))
                    else:
                        just_teleported = False

            # --- Game State Updates ---
            if maze[player_y][player_x] == 2:
                game_state = "won"
                pygame.mixer.music.stop()  # Stop the background .ogg
                win_sfx.play()

            if has_moved and game_state == "playing":
                elapsed_seconds = (current_time - start_time) // 1000
                score = elapsed_seconds * 5

            # --- Drawing ---
            screen.fill(BLACK)

            offset_x = (current_w - (maze_cols * TILE_SIZE)) // 2
            offset_y = UI_HEIGHT + (current_h - UI_HEIGHT - (maze_rows * TILE_SIZE)) // 2

            score_string = TEXTS["score_display"].format(score=score)
            time_string = TEXTS["time_display"].format(seconds=elapsed_seconds)

            score_text = ui_font.render(score_string, True, WHITE)

            time_color = RED if current_time < stun_until else WHITE
            time_text = ui_font.render(time_string, True, time_color)

            screen.blit(score_text, (20, 10))
            screen.blit(time_text, (current_w - time_text.get_width() - 20, 10))
            pygame.draw.line(screen, GRAY, (0, UI_HEIGHT - 1), (current_w, UI_HEIGHT - 1), 2)

            for y in range(maze_rows):
                for x in range(maze_cols):
                    rect_x = offset_x + (x * TILE_SIZE)
                    rect_y = offset_y + (y * TILE_SIZE)
                    rect = pygame.Rect(rect_x, rect_y, TILE_SIZE, TILE_SIZE)

                    if maze[y][x] == 0:
                        if (x, y) in trail:
                            pygame.draw.rect(screen, TRAIL_COLOR, rect)
                        else:
                            pygame.draw.rect(screen, WHITE, rect)
                    elif maze[y][x] == 2:
                        pygame.draw.rect(screen, RED, rect)
                    elif maze[y][x] == 3:
                        pygame.draw.rect(screen, PURPLE, rect)
                    elif maze[y][x] == 4:
                        pygame.draw.rect(screen, TRAP_COLOR, rect)

            player_rect_x = offset_x + (player_x * TILE_SIZE)
            player_rect_y = offset_y + (player_y * TILE_SIZE)
            player_rect = pygame.Rect(player_rect_x, player_rect_y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, GREEN, player_rect)

            pygame.display.flip()
            clock.tick(30)

        show_game_over_screen(screen, score)