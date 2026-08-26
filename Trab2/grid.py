# Classe base abstrata (Abstract Base Class)
from abc import ABC, abstractmethod
import pygame
import random

SHAPES = {
    'T': [[0, 1, 0],
          [1, 1, 1],
          [0, 0, 0]],
          
    'O': [[1, 1],
          [1, 1]],
          
    'I': [[0, 0, 0, 0],
          [1, 1, 1, 1],
          [0, 0, 0, 0],
          [0, 0, 0, 0]],
          
    'S': [[0, 1, 1],
          [1, 1, 0],
          [0, 0, 0]],
          
    'Z': [[1, 1, 0],
          [0, 1, 1],
          [0, 0, 0]],
          
    'J': [[1, 0, 0],
          [1, 1, 1],
          [0, 0, 0]],
          
    'L': [[0, 0, 1],
          [1, 1, 1],
          [0, 0, 0]]
}

COLORS = [
    pygame.Color('cyan'),
    pygame.Color('yellow'),
    pygame.Color('purple'),
    pygame.Color('green'),
    pygame.Color('red'),
    pygame.Color('blue'),
    pygame.Color('orange')
]

# objeto herda de classe abstrata
## nunca pode ser criada, só as filhas
class obj (ABC):

    def __init__(self, x, y, sprites):
        self.x = x
        self.y = y
        #lista
        self.sprites = sprites


    def draw(self, screen):
        for s in self.sprites:
            screen.blit(s, (self.x, self.y))

    # avisa que o método é abstato e precisa ser feito pelos filhos
    @abstractmethod
    def update(self, dt):
        pass

class Grid (obj):
    # só avisa a construtora da mãe o que fazer
    # pode, e deve ser extendido para outras caracteristicas nescessárias
    def __init__(self, x, y, sprites, grid_size):
        # bom lugar para criar uma matriz de celulas
        super().__init__(x, y, sprites)

        self.columns = grid_size[0]
        self.rows = grid_size[1]

        self.matrix = [[0 for _ in range(self.columns)] for _ in range(self.rows)]

        self.current_piece = None
        self.piece_x = 0
        self.piece_y = 0
        self.next_piece = None
        self.next_color = None

        self.fall_time = 0
        self.fall_speed = 30
        self.ispaused = False
        self.game_over = False
        self.score = 0
        self.font = pygame.font.SysFont('arial', 24, bold=True)
        self.font_small = pygame.font.SysFont('arial', 16)

        self.spawn_piece()

    def check_collision(self, dx=0, dy=0):
        for y in range(len(self.current_piece)):
            for x in range(len(self.current_piece[0])):
                if self.current_piece[y][x] > 0:
                    global_x = self.piece_x + x + dx
                    global_y = self.piece_y + y + dy

                    if global_x < 0 or global_x >= self.columns or global_y >= self.rows:
                        return True

                    if global_y >= 0 and self.matrix[global_y][global_x] != 0:
                        return True
        return False

    def lock_piece(self):
        for y in range(len(self.current_piece)):
            for x in range(len(self.current_piece[0])):
                if self.current_piece[y][x] > 0:
                    self.matrix[self.piece_y + y][self.piece_x + x] = self.piece_color 

        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        surviving_lines = [row for row in self.matrix if 0 in row]

        cleared_count = self.rows - len(surviving_lines)

        if cleared_count > 0:
            new_empty_line = [[0 for _ in range(self.columns)] for _ in range(cleared_count)]
            self.matrix = new_empty_line + surviving_lines

            score_table = {1:100, 2:300, 3:300, 4:800}
            self.score += score_table.get(cleared_count, 0)

    def move_x(self, dx):
        if not self.ispaused and not self.game_over:
            if not self.check_collision(dx=dx, dy=0):
                self.piece_x +=dx

    def move_y(self, dy):
            if not self.ispaused and not self.game_over:
                if not self.check_collision(dx=0, dy=dy):
                    self.piece_y +=dy

    def rotate(self):
        original_piece = self.current_piece

        if not self.ispaused and not self.game_over:
            self.current_piece = [list(row) for row in zip(*self.current_piece[::-1])]

            if self.check_collision(dx=0, dy=0):
                self.current_piece = original_piece

    def reset(self):
        self.matrix = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        
        self.current_piece = None
        self.piece_x = 0
        self.piece_y = 0
        self.score = 0

        self.game_over = False
        self.ispaused = False
        self.fall_speed = 30

        self.next_piece = None

        self.spawn_piece()

    def pause(self):
        if self.game_over:
            return

        if not self.ispaused:
            self.ispaused = True
            self.fall_speed = 9223372036854775807
        else:
            self.ispaused = False
            self.fall_speed = 30

    def spawn_piece(self):
        if self.next_piece is None:
            shape_key = random.choice(list(SHAPES.keys()))
            self.next_piece = SHAPES[shape_key]
            self.next_color = random.choice(COLORS)
            
        self.current_piece = self.next_piece
        self.piece_color = self.next_color
        self.piece_x = self.columns // 2 - len(self.current_piece[0]) // 2
        self.piece_y = 0
        
        shape_key = random.choice(list(SHAPES.keys()))
        self.next_piece = SHAPES[shape_key]
        self.next_color = random.choice(COLORS)

        if self.check_collision(dx=0, dy=0):
            self.game_over = True

    def draw(self, screen):
        block_size = 25

        grid_width = self.columns * block_size
        grid_height = self.rows * block_size

        border_thickness = 4
        frame_rect = (self.x - border_thickness, 
                      self.y - border_thickness, 
                      grid_width + (border_thickness * 2), 
                      grid_height + (border_thickness * 2))
        
        pygame.draw.rect(screen, pygame.Color('deepskyblue'), frame_rect, border_thickness, border_radius=0)
        
        bg_rect = (self.x, self.y, grid_width, grid_height)
        pygame.draw.rect(screen, pygame.Color('black'), bg_rect)

        for y in range(self.rows):
            for x in range(self.columns):
                if self.matrix[y][x] != 0:
                    rect_x = self.x + (x * block_size)
                    rect_y = self.y + (y * block_size)
                    fixed_color = self.matrix[y][x]
                    pygame.draw.rect(screen, fixed_color, (rect_x, rect_y, block_size, block_size))
                    pygame.draw.rect(screen, pygame.Color('gray'), (rect_x, rect_y, block_size, block_size), 1)

        if self.current_piece:
            for y in range(len(self.current_piece)):
                for x in range(len(self.current_piece[0])):
                    if self.current_piece[y][x] > 0:
                        rect_x = self.x + ((self.piece_x + x) * block_size)
                        rect_y = self.y + ((self.piece_y + y) * block_size)
                        pygame.draw.rect(screen, self.piece_color, (rect_x, rect_y, block_size, block_size))
                        pygame.draw.rect(screen, pygame.Color('gray'), (rect_x, rect_y, block_size, block_size), 1)

        hud_x = self.x + grid_width + 20
        
        score_surface = self.font.render(f'SCORE', True, pygame.Color('White'))
        value_surface = self.font.render(f'{self.score}', True, pygame.Color('cyan'))
        screen.blit(score_surface, (hud_x, self.y + 0))
        screen.blit(value_surface, (hud_x, self.y + 30))
        
        next_surface = self.font.render(f'NEXT', True, pygame.Color('White'))
        screen.blit(next_surface, (hud_x, self.y + 80))
        
        if self.next_piece:
            for y in range(len(self.next_piece)):
                for x in range(len(self.next_piece[0])):
                    if self.next_piece[y][x] > 0:
                        nx = hud_x + (x * block_size)
                        ny = self.y + 110 + (y * block_size)
                        pygame.draw.rect(screen, self.next_color, (nx, ny, block_size, block_size))
                        pygame.draw.rect(screen, pygame.Color('gray'), (nx, ny, block_size, block_size), 1)
                        
        ctrl_y = self.y + 230
        controls = [
            "CONTROLES:",
            "A / D : Mover Horizontal",
            "S : Acelerar queda",
            "W : Rotacionar Peça",
            "R : Reiniciar",
            "P : Pausar"
        ]
        for line in controls:
            ctrl_surface = self.font_small.render(line, True, pygame.Color('lightgray'))
            screen.blit(ctrl_surface, (hud_x, ctrl_y))
            ctrl_y += 25 
            
        if self.game_over:
            go_surface = self.font.render("GAME OVER", True, pygame.Color('red'))
            go_rect = go_surface.get_rect(center=(self.x + grid_width // 2, self.y + grid_height // 2))
            pygame.draw.rect(screen, pygame.Color('black'), go_rect.inflate(20, 20))
            screen.blit(go_surface, go_rect)

    def update(self, dt):
        if not self.current_piece or self.game_over:
            return

        self.fall_time += dt

        if self.fall_time >= self.fall_speed:
            self.fall_time = 0

            if not self.check_collision(dy=1):
                self.piece_y += 1
            else:
                self.lock_piece()

class Cell (obj):

    # só avisa a construtora da mãe o que fazer
    # pode, e deve ser extendido para outras caracteristicas nescessárias
    def __init__(self, x, y, sprites, grid_size):
        # bom lugar para definir coisas como o fundo da céula
        super().__init__(x, y, sprites)

    def draw(self, screen):

        # chama o desenha já pronto de obj, mas pode ser extendido
        return super().draw(screen)

    def update(self, dt):
        # não chama o de super, porque ele não implementa, crie seu próprio
        return 
