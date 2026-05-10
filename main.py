import pygame
import random
import math
import asyncio  # Obligatorio para la web

# --- Inicializar Pygame estándar ---
pygame.init()

# --- CONFIGURACION DE PANTALLA ---
WIDTH = 570   # 19 columnas * 30 pixeles
HEIGHT = 650  # 19 filas * 30 pixeles + 80 pixeles para el panel inferior
CELL_SIZE = 30

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Arcade")
clock = pygame.time.Clock()

# --- MAPA BASE DEL LABERINTO ---
MAP_TEMPLATE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,3,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,3,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,0,1,1,1,2,1,2,1,1,1,0,1,1,1,1],
    [2,2,2,1,0,1,2,2,2,2,2,2,2,1,0,1,2,2,2], 
    [1,1,1,1,0,1,2,1,1,2,1,1,2,1,0,1,1,1,1],
    [2,2,2,2,0,2,2,1,2,2,2,1,2,2,0,2,2,2,2],
    [1,1,1,1,0,1,2,1,1,1,1,1,2,1,0,1,1,1,1],
    [2,2,2,1,0,1,2,2,2,2,2,2,2,1,0,1,2,2,2],
    [1,1,1,1,0,1,2,1,1,1,1,1,2,1,0,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1], 
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,3,0,1,0,0,0,0,0,2,0,0,0,0,0,1,0,3,1],
    [1,1,0,1,0,1,0,1,1,1,1,1,0,1,0,1,0,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

MAP = [row[:] for row in MAP_TEMPLATE]

# --- VARIABLES GLOBALES ---
score = 0
lives = 3
current_level = 1
game_state = "START"      
scared_timer = 0          
state_timer = 0           
flash_pills = True        
flash_counter = 0

class Pacman:
    def __init__(self):
        self.speed = 3
        self.reset()

    def reset(self):
        self.x = (1 * CELL_SIZE) + 15
        self.y = (14 * CELL_SIZE) + 15
        self.dx, self.dy = 0, 0           
        self.next_dx, self.next_dy = 0, 0  
        self.mouth_angle = 0
        self.mouth_opening = True

    def update(self):
        grid_r = int((self.y - 15 + CELL_SIZE // 2) // CELL_SIZE)
        grid_c = int((self.x - 15 + CELL_SIZE // 2) // CELL_SIZE)

        offset_x = (self.x - 15) % CELL_SIZE
        offset_y = (self.y - 15) % CELL_SIZE
        
        if (offset_x < self.speed or offset_x > CELL_SIZE - self.speed) and \
           (offset_y < self.speed or offset_y > CELL_SIZE - self.speed):
            if self.next_dx != 0 or self.next_dy != 0:
                target_r = grid_r + self.next_dy
                target_c = (grid_c + self.next_dx) % 19
                if MAP[target_r][target_c] != 1:
                    self.dx, self.dy = self.next_dx, self.next_dy
                    self.x = (grid_c * CELL_SIZE) + 15
                    self.y = (grid_r * CELL_SIZE) + 15

        if self.dx == 1 and grid_c >= 18:
            self.x = 15
            return
        elif self.dx == -1 and grid_c <= 0:
            self.x = 18 * CELL_SIZE + 15
            return

        next_x = self.x + self.dx * self.speed
        next_y = self.y + self.dy * self.speed
        next_r = int((next_y - 15 + CELL_SIZE // 2) // CELL_SIZE)
        next_c = int((next_x - 15 + CELL_SIZE // 2) // CELL_SIZE)

        if 0 <= next_r < 19 and 0 <= next_c < 19:
            if MAP[next_r][next_c] != 1:
                self.x = next_x
                self.y = next_y
                if self.dx != 0 or self.dy != 0:
                    if self.mouth_opening:
                        self.mouth_angle += 8
                        if self.mouth_angle >= 45:
                            self.mouth_opening = False
                    else:
                        self.mouth_angle -= 8
                        if self.mouth_angle <= 0:
                            self.mouth_opening = True
            else:
                self.dx, self.dy = 0, 0
                self.x = (grid_c * CELL_SIZE) + 15
                self.y = (grid_r * CELL_SIZE) + 15
                self.mouth_angle = 15

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 13)
        if self.mouth_angle > 0:
            rad = math.radians(self.mouth_angle)
            if self.dx == 1 or (self.dx == 0 and self.dy == 0):
                p1 = (self.x + 14, self.y - 14 * rad)
                p2 = (self.x + 14, self.y + 14 * rad)
            elif self.dx == -1:
                p1 = (self.x - 14, self.y - 14 * rad)
                p2 = (self.x - 14, self.y + 14 * rad)
            elif self.dy == 1:
                p1 = (self.x - 14 * rad, self.y + 14)
                p2 = (self.x + 14 * rad, self.y + 14)
            elif self.dy == -1:
                p1 = (self.x - 14 * rad, self.y - 14)
                p2 = (self.x + 14 * rad, self.y - 14)
            pygame.draw.line(screen, (0, 0, 0), (self.x, self.y), p1, 2)
            pygame.draw.line(screen, (0, 0, 0), (self.x, self.y), p2, 2)

class Ghost:
    def __init__(self, color, name):
        self.color = color
        self.name = name
        self.base_speed = 2
        self.speed = 2
        self.reset()

    def reset(self):
        self.x, self.y = 9 * CELL_SIZE + 15, 8 * CELL_SIZE + 15
        self.dx, self.dy = 0, -1

    def update(self):
        if (int(self.x - 15) % CELL_SIZE == 0) and (int(self.y - 15) % CELL_SIZE == 0):
            grid_r = int(self.y // CELL_SIZE)
            grid_c = int(self.x // CELL_SIZE)
            directions = [(1,0), (-1,0), (0,1), (0,-1)]
            valid_moves = []
            
            for dx, dy in directions:
                if dx == -self.dx and dy == -self.dy:
                    continue  
                nr, nc = grid_r + dy, (grid_c + dx) % 19
                if MAP[nr][nc] != 1:
                    valid_moves.append((dx, dy))

            if not valid_moves:
                self.dx, self.dy = -self.dx, -self.dy
                return

            if scared_timer > 0:
                self.dx, self.dy = random.choice(valid_moves)
            else:
                pac_r, pac_c = int(pacman.y // CELL_SIZE), int(pacman.x // CELL_SIZE)
                if self.name == "Blinky":
                    target_r, target_c = pac_r, pac_c
                elif self.name == "Pinky":
                    target_r = pac_r + pacman.dy * 4
                    target_c = pac_c + pacman.dx * 4
                elif self.name == "Inky":
                    dist = math.hypot(grid_r - pac_r, grid_c - pac_c)
                    target_r, target_c = (pac_r, pac_c) if dist > 6 else (1, 17)
                else:
                    dist = math.hypot(grid_r - pac_r, grid_c - pac_c)
                    target_r, target_c = (pac_r, pac_c) if dist > 8 else (17, 1)

                best_move = valid_moves[0]
                min_distance = 9999
                for dx, dy in valid_moves:
                    check_r = grid_r + dy
                    check_c = (grid_c + dx) % 19
                    dist = math.hypot(check_r - target_r, check_c - target_c)
                    if dist < min_distance:
                        min_distance = dist
                        best_move = (dx, dy)
                self.dx, self.dy = best_move

        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def draw(self):
        draw_color = self.color
        if scared_timer > 0:
            if scared_timer < 100 and (scared_timer // 10) % 2 == 0:
                draw_color = (255, 255, 255)
            else:
                draw_color = (25, 25, 166)

        pygame.draw.circle(screen, draw_color, (int(self.x), int(self.y - 2)), 12)
        pygame.draw.rect(screen, draw_color, pygame.Rect(int(self.x - 12), int(self.y - 2), 24, 12))
        pygame.draw.circle(screen, draw_color, (int(self.x - 8), int(self.y + 10)), 4)
        pygame.draw.circle(screen, draw_color, (int(self.x), int(self.y + 10)), 4)
        pygame.draw.circle(screen, draw_color, (int(self.x + 8), int(self.y + 10)), 4)

        if scared_timer == 0:
            eye_offset_x = self.dx * 3
            eye_offset_y = self.dy * 3
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x - 5), int(self.y - 2)), 4)
            pygame.draw.circle(screen, (0, 0, 255), (int(self.x - 5 + eye_offset_x), int(self.y - 2 + eye_offset_y)), 2)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x + 5), int(self.y - 2)), 4)
            pygame.draw.circle(screen, (0, 0, 255), (int(self.x + 5 + eye_offset_x), int(self.y - 2 + eye_offset_y)), 2)
        else:
            pygame.draw.circle(screen, (255, 165, 0), (int(self.x - 4), int(self.y - 2)), 2)
            pygame.draw.circle(screen, (255, 165, 0), (int(self.x + 4), int(self.y - 2)), 2)

# --- Instanciar ---
pacman = Pacman()
ghosts = [
    Ghost((255, 0, 0), "Blinky"),
    Ghost((255, 182, 193), "Pinky"),
    Ghost((0, 255, 255), "Inky"),
    Ghost((255, 165, 0), "Clyde")
]

def next_level():
    global MAP, game_state, state_timer, current_level, scared_timer
    current_level += 1
    scared_timer = 0
    MAP = [row[:] for row in MAP_TEMPLATE]
    pacman.reset()
    for ghost in ghosts:
        ghost.reset()
        ghost.speed = ghost.base_speed + min(current_level * 0.2, 1.2)
    game_state = "START"
    state_timer = 0

# --- Bucle asíncrono principal (Requerido para Pygbag) ---
async def main():
    global score, lives, game_state, scared_timer, state_timer, flash_pills, flash_counter
    font = pygame.font.SysFont("Arial", 28)
    font_large = pygame.font.SysFont("Arial", 46)

    running = True
    while running:
        # Control de FPS (Fijado a 30 para suavidad en la web)
        clock.tick(30)
        screen.fill((0, 0, 0))

        # --- Entrada de usuario (Teclas) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pacman.next_dx, pacman.next_dy = -1, 0
                elif event.key == pygame.K_RIGHT:
                    pacman.next_dx, pacman.next_dy = 1, 0
                elif event.key == pygame.K_UP:
                    pacman.next_dx, pacman.next_dy = 0, -1
                elif event.key == pygame.K_DOWN:
                    pacman.next_dx, pacman.next_dy = 0, 1

        # --- Temporizador de parpadeo de píldoras ---
        flash_counter += 1
        if flash_counter >= 8:
            flash_pills = not flash_pills
            flash_counter = 0

        # --- LOGICA DEL JUEGO ---
        if game_state == "START":
            state_timer += 1
            if state_timer > 60:
                game_state = "PLAYING"
                state_timer = 0
        elif game_state == "DYING":
            state_timer += 1
            if state_timer > 45:
                if lives > 0:
                    pacman.reset()
                    for ghost in ghosts: ghost.reset()
                    game_state = "START"
                else:
                    game_state = "GAME_OVER"
                state_timer = 0
        elif game_state == "VICTORY":
            state_timer += 1
            if state_timer > 60:
                next_level()
        elif game_state == "PLAYING":
            if scared_timer > 0:
                scared_timer -= 1

            pacman.update()
            for ghost in ghosts:
                ghost.update()

            # Comer puntos
            r = int((pacman.y - 15 + CELL_SIZE // 2) // CELL_SIZE)
            c = int((pacman.x - 15 + CELL_SIZE // 2) // CELL_SIZE)
            if 0 <= r < 19 and 0 <= c < 19:
                if MAP[r][c] == 0:
                    MAP[r][c] = 2
                    score += 10
                elif MAP[r][c] == 3:
                    MAP[r][c] = 2
                    score += 50
                    scared_timer = max(300 - (current_level * 30), 80)

            # Colisiones
            for ghost in ghosts:
                dist = math.hypot(pacman.x - ghost.x, pacman.y - ghost.y)
                if dist < 18:
                    if scared_timer > 0:
                        score += 200
                        ghost.reset()
                    else:
                        lives -= 1
                        game_state = "DYING"
                        state_timer = 0

            # Nivel completado?
            dots_left = sum(row.count(0) + row.count(3) for row in MAP)
            if dots_left == 0:
                game_state = "VICTORY"
                state_timer = 0

        # --- RENDERIZADO (DIBUJO) ---
        # Dibujar laberinto
        for r in range(19):
            for c in range(19):
                x, y = c * CELL_SIZE, r * CELL_SIZE
                cx, cy = x + 15, y + 15
                if MAP[r][c] == 1:
                    pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(x+3, y+3, CELL_SIZE-6, CELL_SIZE-6), 1)
                elif MAP[r][c] == 0:
                    pygame.draw.circle(screen, (255, 184, 151), (cx, cy), 3)
                elif MAP[r][c] == 3 and flash_pills:
                    pygame.draw.circle(screen, (255, 184, 151), (cx, cy), 8)

        # Dibujar personajes
        if game_state != "DYING":
            pacman.draw()
            for ghost in ghosts:
                ghost.draw()

        # Textos de UI
        score_txt = font.render(f"SCORE: {score}", True, (255, 255, 255))
        level_txt = font.render(f"LEVEL: {current_level}", True, (255, 255, 0))
        lives_txt = font.render(f"LIVES: {lives}", True, (255, 255, 255))
        screen.blit(score_txt, (20, HEIGHT - 60))
        screen.blit(level_txt, (WIDTH // 2 - 50, HEIGHT - 60))
        screen.blit(lives_txt, (WIDTH - 130, HEIGHT - 60))

        if game_state == "START":
            start_lbl1 = font_large.render(f"LEVEL {current_level}", True, (255, 255, 0))
            start_lbl2 = font.render("PREPARE PLAYER ONE", True, (255, 255, 255))
            screen.blit(start_lbl1, (WIDTH // 2 - start_lbl1.get_width() // 2, HEIGHT // 2 - 20))
            screen.blit(start_lbl2, (WIDTH // 2 - start_lbl2.get_width() // 2, HEIGHT // 2 + 40))
        elif game_state == "GAME_OVER":
            over_lbl = font_large.render("GAME OVER", True, (255, 0, 0))
            screen.blit(over_lbl, (WIDTH // 2 - over_lbl.get_width() // 2, HEIGHT // 2 + 20))
        elif game_state == "VICTORY":
            win_lbl = font_large.render("LEVEL CLEAR!", True, (0, 255, 0))
            screen.blit(win_lbl, (WIDTH // 2 - win_lbl.get_width() // 2, HEIGHT // 2 + 20))

        pygame.display.flip()
        
        # LINEA CRITICA: Cede el control al navegador para evitar bloqueos
        await asyncio.sleep(0)

# Lanzar el bucle asíncrono
asyncio.run(main())
