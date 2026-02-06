#!/usr/bin/env python3
"""
Echo of Terminal 7 — The Herd Edition.
Features:
- Intro Story Screen.
- Neon aesthetics, CRT effects, Smooth Physics.
- ENDING: "The Herd" Swarm Battle (Multiple Enemies).
- Fully implemented Puzzles.
"""

import sys
import math
import random
from typing import List, Dict, Optional, Tuple

import pygame

# ------------------------------------------------------------
# Configuration & Esthetics
# ------------------------------------------------------------
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60

# Physics
PLAYER_ACCEL = 0.8
PLAYER_FRICTION = 0.85
MAX_SPEED = 6
PROJECTILE_SPEED = 14

# Colors (Neon Palette)
C_BG_DEEP = (5, 5, 12)
C_GRID = (20, 30, 45)
C_NEON_CYAN = (0, 255, 240)
C_NEON_BLUE = (0, 100, 255)
C_NEON_GREEN = (50, 255, 50)
C_NEON_RED = (255, 50, 50)
C_BLOOD_RED = (130, 0, 0)
C_NEON_YELLOW = (255, 220, 0)
C_WHITE = (220, 240, 255)
C_SHADOW = (0, 0, 0)

# ------------------------------------------------------------
# Graphical Helpers
# ------------------------------------------------------------

def draw_glow_rect(surface, color, rect, glow_radius=10, border_radius=4):
    """Draws a rectangle with a glowing halo using additive blending."""
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)
    pygame.draw.rect(surface, (255, 255, 255), rect, 1, border_radius=border_radius)
    
    glow_surf = pygame.Surface((rect.width + glow_radius*4, rect.height + glow_radius*4), pygame.SRCALPHA)
    r, g, b = color
    pygame.draw.rect(glow_surf, (r, g, b, 50), 
                     (glow_radius, glow_radius, rect.width + glow_radius*2, rect.height + glow_radius*2), 
                     border_radius=border_radius+glow_radius)
    pygame.draw.rect(glow_surf, (r, g, b, 100), 
                     (glow_radius*2, glow_radius*2, rect.width, rect.height), 
                     border_radius=border_radius)
    
    surface.blit(glow_surf, (rect.x - glow_radius*2, rect.y - glow_radius*2), special_flags=pygame.BLEND_ADD)

def draw_text_shadow(surface, font, text, color, center, shadow_offset=(2,2)):
    shad = font.render(text, True, C_SHADOW)
    rect = shad.get_rect(center=(center[0] + shadow_offset[0], center[1] + shadow_offset[1]))
    surface.blit(shad, rect)
    
    fore = font.render(text, True, color)
    rect = fore.get_rect(center=center)
    surface.blit(fore, rect)

class Particle:
    def __init__(self, x, y, color, speed=2, life_scale=1.0):
        self.x = x
        self.y = y
        self.vx = random.uniform(-speed, speed)
        self.vy = random.uniform(-speed, speed)
        self.life = int(random.randint(20, 60) * life_scale)
        self.color = color
        self.size = random.randint(1, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.05)

    def draw(self, surface):
        if self.life > 0:
            alpha = min(255, self.life * 5)
            surf = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            surface.blit(surf, (self.x, self.y), special_flags=pygame.BLEND_ADD)

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def spawn(self, x, y, color, count=10, speed=2, life_scale=1.0):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, speed, life_scale))

    def update_and_draw(self, surface):
        for p in self.particles[:]:
            p.update()
            p.draw(surface)
            if p.life <= 0:
                self.particles.remove(p)

# ------------------------------------------------------------
# Intro / Lore Screen
# ------------------------------------------------------------

class IntroScreen:
    def __init__(self, font: pygame.font.Font):
        self.font = font
        self.lines = [
            "ESTABLISHING CONNECTION...",
            "YEAR: 2149 // SECTOR: DEEP VOID",
            "LOCATION: TERMINAL 7",
            "",
            "Three weeks ago, the Slip-Drive stability test failed.",
            "The radiation didn't kill the crew. It changed them.",
            "Project 'THE HERD' has breached containment.",
            "The station is silent. The air is toxic.",
            "",
            "MISSION OBJECTIVES:",
            "1. RESTORE POWER GRID",
            "2. DECRYPT SERVER LOGS",
            "3. STABILIZE DRIVE COUPLERS",
            "4. ELIMINATE THE HERD",
            "",
            "[ PRESS ANY KEY TO INITIATE SEQUENCE ]"
        ]
        self.current_line_idx = 0
        self.char_idx = 0
        self.timer = 0
        self.speed = 2
        self.finished = False

    def update(self):
        if not self.finished:
            self.timer += 1
            if self.timer >= self.speed:
                self.timer = 0
                self.char_idx += 1
                current_text = self.lines[self.current_line_idx]
                if self.char_idx > len(current_text):
                    self.current_line_idx += 1
                    self.char_idx = 0
                    if self.current_line_idx >= len(self.lines):
                        self.finished = True

    def draw(self, surface: pygame.Surface):
        surface.fill((0, 5, 10))
        y = 60
        for i in range(min(self.current_line_idx + 1, len(self.lines))):
            line = self.lines[i]
            if i == self.current_line_idx and not self.finished:
                draw_text = line[:self.char_idx]
                if (pygame.time.get_ticks() // 200) % 2 == 0:
                    draw_text += "_"
            else:
                draw_text = line
            
            col = C_NEON_GREEN
            if "MISSION OBJECTIVES" in line: col = C_NEON_YELLOW
            if "PRESS ANY KEY" in line: 
                col = C_NEON_CYAN
                if self.finished and (pygame.time.get_ticks() // 500) % 2 == 0:
                    draw_text = "" 

            txt_surf = self.font.render(draw_text, True, col)
            surface.blit(txt_surf, (80, y))
            y += 28

# ------------------------------------------------------------
# Combat Classes
# ------------------------------------------------------------

class Projectile:
    def __init__(self, x, y, angle_rad):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(math.cos(angle_rad), math.sin(angle_rad)) * PROJECTILE_SPEED
        self.radius = 4
        self.active = True

    def update(self):
        self.pos += self.vel
        if (self.pos.x < 0 or self.pos.x > SCREEN_WIDTH or 
            self.pos.y < 0 or self.pos.y > SCREEN_HEIGHT):
            self.active = False

    def draw(self, surface):
        end_pos = self.pos - self.vel * 0.5
        pygame.draw.line(surface, C_NEON_CYAN, self.pos, end_pos, 3)
        pygame.draw.circle(surface, C_WHITE, (int(self.pos.x), int(self.pos.y)), self.radius)

class HerdMember:
    """A single monster in the swarm."""
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.hp = 4 # Takes 2 shots to kill (projectiles do 2 damage usually, let's say)
        self.radius = 18
        # Random speed to separate the herd
        self.speed = random.uniform(1.8, 3.2) 
        self.wobble_phase = random.uniform(0, 6.28)
        self.eyes_offset = []
        # Create random eyes
        for _ in range(random.randint(2, 5)):
            self.eyes_offset.append((random.randint(-8, 8), random.randint(-8, 8)))

    def update(self, player_pos):
        # Chase logic
        direction = player_pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
        
        # Add some wobble
        self.wobble_phase += 0.2
        wobble = pygame.math.Vector2(math.sin(self.wobble_phase), math.cos(self.wobble_phase)) * 0.5
        
        self.pos += (direction * self.speed) + wobble

    def draw(self, surface):
        cx, cy = int(self.pos.x), int(self.pos.y)
        
        # Draw Spikes / Glitch body
        # We draw a polygon that shifts shape slightly every frame to look scary
        points = []
        num_points = 8
        for i in range(num_points):
            angle = (i / num_points) * 6.28 + self.wobble_phase * 0.1
            # Spiky radius
            r = self.radius + random.randint(-5, 8)
            px = cx + math.cos(angle) * r
            py = cy + math.sin(angle) * r
            points.append((px, py))
        
        pygame.draw.polygon(surface, C_BLOOD_RED, points)
        pygame.draw.polygon(surface, C_NEON_RED, points, 2)
        
        # Draw Glowing Eyes
        for off in self.eyes_offset:
            pygame.draw.circle(surface, C_NEON_YELLOW, (cx + off[0], cy + off[1]), 2)

# ------------------------------------------------------------
# Game Classes
# ------------------------------------------------------------

class GameState:
    def __init__(self) -> None:
        self.power_restored = False
        self.herd_secret_known = False
        self.slip_repaired = False
        self.boss_unlocked = False
        self.particles = ParticleSystem()
    
    def check_all_puzzles(self):
        if self.power_restored and self.herd_secret_known and self.slip_repaired:
            self.boss_unlocked = True

class Player:
    def __init__(self, x: int, y: int) -> None:
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.rect = pygame.Rect(x, y, 32, 32)
        self.angle = 0
        self.hp = 5
        self.invuln_timer = 0

    def handle_input(self, keys) -> None:
        accel = pygame.math.Vector2(0, 0)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: accel.x -= PLAYER_ACCEL
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: accel.x += PLAYER_ACCEL
        if keys[pygame.K_w] or keys[pygame.K_UP]: accel.y -= PLAYER_ACCEL
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: accel.y += PLAYER_ACCEL

        self.vel += accel
        self.vel *= PLAYER_FRICTION
        if self.vel.length() > MAX_SPEED: self.vel.scale_to_length(MAX_SPEED)
        self.pos += self.vel
        self.pos.x = max(0, min(self.pos.x, SCREEN_WIDTH - 32))
        self.pos.y = max(0, min(self.pos.y, SCREEN_HEIGHT - 32))
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface: pygame.Surface) -> None:
        if self.invuln_timer > 0:
            self.invuln_timer -= 1
            if (self.invuln_timer // 5) % 2 == 0: return

        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.pos.x
        dy = mouse_pos[1] - self.pos.y
        
        center = self.rect.center
        pygame.draw.circle(surface, C_NEON_CYAN, center, 12)
        pygame.draw.circle(surface, C_WHITE, center, 6)
        
        # Gun
        barrel_end = (center[0] + (dx/math.sqrt(dx**2 + dy**2+0.1))*20, 
                      center[1] + (dy/math.sqrt(dx**2 + dy**2+0.1))*20)
        pygame.draw.line(surface, C_NEON_CYAN, center, barrel_end, 4)

class RoomHub:
    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.doors = {
            "botany": pygame.Rect(80, 40, 120, 10),
            "server": pygame.Rect(SCREEN_WIDTH // 2 - 60, 40, 120, 10),
            "engineering": pygame.Rect(SCREEN_WIDTH - 200, 40, 120, 10),
        }
        self.boss_door = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 60, 200, 20)
        self.power_console = pygame.Rect(SCREEN_WIDTH - 140, SCREEN_HEIGHT // 2 - 25, 80, 50)
        self.grid_offset = 0
        self.alert_blink = 0

    def draw_bg_grid(self, surface, alert_mode=False):
        self.grid_offset = (self.grid_offset + 0.5) % 40
        line_col = C_GRID
        if alert_mode:
            red_val = 20 + int(math.sin(pygame.time.get_ticks() * 0.01) * 20)
            line_col = (red_val + 20, 0, 0)
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(surface, line_col, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40):
            draw_y = (y + self.grid_offset) % SCREEN_HEIGHT
            line_surf = pygame.Surface((SCREEN_WIDTH, 1), pygame.SRCALPHA)
            line_surf.fill((*line_col, 150))
            surface.blit(line_surf, (0, draw_y))

    def draw(self, surface: pygame.Surface, game_state: GameState, player: Player) -> None:
        surface.fill(C_BG_DEEP)
        self.draw_bg_grid(surface, alert_mode=game_state.boss_unlocked)

        for key, rect in self.doors.items():
            pygame.draw.rect(surface, C_NEON_BLUE, rect)
            draw_text_shadow(surface, self.font, key.upper(), C_WHITE, (rect.centerx, rect.bottom + 40))

        if game_state.boss_unlocked:
            self.alert_blink += 1
            blink_col = C_NEON_RED if (self.alert_blink // 30) % 2 == 0 else (100, 0, 0)
            draw_glow_rect(surface, blink_col, self.boss_door, glow_radius=15)
            draw_text_shadow(surface, self.font, "!!! AIRLOCK OPEN !!!", C_NEON_RED, (self.boss_door.centerx, self.boss_door.top - 30))

        # Power Console
        console_color = C_NEON_YELLOW if not game_state.power_restored else C_NEON_GREEN
        draw_glow_rect(surface, console_color, self.power_console, glow_radius=5)
        status = "PWR: OFF" if not game_state.power_restored else "PWR: ON"
        draw_text_shadow(surface, self.font, status, console_color, (self.power_console.centerx, self.power_console.top - 20))

        interact = self.check_interaction(player, game_state)
        if interact:
            hint_text = f"[E] ENTER {interact.upper()}"
            rect = player.rect
            draw_text_shadow(surface, self.font, hint_text, C_NEON_CYAN, (rect.centerx, rect.top - 20))

    def check_interaction(self, player: Player, game_state: GameState) -> Optional[str]:
        for name, rect in self.doors.items():
            if player.rect.colliderect(rect.inflate(20, 100)): return name
        if game_state.boss_unlocked and player.rect.colliderect(self.boss_door.inflate(20, 60)): return "boss_room"
        if player.rect.colliderect(self.power_console.inflate(20, 20)): return "power_console"
        return None

# ------------------------------------------------------------
# Puzzles (Enhanced Botany)
# ------------------------------------------------------------

class PowerGridPuzzle:
    ORDER = ["blue", "yellow", "green", "red"]
    def __init__(self, font, particles) -> None:
        self.font = font
        self.particles = particles
        self.buttons = {}
        self.sequence = []
        self.resolved = False
        self.failed_timer = 0
        self.colors_map = {"blue": C_NEON_BLUE, "yellow": C_NEON_YELLOW, "green": C_NEON_GREEN, "red": C_NEON_RED}
        start_x = (SCREEN_WIDTH - (4 * 140)) // 2 + 20
        for i, name in enumerate(self.ORDER):
            self.buttons[name] = pygame.Rect(start_x + i * 140, SCREEN_HEIGHT - 180, 100, 100)

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.resolved and self.failed_timer == 0:
            for name, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    self.sequence.append(name)
                    self.particles.spawn(event.pos[0], event.pos[1], self.colors_map[name])
                    if len(self.sequence) == len(self.ORDER):
                        if self.sequence == self.ORDER: self.resolved = True
                        else: self.failed_timer = 60

    def draw(self, surface) -> None:
        surface.fill((10, 5, 5))
        draw_text_shadow(surface, self.font, "POWER GRID CALIBRATION", C_NEON_CYAN, (SCREEN_WIDTH//2, 40))
        riddle = ['"The sky comes before the sun...', '...but the grass must never touch the blood.', 'The sun is not last."']
        for i, line in enumerate(riddle):
            draw_text_shadow(surface, self.font, line, C_WHITE, (SCREEN_WIDTH//2, 90 + i*30))
        for name, rect in self.buttons.items():
            color = self.colors_map[name]
            is_active = name in self.sequence
            draw_color = color if is_active or self.resolved else (color[0]//3, color[1]//3, color[2]//3)
            draw_glow_rect(surface, draw_color, rect, glow_radius=15 if is_active else 2)
        
        if self.resolved:
            draw_text_shadow(surface, self.font, "SYSTEM RESTORED", C_NEON_GREEN, (SCREEN_WIDTH//2, SCREEN_HEIGHT - 40))
        elif self.failed_timer > 0:
            self.failed_timer -= 1
            draw_text_shadow(surface, self.font, "ERROR - RESETTING", C_NEON_RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT - 40))
            if self.failed_timer == 1: self.sequence.clear()

class ServerRoomPuzzle:
    TARGET = "they are in the herd"
    def __init__(self, font, game_state) -> None:
        self.font = font
        self.game_state = game_state
        self.input_text = ""
        self.solved = False
        self.cursor_blink = 0

    def handle_event(self, event) -> None:
        if self.solved: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_text.strip().lower() == self.TARGET:
                    self.solved = True
                    self.game_state.herd_secret_known = True
            elif event.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
            elif len(self.input_text) < 30 and event.unicode.isprintable(): self.input_text += event.unicode

    def draw(self, surface) -> None:
        surface.fill((0, 10, 0))
        term_rect = pygame.Rect(100, 80, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 160)
        pygame.draw.rect(surface, (0, 20, 0), term_rect)
        pygame.draw.rect(surface, C_NEON_GREEN, term_rect, 2)
        lines = ["ADMIN_CONSOLE_V7.2", "LOG_ENCRYPTED [ROT-3]", 'RAW: "Wkhy duh lq wkh khug."', ""]
        y = 100
        for l in lines:
            surface.blit(self.font.render(l, True, C_NEON_GREEN), (120, y))
            y += 30
        self.cursor_blink = (self.cursor_blink + 1) % 60
        cursor = "_" if self.cursor_blink < 30 else ""
        surface.blit(self.font.render(f"> {self.input_text}{cursor}", True, C_WHITE if not self.solved else C_NEON_CYAN), (120, y))
        if self.solved:
            draw_text_shadow(surface, self.font, "ACCESS GRANTED. SUBJECT: 'THE HERD' IS SENTIENT.", C_NEON_GREEN, (SCREEN_WIDTH//2, y + 80))

class BotanyRoom:
    """Revised Puzzle: Particle Simulation."""
    def __init__(self, font, game_state, particles) -> None:
        self.font = font
        self.game_state = game_state
        self.particles = particles
        self.tanks = {"A": pygame.Rect(0,0,140,220), "B": pygame.Rect(0,0,140,220), "C": pygame.Rect(0,0,140,220)}
        
        spacing = 250
        start_x = (SCREEN_WIDTH - (3*140 + 2*50)) // 2
        for i, k in enumerate(["A", "B", "C"]):
            self.tanks[k].topleft = (start_x + i*spacing, SCREEN_HEIGHT//2 - 110)
        
        self.solved = False
        self.message = ""
        self.sim_particles = {
            "A": [[random.randint(0, 140), random.randint(0, 220), random.uniform(-2,2), random.uniform(-2,2)] for _ in range(20)],
            "B": [[random.randint(0, 140), random.randint(0, 220), 0, 0] for _ in range(20)],
            "C": [[random.randint(0, 140), random.randint(0, 220), i] for i in range(20)]
        }

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and not self.solved:
            for name, rect in self.tanks.items():
                if rect.collidepoint(event.pos):
                    if name == "C":
                        self.solved = True
                        self.game_state.herd_secret_known = True
                        self.message = "MATCH CONFIRMED: ORGANIZED INTELLIGENCE DETECTED."
                        self.particles.spawn(rect.centerx, rect.centery, C_NEON_GREEN, 30)
                    else:
                        self.message = f"SPECIMEN {name}: NEGATIVE. NO HIGHER THOUGHT PATTERNS."
                        self.particles.spawn(rect.centerx, rect.centery, C_NEON_RED, 10)

    def draw(self, surface) -> None:
        surface.fill((5, 20, 10))
        draw_text_shadow(surface, self.font, "BIO-LAB: IDENTIFY INTELLIGENT LIFE", C_NEON_GREEN, (SCREEN_WIDTH//2, 40))
        draw_text_shadow(surface, self.font, "Analyze movement patterns. Look for Order.", C_WHITE, (SCREEN_WIDTH//2, 70))

        mouse_pos = pygame.mouse.get_pos()
        time_t = pygame.time.get_ticks() * 0.005

        for name, rect in self.tanks.items():
            color = C_NEON_GREEN if name == "C" and self.solved else C_NEON_CYAN
            pygame.draw.rect(surface, (0, 30, 20), rect, border_radius=10)
            pygame.draw.rect(surface, color, rect, 2, border_radius=10)
            
            plist = self.sim_particles[name]
            for i, p in enumerate(plist):
                px, py = 0, 0
                if name == "A": 
                    p[0] += p[2]
                    p[1] += p[3]
                    if p[0] < 0 or p[0] > 140: p[2] *= -1
                    if p[1] < 0 or p[1] > 220: p[3] *= -1
                    px, py = rect.x + p[0], rect.y + p[1]
                elif name == "B": 
                    target_x = max(0, min(140, mouse_pos[0] - rect.x))
                    target_y = max(0, min(220, mouse_pos[1] - rect.y))
                    dx = target_x - p[0]
                    dy = target_y - p[1]
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        p[0] += (dx/dist) * 4
                        p[1] += (dy/dist) * 4
                    p[0] += random.uniform(-2, 2)
                    p[1] += random.uniform(-2, 2)
                    px, py = rect.x + p[0], rect.y + p[1]
                elif name == "C": 
                    center_x, center_y = 70, 110
                    radius = 40
                    angle = time_t + (p[2] * (6.28 / 20))
                    p[0] = center_x + math.cos(angle) * radius
                    p[1] = center_y + math.sin(angle) * radius
                    px, py = rect.x + p[0], rect.y + p[1]
                pygame.draw.circle(surface, C_NEON_GREEN if name == "C" else (100, 255, 100), (int(px), int(py)), 3)

            draw_text_shadow(surface, self.font, name, color, (rect.centerx, rect.top - 20))
        
        if self.message:
            draw_text_shadow(surface, self.font, self.message, C_NEON_GREEN if self.solved else C_NEON_RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))

class EngineeringRoom:
    def __init__(self, font, game_state) -> None:
        self.font = font
        self.game_state = game_state
        self.toggles = [False, False, False]
        self.rects = []
        start_x = (SCREEN_WIDTH - (3 * 100 + 2 * 60)) // 2
        for i in range(3):
            self.rects.append(pygame.Rect(start_x + i * 160, SCREEN_HEIGHT // 2 - 60, 100, 120))

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and not self.game_state.slip_repaired:
            for idx, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos):
                    self.toggles[idx] = not self.toggles[idx]
                    if self.toggles == [True, False, True]:
                        self.game_state.slip_repaired = True

    def draw(self, surface) -> None:
        surface.fill((20, 10, 10))
        draw_text_shadow(surface, self.font, "ENGINEERING: COUPLERS (UP, DOWN, UP)", C_NEON_RED, (SCREEN_WIDTH//2, 40))
        for idx, rect in enumerate(self.rects):
            is_up = self.toggles[idx]
            color = C_NEON_CYAN if is_up else C_NEON_RED
            draw_glow_rect(surface, color, rect, glow_radius=5)
            draw_text_shadow(surface, self.font, "UP" if is_up else "DN", C_WHITE, (rect.centerx, rect.bottom + 20))
        if self.game_state.slip_repaired:
            draw_text_shadow(surface, self.font, "DRIVE STABLE", C_NEON_GREEN, (SCREEN_WIDTH//2, SCREEN_HEIGHT - 60))

class BossRoom:
    def __init__(self, font: pygame.font.Font, game_state: GameState, particles: ParticleSystem):
        self.font = font
        self.game_state = game_state
        self.particles = particles
        self.swarm: List[HerdMember] = []
        self.projectiles: List[Projectile] = []
        self.state = "intro" 
        self.intro_timer = 120

    def reset(self, player: Player):
        self.swarm = []
        # Spawn the Swarm (15 monsters)
        for _ in range(15):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(50, 200)
            self.swarm.append(HerdMember(x, y))
            
        self.projectiles = []
        self.state = "intro"
        self.intro_timer = 180
        player.pos = pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100)
        player.hp = 5

    def handle_event(self, event: pygame.event.Event, player: Player):
        if self.state == "fight":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                dx = mx - player.pos.x
                dy = my - player.pos.y
                angle = math.atan2(dy, dx)
                self.projectiles.append(Projectile(player.pos.x + 16, player.pos.y + 16, angle))
                self.particles.spawn(player.pos.x, player.pos.y, C_NEON_CYAN, count=5, speed=1)

    def update(self, player: Player):
        if self.state == "intro":
            self.intro_timer -= 1
            if self.intro_timer <= 0: self.state = "fight"
        
        if self.state == "fight":
            # Update Swarm
            for monster in self.swarm:
                monster.update(player.pos)
                
                # Player Hit Logic
                monster_rect = pygame.Rect(monster.pos.x - monster.radius, monster.pos.y - monster.radius, 
                                           monster.radius*2, monster.radius*2)
                if player.invuln_timer == 0 and monster_rect.colliderect(player.rect):
                    player.hp -= 1
                    player.invuln_timer = 60
                    self.particles.spawn(player.pos.x, player.pos.y, C_NEON_RED, count=20, speed=4)
                    if player.hp <= 0: self.state = "game_over"

            # Projectile Logic
            for p in self.projectiles:
                p.update()
                hit = False
                for monster in self.swarm:
                    dist = p.pos.distance_to(monster.pos)
                    if dist < monster.radius + 5:
                        monster.hp -= 2 # 2 damage per shot
                        self.particles.spawn(monster.pos.x, monster.pos.y, C_BLOOD_RED, count=5)
                        hit = True
                        break # One bullet hits one monster
                if hit:
                    p.active = False
            
            # Remove Dead Monsters and Projectiles
            dead_monsters = [m for m in self.swarm if m.hp <= 0]
            for m in dead_monsters:
                self.particles.spawn(m.pos.x, m.pos.y, C_NEON_RED, count=15, speed=3)
            
            self.swarm = [m for m in self.swarm if m.hp > 0]
            self.projectiles = [p for p in self.projectiles if p.active]

            # Win Condition
            if len(self.swarm) == 0:
                self.state = "win"

    def draw(self, surface: pygame.Surface, player: Player):
        surface.fill((20, 0, 0))
        t = pygame.time.get_ticks() * 0.05
        for i in range(0, SCREEN_WIDTH + 100, 100):
            x = (i + t) % (SCREEN_WIDTH + 100) - 50
            pygame.draw.line(surface, (50, 0, 0), (x, 0), (x, SCREEN_HEIGHT))

        for m in self.swarm: m.draw(surface)
        for p in self.projectiles: p.draw(surface)
        player.draw(surface)

        if self.state == "intro":
            draw_text_shadow(surface, self.font, "WARNING: CONTAINMENT FAILURE", C_NEON_RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            draw_text_shadow(surface, self.font, "THE HERD APPROACHES", C_WHITE, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        elif self.state == "game_over":
            draw_text_shadow(surface, self.font, "STATUS: CONSUMED BY THE SWARM", C_NEON_RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            draw_text_shadow(surface, self.font, "PRESS ESC TO RETRY", C_WHITE, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        elif self.state == "win":
            draw_text_shadow(surface, self.font, "ALL ENTITIES ELIMINATED", C_NEON_GREEN, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            draw_text_shadow(surface, self.font, "TERMINAL SECURED.", C_WHITE, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))

        if self.state == "fight":
            hp_text = f"INTEGRITY: {player.hp * 20}%"
            col = C_NEON_GREEN if player.hp > 2 else C_NEON_RED
            draw_text_shadow(surface, self.font, hp_text, col, (100, SCREEN_HEIGHT - 30))
            
            # Enemy Counter
            count_text = f"ENTITIES: {len(self.swarm)}"
            draw_text_shadow(surface, self.font, count_text, C_NEON_RED, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 30))

# ------------------------------------------------------------
# Main Loop
# ------------------------------------------------------------

def draw_crt_overlay(surface):
    for y in range(0, SCREEN_HEIGHT, 4):
        pygame.draw.line(surface, (0, 0, 0, 100), (0, y), (SCREEN_WIDTH, y))
    vig = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(vig, (0,0,0,100), (0,0,SCREEN_WIDTH, SCREEN_HEIGHT), 20)
    surface.blit(vig, (0,0))

def main() -> None:
    pygame.init()
    pygame.display.set_caption("Echo of Terminal 7 — The Herd Edition")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18, bold=True)
    mono_font = pygame.font.SysFont("consolas", 20) 

    game_state = GameState()
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    
    # Screens
    intro_screen = IntroScreen(mono_font)
    hub = RoomHub(font)
    
    # Puzzles
    power_puzzle = PowerGridPuzzle(font, game_state.particles)
    server_puzzle = ServerRoomPuzzle(font, game_state)
    botany_room = BotanyRoom(font, game_state, game_state.particles)
    engineering_room = EngineeringRoom(font, game_state)
    boss_room = BossRoom(font, game_state, game_state.particles)

    mode = "intro" 
    running = True
    canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    while running:
        canvas.fill(C_BG_DEEP)
        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        for event in events:
            if event.type == pygame.QUIT: running = False
            
            # Global Key Handling
            elif mode == "intro":
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    mode = "hub" 
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if mode == "hub": running = False
                elif mode == "boss_room" and boss_room.state == "game_over":
                    boss_room.reset(player)
                else: 
                    if mode != "boss_room": game_state.check_all_puzzles()
                    mode = "hub"
            else:
                if mode == "power_puzzle": power_puzzle.handle_event(event)
                elif mode == "server": server_puzzle.handle_event(event)
                elif mode == "botany": botany_room.handle_event(event)
                elif mode == "engineering": engineering_room.handle_event(event)
                elif mode == "boss_room": boss_room.handle_event(event, player)

        if mode == "intro":
            intro_screen.update()
            intro_screen.draw(canvas)

        elif mode == "hub":
            player.handle_input(keys)
            if power_puzzle.resolved: game_state.power_restored = True
            game_state.check_all_puzzles()

            if keys[pygame.K_e]:
                action = hub.check_interaction(player, game_state)
                if action == "power_console": mode = "power_puzzle"
                elif action == "botany": mode = "botany"
                elif action == "server": mode = "server"
                elif action == "engineering": mode = "engineering"
                elif action == "boss_room":
                    mode = "boss_room"
                    boss_room.reset(player)

            hub.draw(canvas, game_state, player)
            player.draw(canvas)
            
        elif mode == "boss_room":
            if boss_room.state == "fight": player.handle_input(keys)
            boss_room.update(player)
            boss_room.draw(canvas, player)
        elif mode == "power_puzzle": power_puzzle.draw(canvas)
        elif mode == "server": server_puzzle.draw(canvas)
        elif mode == "botany": botany_room.draw(canvas)
        elif mode == "engineering": engineering_room.draw(canvas)

        if mode != "intro":
            game_state.particles.update_and_draw(canvas)
        
        screen.blit(canvas, (0,0))
        draw_crt_overlay(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()