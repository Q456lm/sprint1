#!/usr/bin/env python3
"""
Echo of Terminal 7 — Complete Edition.
Features:
- Neon aesthetics, CRT effects, Smooth Physics, Particles.
- Boss Battle Ending with Weapon mechanics.
- Restored Botany Room atmospheric spores.
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
PROJECTILE_SPEED = 12

# Colors (Neon Palette)
C_BG_DEEP = (5, 5, 12)
C_GRID = (20, 30, 45)
C_NEON_CYAN = (0, 255, 240)
C_NEON_BLUE = (0, 100, 255)
C_NEON_GREEN = (50, 255, 50)
C_NEON_RED = (255, 50, 50)
C_NEON_YELLOW = (255, 220, 0)
C_NEON_PURPLE = (200, 50, 255)
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
        self.size = random.randint(1, 3)

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
        # Draw a glowing line/bullet
        end_pos = self.pos - self.vel * 0.5
        pygame.draw.line(surface, C_NEON_CYAN, self.pos, end_pos, 3)
        pygame.draw.circle(surface, C_WHITE, (int(self.pos.x), int(self.pos.y)), self.radius)

class Boss:
    def __init__(self):
        self.pos = pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100)
        self.radius = 40
        self.hp = 100
        self.max_hp = 100
        self.angle = 0
        self.pulse = 0
        self.speed = 2.5
        self.active = True

    def update(self, player_pos):
        if not self.active: return
        
        # Chase logic
        direction = player_pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
        self.pos += direction * self.speed
        
        self.pulse += 0.1
        self.angle += 2

    def draw(self, surface):
        if not self.active: return
        
        cx, cy = int(self.pos.x), int(self.pos.y)
        
        # Glitchy/Pulsing effect
        pulse_size = math.sin(self.pulse) * 5
        
        # Outer Aura
        for i in range(3):
            off_x = random.randint(-5, 5)
            off_y = random.randint(-5, 5)
            pygame.draw.circle(surface, (100, 0, 0), (cx + off_x, cy + off_y), self.radius + 10 + int(pulse_size))

        # Core
        pygame.draw.circle(surface, C_NEON_RED, (cx, cy), self.radius)
        pygame.draw.circle(surface, (50, 0, 0), (cx, cy), self.radius - 10)
        
        # "Eye" looking at player
        pygame.draw.circle(surface, C_NEON_YELLOW, (cx, cy), 8)

        # Health Bar
        bar_w = 100
        bar_h = 10
        pygame.draw.rect(surface, (50, 0, 0), (cx - bar_w//2, cy - self.radius - 20, bar_w, bar_h))
        fill_w = int((self.hp / self.max_hp) * bar_w)
        pygame.draw.rect(surface, C_NEON_RED, (cx - bar_w//2, cy - self.radius - 20, fill_w, bar_h))


# ------------------------------------------------------------
# Game Classes
# ------------------------------------------------------------

class GameState:
    def __init__(self) -> None:
        self.power_restored = False
        self.herd_secret_known = False
        self.slip_repaired = False
        self.boss_unlocked = False
        self.boss_defeated = False
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
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            accel.x -= PLAYER_ACCEL
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            accel.x += PLAYER_ACCEL
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            accel.y -= PLAYER_ACCEL
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            accel.y += PLAYER_ACCEL

        self.vel += accel
        self.vel *= PLAYER_FRICTION
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)

        self.pos += self.vel
        self.pos.x = max(0, min(self.pos.x, SCREEN_WIDTH - 32))
        self.pos.y = max(0, min(self.pos.y, SCREEN_HEIGHT - 32))
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface: pygame.Surface) -> None:
        if self.invuln_timer > 0:
            self.invuln_timer -= 1
            if (self.invuln_timer // 5) % 2 == 0: # Blink effect
                return

        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.pos.x
        dy = mouse_pos[1] - self.pos.y
        self.angle = math.degrees(math.atan2(-dy, dx)) # Simple visual angle

        center = self.rect.center
        pygame.draw.circle(surface, C_NEON_CYAN, center, 12)
        pygame.draw.circle(surface, C_WHITE, center, 6)
        
        # Weapon barrel
        barrel_end = (center[0] + (dx/math.sqrt(dx**2 + dy**2))*20, 
                      center[1] + (dy/math.sqrt(dx**2 + dy**2))*20)
        pygame.draw.line(surface, C_NEON_CYAN, center, barrel_end, 4)

class RoomHub:
    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.doors = {
            "botany": pygame.Rect(80, 40, 120, 10),
            "server": pygame.Rect(SCREEN_WIDTH // 2 - 60, 40, 120, 10),
            "engineering": pygame.Rect(SCREEN_WIDTH - 200, 40, 120, 10),
        }
        # Boss door spawns later
        self.boss_door = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 60, 200, 20)
        self.power_console = pygame.Rect(SCREEN_WIDTH - 140, SCREEN_HEIGHT // 2 - 25, 80, 50)
        self.grid_offset = 0
        self.alert_blink = 0

    def draw_bg_grid(self, surface, alert_mode=False):
        self.grid_offset = (self.grid_offset + 0.5) % 40
        line_col = C_GRID
        if alert_mode:
            # Pulse red during alert
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

        # Draw Standard Doors
        for key, rect in self.doors.items():
            col = C_NEON_BLUE
            pygame.draw.rect(surface, col, rect)
            draw_text_shadow(surface, self.font, key.upper(), C_WHITE, (rect.centerx, rect.bottom + 40))

        # Boss Door (Only if unlocked)
        if game_state.boss_unlocked:
            self.alert_blink += 1
            blink_col = C_NEON_RED if (self.alert_blink // 30) % 2 == 0 else (100, 0, 0)
            
            draw_glow_rect(surface, blink_col, self.boss_door, glow_radius=15)
            draw_text_shadow(surface, self.font, "!!! AIRLOCK OPEN !!!", C_NEON_RED, (self.boss_door.centerx, self.boss_door.top - 30))
            draw_text_shadow(surface, self.font, "ENTITY DETECTED", C_NEON_RED, (self.boss_door.centerx, self.boss_door.top - 10))

        # Power Console
        console_color = C_NEON_YELLOW if not game_state.power_restored else C_NEON_GREEN
        draw_glow_rect(surface, console_color, self.power_console, glow_radius=5)
        status = "PWR: OFF" if not game_state.power_restored else "PWR: ON"
        draw_text_shadow(surface, self.font, status, console_color, (self.power_console.centerx, self.power_console.top - 20))

        # Interactions
        interact = self.check_interaction(player, game_state)
        if interact:
            hint_text = f"[E] ENTER {interact.upper()}"
            rect = player.rect
            draw_text_shadow(surface, self.font, hint_text, C_NEON_CYAN, (rect.centerx, rect.top - 20))

    def check_interaction(self, player: Player, game_state: GameState) -> Optional[str]:
        for name, rect in self.doors.items():
            if player.rect.colliderect(rect.inflate(20, 100)):
                return name
        
        if game_state.boss_unlocked and player.rect.colliderect(self.boss_door.inflate(20, 60)):
            return "boss_room"

        if player.rect.colliderect(self.power_console.inflate(20, 20)):
            return "power_console"
        return None

class BossRoom:
    """The final arena."""
    def __init__(self, font: pygame.font.Font, game_state: GameState, particles: ParticleSystem):
        self.font = font
        self.game_state = game_state
        self.particles = particles
        self.boss = Boss()
        self.projectiles: List[Projectile] = []
        self.state = "intro" # intro, fight, win, game_over
        self.intro_timer = 120

    def reset(self, player: Player):
        self.boss = Boss()
        self.projectiles = []
        self.state = "intro"
        self.intro_timer = 180
        player.pos = pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100)
        player.hp = 5

    def handle_event(self, event: pygame.event.Event, player: Player):
        if self.state == "fight":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Shoot
                mx, my = pygame.mouse.get_pos()
                dx = mx - player.pos.x
                dy = my - player.pos.y
                angle = math.atan2(dy, dx)
                
                # Spawn bullet
                self.projectiles.append(Projectile(player.pos.x + 16, player.pos.y + 16, angle))
                # Recoil effect (particles)
                self.particles.spawn(player.pos.x, player.pos.y, C_NEON_CYAN, count=5, speed=1)

    def update(self, player: Player):
        if self.state == "intro":
            self.intro_timer -= 1
            if self.intro_timer <= 0:
                self.state = "fight"
        
        if self.state == "fight":
            # Update Boss
            self.boss.update(player.pos)
            
            # Check Boss hitting Player
            boss_rect = pygame.Rect(self.boss.pos.x - self.boss.radius, self.boss.pos.y - self.boss.radius, 
                                    self.boss.radius*2, self.boss.radius*2)
            if player.invuln_timer == 0 and boss_rect.colliderect(player.rect):
                player.hp -= 1
                player.invuln_timer = 60
                self.particles.spawn(player.pos.x, player.pos.y, C_NEON_RED, count=20, speed=4)
                if player.hp <= 0:
                    self.state = "game_over"

            # Update Projectiles
            for p in self.projectiles:
                p.update()
                # Check collision with Boss
                dist_to_boss = p.pos.distance_to(self.boss.pos)
                if dist_to_boss < self.boss.radius:
                    self.boss.hp -= 2
                    p.active = False
                    self.particles.spawn(p.pos.x, p.pos.y, C_NEON_YELLOW, count=8)
                    if self.boss.hp <= 0:
                        self.boss.active = False
                        self.state = "win"
                        # Big explosion
                        self.particles.spawn(self.boss.pos.x, self.boss.pos.y, C_NEON_RED, count=100, speed=6, life_scale=3.0)

            self.projectiles = [p for p in self.projectiles if p.active]

    def draw(self, surface: pygame.Surface, player: Player):
        # Background
        surface.fill((20, 0, 0))
        # Moving Grid
        t = pygame.time.get_ticks() * 0.05
        for i in range(0, SCREEN_WIDTH + 100, 100):
            x = (i + t) % (SCREEN_WIDTH + 100) - 50
            pygame.draw.line(surface, (50, 0, 0), (x, 0), (x, SCREEN_HEIGHT))

        # Draw Boss
        if self.boss.active:
            self.boss.draw(surface)

        # Draw Projectiles
        for p in self.projectiles:
            p.draw(surface)

        # Draw Player
        player.draw(surface)

        # UI Overlays
        if self.state == "intro":
            draw_text_shadow(surface, self.font, "WARNING: SPECIMEN BREACH", C_NEON_RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            draw_text_shadow(surface, self.font, "ELIMINATE THE TARGET", C_WHITE, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        
        elif self.state == "game_over":
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            surface.blit(s, (0,0))
            draw_text_shadow(surface, self.font, "STATUS: DECEASED", C_NEON_RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            draw_text_shadow(surface, self.font, "PRESS ESC TO RETRY", C_WHITE, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))

        elif self.state == "win":
            draw_text_shadow(surface, self.font, "TARGET ELIMINATED", C_NEON_GREEN, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            draw_text_shadow(surface, self.font, "TERMINAL SECURED. MISSION COMPLETE.", C_WHITE, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))

        # Player HUD
        if self.state == "fight":
            hp_text = f"INTEGRITY: {player.hp * 20}%"
            col = C_NEON_GREEN if player.hp > 2 else C_NEON_RED
            draw_text_shadow(surface, self.font, hp_text, col, (100, SCREEN_HEIGHT - 30))

# ------------------------------------------------------------
# Puzzles
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
                        if self.sequence == self.ORDER:
                            self.resolved = True
                        else:
                            self.failed_timer = 60

    def draw(self, surface) -> None:
        surface.fill((10, 5, 5))
        draw_text_shadow(surface, self.font, "POWER GRID CALIBRATION", C_NEON_CYAN, (SCREEN_WIDTH//2, 40))
        # Riddle
        riddle = ['"The sky comes before the sun...', '...but the grass must never touch the blood.', 'The sun is not last."']
        for i, line in enumerate(riddle):
            draw_text_shadow(surface, self.font, line, C_WHITE, (SCREEN_WIDTH//2, 90 + i*30))
        # Buttons
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
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif len(self.input_text) < 30 and event.unicode.isprintable():
                self.input_text += event.unicode

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
    """Restored with atmospheric spores (dots)."""
    def __init__(self, font, game_state, particles) -> None:
        self.font = font
        self.game_state = game_state
        self.particles = particles
        self.tanks = {"A": pygame.Rect(0,0,120,200), "B": pygame.Rect(0,0,120,200), "C": pygame.Rect(0,0,120,200)}
        
        # Init Spores (The dots)
        self.cells = [] 
        for _ in range(50):
            # [x, y, speed]
            self.cells.append([random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.uniform(0.5, 2)])

        start_x = (SCREEN_WIDTH - (3*120 + 2*80)) // 2
        for i, k in enumerate(["A", "B", "C"]):
            self.tanks[k].topleft = (start_x + i*200, SCREEN_HEIGHT//2 - 100)
        self.solved = False
        self.message = ""

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and not self.solved:
            for name, rect in self.tanks.items():
                if rect.collidepoint(event.pos):
                    if name == "C":
                        self.solved = True
                        self.game_state.herd_secret_known = True
                        self.message = "MATCH CONFIRMED: PREDICTIVE ALGORITHM DETECTED."
                        self.particles.spawn(rect.centerx, rect.centery, C_NEON_GREEN, 30)
                    else:
                        self.message = f"SPECIMEN {name}: NEGATIVE. STANDARD BEHAVIOR."
                        self.particles.spawn(rect.centerx, rect.centery, C_NEON_RED, 10)

    def draw(self, surface) -> None:
        surface.fill((5, 20, 10))
        
        # Draw Floating Spores
        for c in self.cells:
            c[1] -= c[2] # Move up
            if c[1] < 0: c[1] = SCREEN_HEIGHT
            # Draw faint spore
            pygame.draw.circle(surface, (40, 80, 50), (int(c[0]), int(c[1])), 2)

        draw_text_shadow(surface, self.font, "BIO-LAB: SUBJECT IDENTIFICATION", C_NEON_GREEN, (SCREEN_WIDTH//2, 40))
        for name, rect in self.tanks.items():
            color = C_NEON_GREEN if name == "C" and self.solved else C_NEON_CYAN
            pygame.draw.rect(surface, (0, 20, 10), rect, border_radius=10)
            pygame.draw.rect(surface, color, rect, 2, border_radius=10)
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

# ------------------------------------------------------------
# Main Loop & CRT Effect
# ------------------------------------------------------------

def draw_crt_overlay(surface):
    for y in range(0, SCREEN_HEIGHT, 4):
        pygame.draw.line(surface, (0, 0, 0, 100), (0, y), (SCREEN_WIDTH, y))
    vig = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(vig, (0,0,0,100), (0,0,SCREEN_WIDTH, SCREEN_HEIGHT), 20)
    surface.blit(vig, (0,0))

def main() -> None:
    pygame.init()
    pygame.display.set_caption("Echo of Terminal 7 — Boss Edition")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18, bold=True)

    game_state = GameState()
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    
    hub = RoomHub(font)
    power_puzzle = PowerGridPuzzle(font, game_state.particles)
    server_puzzle = ServerRoomPuzzle(font, game_state)
    botany_room = BotanyRoom(font, game_state, game_state.particles)
    engineering_room = EngineeringRoom(font, game_state)
    boss_room = BossRoom(font, game_state, game_state.particles)

    mode = "hub"
    running = True
    canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    while running:
        canvas.fill(C_BG_DEEP)
        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if mode == "hub": running = False
                elif mode == "boss_room" and boss_room.state == "game_over":
                    # Reset boss fight on fail
                    boss_room.reset(player)
                else: 
                    # If leaving a puzzle, check if we just unlocked the boss
                    if mode != "boss_room":
                        game_state.check_all_puzzles()
                    mode = "hub"
            else:
                if mode == "power_puzzle": power_puzzle.handle_event(event)
                elif mode == "server": server_puzzle.handle_event(event)
                elif mode == "botany": botany_room.handle_event(event)
                elif mode == "engineering": engineering_room.handle_event(event)
                elif mode == "boss_room": boss_room.handle_event(event, player)

        if mode == "hub":
            player.handle_input(keys)
            # Check puzzle states
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
            if boss_room.state == "fight":
                player.handle_input(keys)
            boss_room.update(player)
            boss_room.draw(canvas, player)
            
        elif mode == "power_puzzle": power_puzzle.draw(canvas)
        elif mode == "server": server_puzzle.draw(canvas)
        elif mode == "botany": botany_room.draw(canvas)
        elif mode == "engineering": engineering_room.draw(canvas)

        game_state.particles.update_and_draw(canvas)
        screen.blit(canvas, (0,0))
        draw_crt_overlay(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()