import pygame
import math
from ball import Ball
from shape import Polygon
from collision import Collide

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

parede_esq = Polygon([(0, 0), (20, 0), (20, 600), (0, 600)])
parede_dir = Polygon([(780, 0), (800, 0), (800, 600), (780, 600)])
teto       = Polygon([(0, 0), (800, 0), (800, 20), (0, 20)])
rampa1_esq = Polygon([(180, 600), (228, 600), (228, 560)], is_subshape=True)
rampa1_dir = Polygon([(262, 560), (262, 600), (310, 600)], is_subshape=True)
rampa2_esq = Polygon([(490, 600), (538, 600), (538, 560)], is_subshape=True)
rampa2_dir = Polygon([(572, 560), (572, 600), (620, 600)], is_subshape=True)

def create_peg(cx, cy, radius=10, sides=20):
    points = []
    for i in range(sides):
        angle = (2 * math.pi / sides) * i
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        points.append((px, py))

    peg = Polygon(points, is_subshape=True)
    peg.can_hit = True
    return peg

pegs = []
rows = 5
cols = 8

for row in range(rows):
    y = 180 + row * 70  

    offset_x = 50 if row % 2 == 1 else 0 
    
    for col in range(cols):
        x = 75 + col * 100 + offset_x
        if 40 < x < 760:  
            pegs.append(create_peg(x, y))

polygons = [parede_esq, teto, parede_dir, rampa1_esq, rampa1_dir, rampa2_esq, rampa2_dir] + pegs

duck_raw = pygame.image.load("imagens/base.png").convert_alpha()

ball_radius = 16
duck_sprite = pygame.transform.scale(duck_raw, (ball_radius * 2, ball_radius * 2))

bola = Ball(400,100,duck_sprite,ball_radius)

pontos = 0
pontos_rodada = 0
tentativas = 3
game_over = False

running = True

while running:
    dt = clock.tick(60) / 1000.0
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not bola.launched:
                bola.launch(event.pos)
                tentativas -= 1

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                pontos = 0
                pontos_rodada = 0
                tentativas = 3
                game_over = False
                bola.reset()

    bola.update(dt)

    for peg in pegs:
        peg.update(dt)

    for polygon in polygons:
        if bola.bounce_off_polygon(polygon):
            if getattr(polygon, 'can_hit', False):
                pontos_rodada += 10

    if bola.pos.y > 595 and bola.launched:
        x = bola.pos.x

        if (70 <= x <= 140) or (660 <= x <= 730):
            mult = 2  
        elif 380 <= x <= 420:
            mult = 5  
        else:
            mult = 1  

        base_pts = pontos_rodada 
        pontos += base_pts * mult

        pontos_rodada = 0

        if tentativas > 0:
            bola.reset()
        else:
            game_over = True

    screen.fill((30, 30, 30))

    for a in [parede_esq,teto,parede_dir]:
        a.draw(screen, color=(pygame.Color('darkgreen')))

    for a in [rampa1_dir, rampa1_esq, rampa2_dir, rampa2_esq]:
            a.draw(screen, color=(pygame.Color('darkblue')))

    for peg in pegs:
        peg.draw(screen, color=(pygame.Color('red')))

    bola.draw(screen, mouse_pos)

    pygame.draw.rect(screen, (50, 180, 50), (70, 580, 70, 20))    # Canto esquerdo (2x)
    pygame.draw.rect(screen, (220, 180, 40), (350, 580, 100, 20))  # Meio (5x)
    pygame.draw.rect(screen, (50, 180, 50), (660, 580, 70, 20))   # Canto direito (2x)

    font = pygame.font.SysFont(None, 24)

    screen.blit(font.render("2X", True, (255, 255, 255)), (93, 582))
    screen.blit(font.render("5X", True, (255, 255, 255)), (390, 582))
    screen.blit(font.render("2X", True, (255, 255, 255)), (683, 582))

    txt_pontos = font.render(f"Pontos: {pontos}  (Rodada: +{pontos_rodada})", True, (255, 255, 255))
    txt_tentativas = font.render(f"Tentativas restantes: {tentativas}", True, (255, 255, 255))
    screen.blit(txt_pontos, (35, 30))
    screen.blit(txt_tentativas, (35, 55))

    if game_over:
        font_go = pygame.font.SysFont(None, 42)
        txt_go = font_go.render("FIM DE JOGO! Clique R para jogar novamente.", True, (255, 80, 80))
        screen.blit(txt_go, (110, 270))

    txt_cmd = font.render("Clique Esquerdo: Mirar e Atirar | R: Resetar bola", True, (255, 255, 255))
    screen.blit(txt_cmd, (35, 4))

    pygame.display.flip()

pygame.quit()