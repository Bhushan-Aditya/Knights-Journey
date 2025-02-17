import pygame
import sys
import time
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.font.init()

# Constants
WINDOW_SIZE = 900
BOARD_SIZE = 8
SQUARE_SIZE = (WINDOW_SIZE - 240) // BOARD_SIZE
BACKGROUND_COLOR = (34, 40, 49)
LIGHT_TILE = (255, 248, 220)
DARK_TILE = (139, 69, 19)
HIGHLIGHT_COLOR = (255, 223, 127, 128)
HINT_COLOR = (0, 255, 0, 128)
WARNING_COLOR = (255, 0, 0, 128)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 149, 237)
BUTTON_TEXT_COLOR = WHITE
PANEL_COLOR = (245, 245, 245)
KNIGHT_COLOR = (178, 34, 34)  # Firebrick red for the knight symbol

# Set up the display
DISPLAYSURF = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Enhanced Knight's Tour")


class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.font = pygame.font.Font(None, 28)

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (0, 0, 0, 30), self.rect.inflate(2, 2), border_radius=8)
        text_surface = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return self.action
        return None


class KnightsTour:
    def __init__(self):
        self.reset_board()
        self.ai_speed = 100
        self.start_time = None
        self.elapsed_time = 0
        self.paused = False
        self.move_history = []
        self.hint_moves = []
        self.setup_buttons()

    def setup_buttons(self):
        panel_x = WINDOW_SIZE - 190
        self.buttons = [
            Button(panel_x, 280, 160, 40, "Undo", "undo"),
            Button(panel_x, 330, 160, 40, "Reset", "reset"),
            Button(panel_x, 380, 160, 40, "Hint", "hint"),
            Button(panel_x, 430, 160, 40, "Pause/Resume", "pause"),
            Button(panel_x, 480, 160, 40, "Speed +", "speed_up"),
            Button(panel_x, 530, 160, 40, "Speed -", "speed_down")
        ]

    def reset_board(self):
        self.board = [[-1 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_pos = None
        self.move_count = 0
        self.move_history = []
        self.start_time = None
        self.elapsed_time = 0
        self.paused = False
        self.hint_moves = []

    def is_valid_move(self, x, y):
        return (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and self.board[y][x] == -1)

    def count_possible_moves(self, x, y):
        count = 0
        for dx, dy in [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_move(next_x, next_y):
                count += 1
        return count

    def get_possible_moves(self):
        if not self.current_pos:
            return []
        possible_moves = []
        x, y = self.current_pos
        for dx, dy in [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_move(next_x, next_y):
                possible_moves.append((next_x, next_y))
        return possible_moves

    def warnsdorff_move(self, x, y):
        possible_moves = []
        for dx, dy in [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_move(next_x, next_y):
                num_next_moves = self.count_possible_moves(next_x, next_y)
                possible_moves.append((num_next_moves, next_x, next_y))
        if possible_moves:
            possible_moves.sort()
            return possible_moves[0][1], possible_moves[0][2]
        return None

    def solve_ai(self, start_x, start_y):
        if not self.start_time:
            self.start_time = time.time()

        if self.current_pos is None:
            self.current_pos = (start_x, start_y)
            self.board[start_y][start_x] = 0
            self.move_count = 1
            self.move_history = [(start_x, start_y)]

        while self.move_count < BOARD_SIZE * BOARD_SIZE:
            if self.paused:
                return False

            next_move = self.warnsdorff_move(*self.current_pos)
            if next_move is None:
                if self.move_history:
                    self.undo_move()
                    continue
                return False

            x, y = next_move
            self.board[y][x] = self.move_count
            self.current_pos = (x, y)
            self.move_count += 1
            self.move_history.append((x, y))

            self.draw_board()
            pygame.display.flip()
            pygame.time.delay(self.ai_speed)

            if not self.paused:
                self.elapsed_time = time.time() - self.start_time

        return True

    def try_manual_move(self, pos):
        x, y = (pos[0] - 20) // SQUARE_SIZE, (pos[1] - 20) // SQUARE_SIZE

        if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
            return False

        if not self.start_time:
            self.start_time = time.time()

        if not self.current_pos:
            self.current_pos = (x, y)
            self.board[y][x] = self.move_count
            self.move_count += 1
            self.move_history.append((x, y))
            return True

        if (x, y) in self.get_possible_moves():
            self.board[y][x] = self.move_count
            self.current_pos = (x, y)
            self.move_count += 1
            self.move_history.append((x, y))

            if not self.paused:
                self.elapsed_time = time.time() - self.start_time
            return True
        return False

    def undo_move(self):
        if self.move_history:
            x, y = self.move_history.pop()
            self.board[y][x] = -1
            self.move_count -= 1
            self.current_pos = self.move_history[-1] if self.move_history else None
            return True
        return False

    def get_hints(self):
        if not self.current_pos:
            return []
        possible_moves = self.get_possible_moves()
        rated_moves = []
        for move in possible_moves:
            x, y = move
            future_moves = self.count_possible_moves(x, y)
            rated_moves.append((future_moves, move))
        rated_moves.sort()
        return [move for _, move in rated_moves[:3]]

    def draw_board(self):
        DISPLAYSURF.fill(BACKGROUND_COLOR)

        # Draw the chess board
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                rect = pygame.Rect(x * SQUARE_SIZE + 20, y * SQUARE_SIZE + 20, SQUARE_SIZE, SQUARE_SIZE)
                color = LIGHT_TILE if (x + y) % 2 == 0 else DARK_TILE
                pygame.draw.rect(DISPLAYSURF, color, rect, border_radius=6)

                if self.board[y][x] != -1:
                    font = pygame.font.Font(None, 36)
                    text = font.render(str(self.board[y][x]), True, BLUE)
                    text_rect = text.get_rect(center=(rect.x + SQUARE_SIZE // 2, rect.y + SQUARE_SIZE // 2))
                    DISPLAYSURF.blit(text, text_rect)

        # Highlight possible moves
        for move in self.get_possible_moves():
            x, y = move
            highlight_rect = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight_rect.fill(HIGHLIGHT_COLOR)
            DISPLAYSURF.blit(highlight_rect, (x * SQUARE_SIZE + 20, y * SQUARE_SIZE + 20))

        # Highlight hint moves
        for move in self.hint_moves:
            x, y = move
            hint_rect = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            hint_rect.fill(HINT_COLOR)
            DISPLAYSURF.blit(hint_rect, (x * SQUARE_SIZE + 20, y * SQUARE_SIZE + 20))

        # Draw the knight symbol
        if self.current_pos:
            knight_x, knight_y = self.current_pos
            font = pygame.font.Font(None, 48)
            knight_text = font.render("N", True, KNIGHT_COLOR)
            text_rect = knight_text.get_rect(center=(
                knight_x * SQUARE_SIZE + SQUARE_SIZE // 2 + 20,
                knight_y * SQUARE_SIZE + SQUARE_SIZE // 2 + 20))
            DISPLAYSURF.blit(knight_text, text_rect)

        # Draw UI panel
        panel_rect = pygame.Rect(WINDOW_SIZE - 200, 20, 180, WINDOW_SIZE - 40)
        pygame.draw.rect(DISPLAYSURF, (0, 0, 0, 50), panel_rect.inflate(4, 4), border_radius=10)
        pygame.draw.rect(DISPLAYSURF, PANEL_COLOR, panel_rect, border_radius=10)

        # Draw stats
        font = pygame.font.Font(None, 32)
        stats_x = WINDOW_SIZE - 180

        # Title
        title_font = pygame.font.Font(None, 40)
        title = title_font.render("Statistics", True, BLACK)
        DISPLAYSURF.blit(title, (stats_x, 40))

        # Timer
        time_text = f"Time: {int(self.elapsed_time)}s"
        text = font.render(time_text, True, BLACK)
        DISPLAYSURF.blit(text, (stats_x, 100))

        # Move counter
        moves_text = f"Moves: {self.move_count}"
        text = font.render(moves_text, True, BLACK)
        DISPLAYSURF.blit(text, (stats_x, 140))

        # Speed indicator
        speed_text = f"Speed: {self.ai_speed}ms"
        text = font.render(speed_text, True, BLACK)
        DISPLAYSURF.blit(text, (stats_x, 180))

        # Draw all buttons
        for button in self.buttons:
            button.draw(DISPLAYSURF)

    def handle_button_click(self, event):
        for button in self.buttons:
            action = button.handle_event(event)
            if action:
                if action == "undo":
                    self.undo_move()
                elif action == "reset":
                    self.reset_board()
                elif action == "hint":
                    self.hint_moves = self.get_hints()
                elif action == "pause":
                    self.paused = not self.paused
                    if not self.paused:
                        self.start_time = time.time() - self.elapsed_time
                elif action == "speed_up":
                    self.ai_speed = max(50, self.ai_speed - 50)
                elif action == "speed_down":
                    self.ai_speed = min(500, self.ai_speed + 50)


def main():
    game = KnightsTour()
    clock = pygame.time.Clock()
    mode = None

    print("Knight's Tour")
    print("1. Manual mode")
    print("2. AI mode")
    while mode not in ["1", "2"]:
        mode = input("Choose your mode (1 or 2): ")

    if mode == "2":
        print("AI Mode initialized...")
        game.solve_ai(0, 0)
        print("AI completed the Knight's Tour!")

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in (MOUSEBUTTONDOWN, MOUSEMOTION):
                if mode == "1":
                    if event.pos[0] < WINDOW_SIZE - 200 and event.type == MOUSEBUTTONDOWN:
                        game.try_manual_move(event.pos)
                    else:
                        game.handle_button_click(event)
                else:
                    game.handle_button_click(event)

        game.draw_board()
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()