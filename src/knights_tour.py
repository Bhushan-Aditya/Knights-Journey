import pygame
import sys
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.font.init()

# Constants
WINDOW_SIZE = 800
BOARD_SIZE = 8
SQUARE_SIZE = (WINDOW_SIZE - 40) // BOARD_SIZE
BACKGROUND_COLOR = (34, 40, 49)  # Main background color
LIGHT_TILE = (255, 248, 220)  # Light beige tile
DARK_TILE = (139, 69, 19)  # Dark brown tile
HIGHLIGHT_COLOR = (255, 223, 127, 128)  # Semi-transparent gold for highlighting
KNIGHT_IMAGE_PATH = "knight.png"  # Replace with your knight image path
BLUE = (0, 0, 255)  # Move number color

# Set up the display
DISPLAYSURF = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Knight's Tour - Human & AI Modes")

# Knight Image Loading
def load_knight_image():
    try:
        image = pygame.image.load(KNIGHT_IMAGE_PATH).convert_alpha()
        image_scaled = pygame.transform.scale(image, (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        return image_scaled
    except Exception as e:
        print(f"Error loading knight image: {e}")
        return None

KNIGHT_IMAGE = load_knight_image()

class KnightsTour:
    def __init__(self):
        self.board = [[-1 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.moves = [(2, 1), (1, 2), (-1, 2), (-2, 1),
                     (-2, -1), (-1, -2), (1, -2), (2, -1)]
        self.current_pos = None
        self.move_count = 0
        self.possible_moves = []

    def is_valid_move(self, x, y):
        return (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and self.board[y][x] == -1)

    def count_possible_moves(self, x, y):
        count = 0
        for dx, dy in self.moves:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_move(next_x, next_y):
                count += 1
        return count

    def get_possible_moves(self):
        if not self.current_pos:
            return []
        possible_moves = []
        x, y = self.current_pos
        for dx, dy in self.moves:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_move(next_x, next_y):
                possible_moves.append((next_x, next_y))
        return possible_moves

    def warnsdorff_move(self, x, y):
        possible_moves = []
        for dx, dy in self.moves:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_move(next_x, next_y):
                num_next_moves = self.count_possible_moves(next_x, next_y)
                possible_moves.append((num_next_moves, next_x, next_y))
        if possible_moves:
            possible_moves.sort()
            return possible_moves[0][1], possible_moves[0][2]
        return None

    def solve_ai(self, start_x, start_y):
        self.reset_board()
        self.current_pos = (start_x, start_y)
        self.board[start_y][start_x] = 0
        self.move_count = 1

        while self.move_count < BOARD_SIZE * BOARD_SIZE:
            next_move = self.warnsdorff_move(*self.current_pos)
            if next_move is None:
                return False
            x, y = next_move
            self.board[y][x] = self.move_count
            self.current_pos = (x, y)
            self.move_count += 1
            self.draw_board()
            pygame.display.flip()
            pygame.time.delay(100)
        return True

    def reset_board(self):
        self.board = [[-1 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_pos = None
        self.move_count = 0
        self.possible_moves = []

    def try_manual_move(self, pos):
        x, y = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE

        if not self.current_pos:
            self.current_pos = (x, y)
            self.board[y][x] = self.move_count
            self.move_count += 1
            self.possible_moves = self.get_possible_moves()
            return True

        if (x, y) in self.possible_moves:
            self.board[y][x] = self.move_count
            self.current_pos = (x, y)
            self.move_count += 1
            self.possible_moves = self.get_possible_moves()
            return True
        return False

    def draw_board(self):
        DISPLAYSURF.fill(BACKGROUND_COLOR)

        # Draw the chess board
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                rect = pygame.Rect(x * SQUARE_SIZE + 20, y * SQUARE_SIZE + 20, SQUARE_SIZE, SQUARE_SIZE)
                color = LIGHT_TILE if (x + y) % 2 == 0 else DARK_TILE
                pygame.draw.rect(DISPLAYSURF, color, rect, border_radius=6)

                # Draw move numbers
                if self.board[y][x] != -1:
                    font = pygame.font.Font(None, 40)
                    text = font.render(str(self.board[y][x]), True, BLUE)
                    text_rect = text.get_rect(center=(rect.x + SQUARE_SIZE // 2, rect.y + SQUARE_SIZE // 2))
                    DISPLAYSURF.blit(text, text_rect)

        # Highlight possible moves
        for move in self.get_possible_moves():
            x, y = move
            highlight_rect = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight_rect.fill(HIGHLIGHT_COLOR)
            DISPLAYSURF.blit(highlight_rect, (x * SQUARE_SIZE + 20, y * SQUARE_SIZE + 20))

        # Draw the knight
        if self.current_pos and KNIGHT_IMAGE:
            knight_x, knight_y = self.current_pos
            knight_rect = KNIGHT_IMAGE.get_rect(center=(
                knight_x * SQUARE_SIZE + SQUARE_SIZE // 2 + 20,
                knight_y * SQUARE_SIZE + SQUARE_SIZE // 2 + 20))
            DISPLAYSURF.blit(KNIGHT_IMAGE, knight_rect)


def main():
    game = KnightsTour()
    clock = pygame.time.Clock()
    mode = None

    # Game instructions and mode selection
    print("Knight's Tour")
    print("1. Manual mode")
    print("2. AI mode")
    while mode not in ["1", "2"]:
        mode = input("Choose your mode (1 or 2): ")

    if mode == "2":
        print("AI Mode initialized...")
        game.solve_ai(0, 0)  # Start from the top-left corner
        print("AI completed the Knight's Tour!")

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and mode == "1":
                game.try_manual_move(pygame.mouse.get_pos())

        game.draw_board()
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
