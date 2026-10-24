import pygame

#não achei um tileset que funcionasse no 8-4-4 ent pedi para o gemini gerar a imagem de tileset que estou usando.

class AutotileGrid:
    def __init__(self, cols=10, rows=7, tile_size=80, image_path=None):
        self.cols = cols
        self.rows = rows
        self.tile_size = tile_size
        self.quad_size = tile_size // 2
        
        self.grid = [[0 for _ in range(rows)] for _ in range(cols)]
        
        # Se passar o caminho da imagem, carrega do arquivo; senão usa procedural
        if image_path:
            self.quad_sprites = self.load_quad_sprites_from_image(image_path)
        else:
            self.quad_sprites = self.generate_quad_sprites()

    def load_quad_sprites_from_image(self, image_path):
        sheet = pygame.image.load(image_path).convert_alpha()

        # Cada tile completo do tileset2.png tem 118x118 px,
        # então cada sub tile (quadrante) tem 59x59 px
        Q = 59

        # Recorta um quadrante de 59x59 px na posição (x, y) em pixels da imagem
        def cut(x, y):
            surf = pygame.Surface((Q, Q), pygame.SRCALPHA)
            surf.blit(sheet, (0, 0), pygame.Rect(x, y, Q, Q))
            return surf

        empty  = pygame.Surface((Q, Q), pygame.SRCALPHA)  # 0: Vazio
        top    = cut(133, 5)    # 1: Borda Topo
        left   = cut(5, 133)    # 2: Borda Esquerda
        corner = cut(5, 5)      # 3: Quina Externa
        center = cut(192, 64)   # 4: CENTRO SÓLIDO

        raw = [empty, top, left, corner, center]

        # Escala cada sub tile para o tamanho do quadrante na tela
        size = (self.quad_size, self.quad_size)
        return [pygame.transform.scale(s, size) for s in raw]

    def generate_quad_sprites(self):
        sprites = []
        c_solid = (110, 170, 80)
        c_bg = (40, 40, 50)
        c_edge = (240, 200, 80)

        for i in range(5):
            surf = pygame.Surface((self.quad_size, self.quad_size))
            surf.fill(c_solid if i > 0 else c_bg)
            
            if i in [1, 3]: # Borda superior
                pygame.draw.rect(surf, c_edge, (0, 0, self.quad_size, 4))
            if i in [2, 3]: # Borda lateral
                pygame.draw.rect(surf, c_edge, (0, 0, 4, self.quad_size))
            if i == 0: # Fundo puro
                pygame.draw.rect(surf, (60, 60, 75), (2, 2, self.quad_size-4, self.quad_size-4), 1)

            sprites.append(surf)
        return sprites

    def get_cell(self, x, y):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.grid[x][y]
        return 1

    def toggle_cell(self, x, y, value=None):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            if value is None:
                self.grid[x][y] = 0 if self.grid[x][y] == 1 else 1
            else:
                self.grid[x][y] = value

    def calculate_quad_index(self, v1, v2):
        # v1 e v2 são os 2 vizinhos adjacentes ao quadrante (vertical e horizontal)
        # A borda verde aparece do lado onde NÃO há vizinho
        if v1 == 0 and v2 == 0:
            return 3  # Quina Externa (Borda verde no canto)
        if v1 == 0 and v2 == 1:
            return 1  # Borda Topo/Base (vazio só em cima/embaixo)
        if v1 == 1 and v2 == 0:
            return 2  # Borda Lateral (vazio só na esquerda/direita)
        return 4      # CENTRO SÓLIDO (os dois vizinhos existem)

    def draw_tile(self, screen, x, y):
        px = x * self.tile_size
        py = y * self.tile_size
        qs = self.quad_size

        # SE TILE == 0 (SEM COLISÃO / AR):
        if self.grid[x][y] == 0:
            pygame.draw.rect(screen, (70, 70, 80), (px, py, self.tile_size, self.tile_size), 1)
            return

        n  = self.get_cell(x, y - 1)
        s  = self.get_cell(x, y + 1)
        e  = self.get_cell(x + 1, y)
        w  = self.get_cell(x - 1, y)

        # Topo-Esquerdo (TL)
        idx_tl = self.calculate_quad_index(n, w)
        surf_tl = self.quad_sprites[idx_tl]
        screen.blit(surf_tl, (px, py))

        # Topo-Direito (TR)
        idx_tr = self.calculate_quad_index(n, e)
        surf_tr = pygame.transform.flip(self.quad_sprites[idx_tr], True, False)
        screen.blit(surf_tr, (px + qs, py))

        # Fundo-Esquerdo (BL)
        idx_bl = self.calculate_quad_index(s, w)
        surf_bl = pygame.transform.flip(self.quad_sprites[idx_bl], False, True)
        screen.blit(surf_bl, (px, py + qs))

        # Fundo-Direito (BR)
        idx_br = self.calculate_quad_index(s, e)
        surf_br = pygame.transform.flip(self.quad_sprites[idx_br], True, True)
        screen.blit(surf_br, (px + qs, py + qs))

    def draw(self, screen):
        for x in range(self.cols):
            for y in range(self.rows):
                self.draw_tile(screen, x, y)