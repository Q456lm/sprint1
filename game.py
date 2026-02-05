#!/usr/bin/env python3
"""
Echo of Terminal 7 — Pygame prototype.

This version is a simple top-down game where you control a scientist
moving between rooms in a space station. One puzzle (the Power Grid)
is implemented as a small mini-game; the other rooms are ready for
future puzzles.

Controls:
- Arrow keys or WASD: move
- E: interact (when near a console/door)
- ESC: quit current puzzle or close the game from the main view

Requirements:
- Python 3.8+
- pygame 2.x  (install with: pip install pygame)
"""

import sys
from typing import List, Dict, Optional

import pygame


# ------------------------------------------------------------
# Basic configuration
# ------------------------------------------------------------
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60

PLAYER_SPEED = 4
PLAYER_SIZE = 32

ROOM_BG_COLOR = (10, 10, 20)
HUB_BG_COLOR = (15, 15, 35)
TEXT_COLOR = (230, 230, 240)


class GameState:
    """Holds high-level game state flags."""

    def __init__(self) -> None:
        # Whether the initial power grid puzzle is solved
        self.power_restored = False
        # Whether the player has correctly solved the herd/cipher mystery
        self.herd_secret_known = False
        # Whether the player has completed the engineering/repair puzzle
        self.slip_repaired = False


class Player:
    """Simple rectangular 'scientist' you can move around."""

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.color = (180, 240, 255)

    def handle_input(self, keys) -> None:
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += PLAYER_SPEED
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += PLAYER_SPEED

        self.rect.x += dx
        self.rect.y += dy

        # Keep player inside the window
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)


class RoomHub:
    """
    Central hub room.

    From here you can walk up to the three doors which lead to:
    - Botany Wing
    - Server Room
    - Engineering Deck
    The right-hand console is the Power Grid puzzle console.
    """

    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font

        # Door hitboxes to other rooms
        self.doors = {
            "botany": pygame.Rect(80, 40, 120, 40),
            "server": pygame.Rect(SCREEN_WIDTH // 2 - 60, 40, 120, 40),
            "engineering": pygame.Rect(SCREEN_WIDTH - 200, 40, 120, 40),
        }

        # Power console on the right wall
        self.power_console = pygame.Rect(SCREEN_WIDTH - 140, SCREEN_HEIGHT // 2 - 25, 80, 50)

    def draw(self, surface: pygame.Surface, game_state: GameState) -> None:
        surface.fill(HUB_BG_COLOR)

        # Title
        title = self.font.render("Central Hub", True, TEXT_COLOR)
        surface.blit(title, (20, 10))

        # Instructions
        hint = self.font.render("Move with WASD/Arrows. Press E to interact.", True, TEXT_COLOR)
        surface.blit(hint, (20, SCREEN_HEIGHT - 30))

        # Draw door rectangles
        door_color = (90, 90, 130)
        for key, rect in self.doors.items():
            pygame.draw.rect(surface, door_color, rect, border_radius=4)
            label = self.font.render(key.capitalize(), True, TEXT_COLOR)
            label_pos = label.get_rect(center=rect.center)
            surface.blit(label, label_pos)

        # Draw power console
        console_color = (120, 100, 40) if not game_state.power_restored else (40, 130, 40)
        pygame.draw.rect(surface, console_color, self.power_console, border_radius=6)

        console_text = "Power Grid" if not game_state.power_restored else "Power: Restored"
        label = self.font.render(console_text, True, TEXT_COLOR)
        label_pos = label.get_rect(center=self.power_console.center)
        surface.blit(label, label_pos)

    def check_interaction(self, player: Player) -> Optional[str]:
        """
        Return an action string if the player is close enough to something.
        Possible values: 'botany', 'server', 'engineering', 'power_console', or None.
        """
        # Simple overlap check
        for name, rect in self.doors.items():
            if player.rect.colliderect(rect.inflate(10, 10)):
                return name

        if player.rect.colliderect(self.power_console.inflate(10, 10)):
            return "power_console"

        return None


class PowerGridPuzzle:
    """
    Mini-game version of the original fuse puzzle.

    Four colored buttons are shown on screen:
    - Blue, Yellow, Green, Red
    Click them in the correct order to restore power.
    """

    ORDER = ["blue", "yellow", "green", "red"]

    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.buttons: Dict[str, pygame.Rect] = {}
        self.sequence: List[str] = []
        self.resolved: bool = False
        self.failed_message: Optional[str] = None

        # Layout buttons at the bottom of the screen
        button_width = 120
        button_height = 60
        spacing = 20
        total_width = 4 * button_width + 3 * spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = SCREEN_HEIGHT - button_height - 60

        colors = {
            "blue": (50, 120, 230),
            "yellow": (220, 200, 60),
            "green": (60, 180, 90),
            "red": (210, 70, 70),
        }

        self.button_colors = colors
        for i, name in enumerate(self.ORDER):
            rect = pygame.Rect(start_x + i * (button_width + spacing), y, button_width, button_height)
            self.buttons[name] = rect

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.resolved:
            mouse_pos = event.pos
            for name, rect in self.buttons.items():
                if rect.collidepoint(mouse_pos):
                    self.sequence.append(name)
                    if len(self.sequence) == len(self.ORDER):
                        self.check_sequence()

    def check_sequence(self) -> None:
        if self.sequence == self.ORDER:
            self.resolved = True
            self.failed_message = None
        else:
            self.sequence.clear()
            self.failed_message = "Incorrect order. Try again."

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((5, 5, 18))

        # Title and instructions
        title = self.font.render("Power Grid Puzzle", True, TEXT_COLOR)
        surface.blit(title, (20, 20))

        instructions_lines = [
            'Click the fuses in order:',
            '"The sky comes before the sun, but the grass must never touch the blood.',
            'The sun is not last."',
        ]
        y = 60
        for line in instructions_lines:
            text_surf = self.font.render(line, True, TEXT_COLOR)
            surface.blit(text_surf, (20, y))
            y += 24

        # Draw buttons
        for name, rect in self.buttons.items():
            color = self.button_colors[name]
            pygame.draw.rect(surface, color, rect, border_radius=8)
            label = self.font.render(name.capitalize(), True, (0, 0, 0))
            label_pos = label.get_rect(center=rect.center)
            surface.blit(label, label_pos)

        # Draw the current selection as text
        seq_text = "Selected: " + " → ".join(s.capitalize() for s in self.sequence)
        seq_surf = self.font.render(seq_text, True, TEXT_COLOR)
        surface.blit(seq_surf, (20, SCREEN_HEIGHT - 40))

        if self.failed_message:
            msg = self.font.render(self.failed_message, True, (230, 180, 180))
            msg_pos = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            surface.blit(msg, msg_pos)

        if self.resolved:
            done = self.font.render("Power restored! Press ESC to return to the Hub.", True, (160, 230, 160))
            done_pos = done.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
            surface.blit(done, done_pos)


class ServerRoomPuzzle:
    """
    Server Room puzzle: decrypt the Captain's log using a Caesar cipher (shift 3).

    Encrypted text: "Wkhy duh lq wkh khug."
    Correct answer: "they are in the herd"
    """

    TARGET = "they are in the herd"

    def __init__(self, font: pygame.font.Font, game_state: GameState) -> None:
        self.font = font
        self.game_state = game_state
        self.input_text: str = ""
        self.solved: bool = False
        self.message: Optional[str] = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self.solved:
            return

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            normalized = self.input_text.strip().lower()
            if normalized == self.TARGET:
                self.solved = True
                self.game_state.herd_secret_known = True
                self.message = "Correct. \"They are in the herd.\""
            else:
                self.message = "Incorrect. Hint: shift each letter back by 3."
        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        else:
            ch = event.unicode
            if ch and ch.isprintable() and len(self.input_text) < 40:
                self.input_text += ch

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(ROOM_BG_COLOR)

        title = self.font.render("Server Room — Encrypted Log", True, TEXT_COLOR)
        surface.blit(title, (20, 20))

        enc = self.font.render('Encrypted: "Wkhy duh lq wkh khug."', True, TEXT_COLOR)
        surface.blit(enc, (20, 60))

        inst1 = self.font.render("Type the decrypted phrase (ENTER to submit, ESC to return):", True, TEXT_COLOR)
        surface.blit(inst1, (20, 100))

        box_rect = pygame.Rect(20, 140, SCREEN_WIDTH - 40, 40)
        pygame.draw.rect(surface, (40, 40, 70), box_rect, border_radius=6)
        txt_surf = self.font.render(self.input_text, True, TEXT_COLOR)
        surface.blit(txt_surf, (box_rect.x + 10, box_rect.y + 10))

        if self.message:
            msg_surf = self.font.render(self.message, True, TEXT_COLOR)
            surface.blit(msg_surf, (20, 200))

        if self.solved:
            extra = self.font.render("The Herd was the botany experiment, not the crew.", True, TEXT_COLOR)
            surface.blit(extra, (20, 230))
            note = self.font.render("Press ESC to return to the Hub.", True, TEXT_COLOR)
            surface.blit(note, (20, 260))


class BotanyRoom:
    """
    Botany Wing puzzle: identify which tank is \"The Herd\" — the emergent, learning organism.

    Click one of three tanks (A, B, C). Only C shows predictive, learning behavior.
    """

    def __init__(self, font: pygame.font.Font, game_state: GameState) -> None:
        self.font = font
        self.game_state = game_state
        self.tanks: Dict[str, pygame.Rect] = {}
        self.solved: bool = False
        self.message: Optional[str] = None

        width = 120
        height = 160
        spacing = 60
        total_width = 3 * width + 2 * spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = SCREEN_HEIGHT // 2 - height // 2

        labels = ["A", "B", "C"]
        for i, name in enumerate(labels):
            rect = pygame.Rect(start_x + i * (width + spacing), y, width, height)
            self.tanks[name] = rect

        self.correct_tank = "C"

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.solved:
            pos = event.pos
            for name, rect in self.tanks.items():
                if rect.collidepoint(pos):
                    if name == self.correct_tank:
                        self.solved = True
                        self.message = "Tank C anticipates sensor sweeps — The Herd has learned."
                        self.game_state.herd_secret_known = True
                    else:
                        self.message = f"Tank {name} reacts, but only in simple patterns. Try another."

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(ROOM_BG_COLOR)

        title = self.font.render("Botany Wing — Project: The Herd", True, TEXT_COLOR)
        surface.blit(title, (20, 20))

        lines = [
            "Three specimen tanks are wired to motion sensors:",
            "A: Cells swirl at random.",
            "B: Cells mirror your movements after a delay.",
            "C: Cells move in patterns that predict the sensor's sweep.",
            "Click the tank that contains The Herd.",
        ]
        y = 60
        for line in lines:
            surf = self.font.render(line, True, TEXT_COLOR)
            surface.blit(surf, (20, y))
            y += 24

        # Draw tanks
        for name, rect in self.tanks.items():
            pygame.draw.rect(surface, (40, 100, 60), rect, border_radius=6)
            label = self.font.render(name, True, TEXT_COLOR)
            label_pos = label.get_rect(center=(rect.centerx, rect.top - 15))
            surface.blit(label, label_pos)

        if self.message:
            msg = self.font.render(self.message, True, TEXT_COLOR)
            surface.blit(msg, (20, SCREEN_HEIGHT - 60))

        if self.solved:
            hint = self.font.render("The Herd learned. Press ESC to return to the Hub.", True, TEXT_COLOR)
            surface.blit(hint, (20, SCREEN_HEIGHT - 30))


class EngineeringRoom:
    """
    Engineering Deck puzzle: set three power couplers into a stable pattern.

    Click the three toggles until they match the correct up/down pattern.
    """

    def __init__(self, font: pygame.font.Font, game_state: GameState) -> None:
        self.font = font
        self.game_state = game_state
        self.toggles: List[bool] = [False, False, False]
        self.rects: List[pygame.Rect] = []
        self.solved: bool = False

        width = 80
        height = 40
        spacing = 40
        total_width = 3 * width + 2 * spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = SCREEN_HEIGHT // 2

        for i in range(3):
            rect = pygame.Rect(start_x + i * (width + spacing), y, width, height)
            self.rects.append(rect)

        # Target pattern: Up, Down, Up
        self.target_pattern = [True, False, True]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.solved:
            pos = event.pos
            for idx, rect in enumerate(self.rects):
                if rect.collidepoint(pos):
                    self.toggles[idx] = not self.toggles[idx]
                    break

            if self.toggles == self.target_pattern:
                self.solved = True
                self.game_state.slip_repaired = True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(ROOM_BG_COLOR)

        title = self.font.render("Engineering Deck — Slip-Drive Couplers", True, TEXT_COLOR)
        surface.blit(title, (20, 20))

        lines = [
            "Radiation alarms wail as you adjust three power couplers.",
            "Only one pattern keeps the Slip-Drive stable:",
            "The outer couplers must match each other, but the center must remain opposite.",
            "Click the couplers to toggle them Up/Down.",
        ]
        y = 60
        for line in lines:
            surf = self.font.render(line, True, TEXT_COLOR)
            surface.blit(surf, (20, y))
            y += 24

        # Draw toggles
        for idx, rect in enumerate(self.rects):
            is_up = self.toggles[idx]
            color = (80, 180, 120) if is_up else (120, 90, 60)
            pygame.draw.rect(surface, color, rect, border_radius=6)
            label_text = "Up" if is_up else "Down"
            label = self.font.render(label_text, True, TEXT_COLOR)
            label_pos = label.get_rect(center=rect.center)
            surface.blit(label, label_pos)

        status = "Stable pattern achieved. Slip-Drive ready." if self.solved else "Pattern unstable."
        status_surf = self.font.render(status, True, TEXT_COLOR)
        surface.blit(status_surf, (20, SCREEN_HEIGHT - 60))

        if self.solved:
            hint = self.font.render("Press ESC to return to the Hub.", True, TEXT_COLOR)
            surface.blit(hint, (20, SCREEN_HEIGHT - 30))


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Echo of Terminal 7 — Pygame Prototype")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Basic font; we keep it simple
    font = pygame.font.SysFont("consolas", 20)

    game_state = GameState()
    player = Player(SCREEN_WIDTH // 2 - PLAYER_SIZE // 2, SCREEN_HEIGHT - PLAYER_SIZE - 40)
    hub = RoomHub(font)
    power_puzzle = PowerGridPuzzle(font)
    server_puzzle = ServerRoomPuzzle(font, game_state)
    botany_room = BotanyRoom(font, game_state)
    engineering_room = EngineeringRoom(font, game_state)

    mode: str = "hub"  # 'hub', 'power_puzzle', 'server', 'botany', 'engineering'

    running = True
    while running:
        dt = clock.tick(FPS)  # frame limiter; dt currently unused but kept for future use

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if mode == "hub":
                    running = False
                else:
                    # Escape out of the current room/puzzle back to hub
                    mode = "hub"
            else:
                if mode == "power_puzzle":
                    power_puzzle.handle_event(event)
                elif mode == "server":
                    server_puzzle.handle_event(event)
                elif mode == "botany":
                    botany_room.handle_event(event)
                elif mode == "engineering":
                    engineering_room.handle_event(event)

        keys = pygame.key.get_pressed()

        if mode == "hub":
            # Movement only in hub mode
            player.handle_input(keys)

            # Interactions
            if keys[pygame.K_e]:
                action = hub.check_interaction(player)
                if action == "power_console":
                    mode = "power_puzzle"
                elif action in {"botany", "server", "engineering"}:
                    if action == "botany":
                        mode = "botany"
                    elif action == "server":
                        mode = "server"
                    elif action == "engineering":
                        mode = "engineering"

            # Check if power puzzle has been solved
            if power_puzzle.resolved:
                game_state.power_restored = True

            # Draw hub
            hub.draw(screen, game_state)
            player.draw(screen)
        elif mode == "power_puzzle":
            power_puzzle.draw(screen)
        elif mode == "server":
            server_puzzle.draw(screen)
        elif mode == "botany":
            botany_room.draw(screen)
        elif mode == "engineering":
            engineering_room.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()