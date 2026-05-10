import random
import math

# --- CONFIGURACION DE PANTALLA ---
WIDTH = 570  # 19 columnas * 30 pixeles
HEIGHT = 650  # 19 filas * 30 pixeles + 80 pixeles para el panel inferior
TITLE = "Pac-Man Arcade - 4 Fantasmas y Niveles"
CELL_SIZE = 30

# --- MAPA BASE DEL LABERINTO ---
# 1 = Muro azul, 0 = Punto blanco, 3 = Pildora de poder (Grande), 2 = Pasillo vacio
MAP_TEMPLATE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 3, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 2, 1, 2, 1, 1, 1, 0, 1, 1, 1, 1],
    [2, 2, 2, 1, 0, 1, 2, 2, 2, 2, 2, 2, 2, 1, 0, 1, 2, 2, 2],  # Tunel lateral
    [1, 1, 1, 1, 0, 1, 2, 1, 1, 2, 1, 1, 2, 1, 0, 1, 1, 1, 1],
    [2, 2, 2, 2, 0, 2, 2, 1, 2, 2, 2, 1, 2, 2, 0, 2, 2, 2, 2],
    [1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1],
    [2, 2, 2, 1, 0, 1, 2, 2, 2, 2, 2, 2, 2, 1, 0, 1, 2, 2, 2],
    [1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Fila 14
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 3, 0, 1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1, 0, 3, 1],
    [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# Copia de trabajo para el nivel actual
MAP = [row[:] for row in MAP_TEMPLATE]

# --- VARIABLES DE CONTROL GLOBAL ---
score = 0
lives = 3
current_level = 1
game_state = "START"  # "START", "PLAYING", "DYING", "GAME_OVER", "VICTORY"
scared_timer = 0  # Temporizador del modo asustado
state_timer = 0  # Para transiciones de pantallas
flash_pills = True  # Parpadeo de pildoras gigantes

# --- ENTIDADES DEL JUEGO ---


class Pacman:
    def __init__(self):
        self.speed = 3
        self.reset()

    def reset(self):
        # Aparece de forma segura en la fila 14, columna 1
        start_row = 14
        start_col = 1
        self.x = (start_col * CELL_SIZE) + 15
        self.y = (start_row * CELL_SIZE) + 15
        self.dx, self.dy = 0, 0
        self.next_dx, self.next_dy = 0, 0
        self.mouth_angle = 0
        self.mouth_opening = True

    def update(self):
        grid_r = int((self.y - 15 + CELL_SIZE // 2) // CELL_SIZE)
        grid_c = int((self.x - 15 + CELL_SIZE // 2) // CELL_SIZE)

        # Intentar girar si estamos cerca del centro
        offset_x = (self.x - 15) % CELL_SIZE
        offset_y = (self.y - 15) % CELL_SIZE

        if (offset_x < self.speed or offset_x > CELL_SIZE - self.speed) and (
            offset_y < self.speed or offset_y > CELL_SIZE - self.speed
        ):

            if self.next_dx != 0 or self.next_dy != 0:
                target_r = grid_r + self.next_dy
                target_c = (grid_c + self.next_dx) % 19

                if MAP[target_r][target_c] != 1:
                    self.dx, self.dy = self.next_dx, self.next_dy
                    self.x = (grid_c * CELL_SIZE) + 15
                    self.y = (grid_r * CELL_SIZE) + 15
        # Tuneles laterales
        if self.dx == 1 and grid_c >= 18:
            self.x = 15
            return
        elif self.dx == -1 and grid_c <= 0:
            self.x = 18 * CELL_SIZE + 15
            return
        # Movimiento hacia adelante
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
        screen.draw.filled_circle((self.x, self.y), 13, (255, 255, 0))

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
            screen.draw.line((self.x, self.y), p1, (0, 0, 0))
            screen.draw.line((self.x, self.y), p2, (0, 0, 0))


class Ghost:
    def __init__(self, color, name):
        self.color = color
        self.name = name
        self.base_speed = 2
        self.speed = 2
        self.reset()

    def reset(self):
        # Los fantasmas inician juntos en su caja central
        self.x, self.y = 9 * CELL_SIZE + 15, 8 * CELL_SIZE + 15
        self.dx, self.dy = 0, -1

    def update(self):
        # Los fantasmas solo toman decisiones cuando están perfectamente alineados en una casilla
        if (int(self.x - 15) % CELL_SIZE == 0) and (int(self.y - 15) % CELL_SIZE == 0):
            grid_r = int(self.y // CELL_SIZE)
            grid_c = int(self.x // CELL_SIZE)

            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            valid_moves = []

            # Buscar direcciones permitidas sin dar media vuelta directa de forma inmediata
            for dx, dy in directions:
                if dx == -self.dx and dy == -self.dy:
                    continue
                nr, nc = grid_r + dy, (grid_c + dx) % 19
                if MAP[nr][nc] != 1:
                    valid_moves.append((dx, dy))
            if not valid_moves:
                self.dx, self.dy = -self.dx, -self.dy
                return
            # Si están asustados, eligen caminos de forma aleatoria
            if scared_timer > 0:
                self.dx, self.dy = random.choice(valid_moves)
            else:
                # Comportamientos de persecución IA clásicos
                pac_r = int(pacman.y // CELL_SIZE)
                pac_c = int(pacman.x // CELL_SIZE)

                if self.name == "Blinky":  # Rojo: Persigue directamente
                    target_r, target_c = pac_r, pac_c
                elif self.name == "Pinky":  # Rosa: Embosca yendo 4 pasos por delante
                    target_r = pac_r + pacman.dy * 4
                    target_c = pac_c + pacman.dx * 4
                elif self.name == "Inky":  # Cian: Patrón variable según cercanía
                    dist = math.hypot(grid_r - pac_r, grid_c - pac_c)
                    if dist > 6:
                        target_r, target_c = pac_r, pac_c
                    else:
                        target_r, target_c = 1, 17  # Esquina superior derecha
                else:  # Clyde (Naranja): Si está lejos persigue, si está cerca huye
                    dist = math.hypot(grid_r - pac_r, grid_c - pac_c)
                    if dist > 8:
                        target_r, target_c = pac_r, pac_c
                    else:
                        target_r, target_c = 17, 1  # Esquina inferior izquierda
                # Buscar el movimiento que más nos acerque a nuestro objetivo
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
                draw_color = (255, 255, 255)  # Parpadeo final
            else:
                draw_color = (25, 25, 166)  # Azul oscuro asustado
        # Cuerpo del fantasma
        screen.draw.filled_circle((self.x, self.y - 2), 12, draw_color)
        screen.draw.filled_rect(Rect((self.x - 12, self.y - 2), (24, 12)), draw_color)
        screen.draw.filled_circle((self.x - 8, self.y + 10), 4, draw_color)
        screen.draw.filled_circle((self.x, self.y + 10), 4, draw_color)
        screen.draw.filled_circle((self.x + 8, self.y + 10), 4, draw_color)

        # Ojos
        if scared_timer == 0:
            eye_offset_x = self.dx * 3
            eye_offset_y = self.dy * 3
            screen.draw.filled_circle((self.x - 5, self.y - 2), 4, (255, 255, 255))
            screen.draw.filled_circle(
                (self.x - 5 + eye_offset_x, self.y - 2 + eye_offset_y), 2, (0, 0, 255)
            )
            screen.draw.filled_circle((self.x + 5, self.y - 2), 4, (255, 255, 255))
            screen.draw.filled_circle(
                (self.x + 5 + eye_offset_x, self.y - 2 + eye_offset_y), 2, (0, 0, 255)
            )
        else:
            # Carita asustada
            screen.draw.filled_circle((self.x - 4, self.y - 2), 2, (255, 165, 0))
            screen.draw.filled_circle((self.x + 4, self.y - 2), 2, (255, 165, 0))


# --- INSTANCIAR ELEMENTOS ---
pacman = Pacman()
ghosts = [
    Ghost((255, 0, 0), "Blinky"),  # Blinky (Rojo)
    Ghost((255, 182, 193), "Pinky"),  # Pinky (Rosa)
    Ghost((0, 255, 255), "Inky"),  # Inky (Cian)
    Ghost((255, 165, 0), "Clyde"),  # Clyde (Naranja)
]

# --- LOGICA DE CONTROL ---
def trigger_flash():
    global flash_pills
    flash_pills = not flash_pills


clock.schedule_interval(trigger_flash, 0.25)


def next_level():
    global MAP, game_state, state_timer, current_level, scared_timer
    current_level += 1
    scared_timer = 0

    # Reiniciar laberinto con todos los puntos de vuelta
    MAP = [row[:] for row in MAP_TEMPLATE]

    # Reiniciar posiciones
    pacman.reset()
    for ghost in ghosts:
        ghost.reset()
        # Los fantasmas aceleran levemente con cada nivel superado
        ghost.speed = ghost.base_speed + min(current_level * 0.2, 1.2)
    game_state = "START"
    state_timer = 0


# --- RENDERING (DIBUJO) ---
def draw():
    screen.fill((0, 0, 0))

    # Dibujar el mapa
    for r in range(19):
        for c in range(19):
            x, y = c * CELL_SIZE, r * CELL_SIZE
            cx, cy = x + 15, y + 15

            if MAP[r][c] == 1:
                screen.draw.rect(
                    Rect((x + 3, y + 3), (CELL_SIZE - 6, CELL_SIZE - 6)), (0, 0, 255)
                )
            elif MAP[r][c] == 0:
                screen.draw.filled_circle((cx, cy), 3, (255, 184, 151))
            elif MAP[r][c] == 3 and flash_pills:
                screen.draw.filled_circle((cx, cy), 8, (255, 184, 151))
    # Dibujar Entidades
    if game_state != "DYING":
        pacman.draw()
        for ghost in ghosts:
            ghost.draw()
    # Interfaz de texto inferior
    screen.draw.text(f"SCORE: {score}", (20, HEIGHT - 60), fontsize=28, color="white")
    screen.draw.text(
        f"LEVEL: {current_level}",
        (WIDTH // 2 - 50, HEIGHT - 60),
        fontsize=28,
        color="yellow",
    )
    screen.draw.text(
        f"LIVES: {lives}", (WIDTH - 130, HEIGHT - 60), fontsize=28, color="white"
    )

    if game_state == "START":
        screen.draw.text(
            f"LEVEL {current_level}",
            center=(WIDTH // 2, HEIGHT // 2 - 10),
            fontsize=48,
            color="yellow",
        )
        screen.draw.text(
            "PREPARE PLAYER ONE",
            center=(WIDTH // 2, HEIGHT // 2 + 40),
            fontsize=32,
            color="white",
        )
    elif game_state == "GAME_OVER":
        screen.draw.text(
            "GAME OVER", center=(WIDTH // 2, HEIGHT // 2 + 20), fontsize=50, color="red"
        )
    elif game_state == "VICTORY":
        screen.draw.text(
            "LEVEL CLEAR!",
            center=(WIDTH // 2, HEIGHT // 2 + 20),
            fontsize=46,
            color="green",
        )


# --- ACTUALIZACION ---
def update():
    global score, lives, game_state, scared_timer, state_timer

    if game_state == "START":
        state_timer += 1
        if state_timer > 90:
            game_state = "PLAYING"
            state_timer = 0
        return
    if game_state == "DYING":
        state_timer += 1
        if state_timer > 60:
            if lives > 0:
                pacman.reset()
                for ghost in ghosts:
                    ghost.reset()
                game_state = "START"
            else:
                game_state = "GAME_OVER"
            state_timer = 0
        return
    if game_state == "VICTORY":
        state_timer += 1
        if state_timer > 90:
            next_level()
        return
    if game_state != "PLAYING":
        return
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
            # Cuanto mayor sea el nivel, menos dura el modo asustado de los fantasmas
            scared_timer = max(300 - (current_level * 30), 80)
    # Colisiones con fantasmas
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
                return
    # Verificar si limpió el nivel
    dots_left = sum(row.count(0) + row.count(3) for row in MAP)
    if dots_left == 0:
        game_state = "VICTORY"
        state_timer = 0


# --- CAPTURA DE TECLAS ---
def on_key_down(key):
    if key == keys.LEFT:
        pacman.next_dx, pacman.next_dy = -1, 0
    elif key == keys.RIGHT:
        pacman.next_dx, pacman.next_dy = 1, 0
    elif key == keys.UP:
        pacman.next_dx, pacman.next_dy = 0, -1
    elif key == keys.DOWN:
        pacman.next_dx, pacman.next_dy = 0, 1
