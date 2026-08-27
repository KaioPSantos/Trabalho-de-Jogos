import pygame
from grid import Grid, Cell

pygame.init()
pygame.font.init()

pygame.key.set_repeat(200,50)

# caso precise de usar fontes na main, descomente
#font_size
#font = pygame.font.Font(None, font_size)

# caso precise carregar imagens na main, descomente
#idle = pygame.image.load("images/duck/base.png").convert_alpha()
#step = pygame.image.load("images/duck/step.png").convert_alpha()
#etc

# Cria a janela
WIDTH   =  500; HEIGHT =  565
screen = pygame.display.set_mode((WIDTH, HEIGHT))  

clock = pygame.time.Clock()
FPS = 60

#numero de celulas
grid_size = (12, 22)
campo_tetris = Grid(10,10,[],grid_size)

#criar objetos, adicione eles a lista
objects = [campo_tetris]

can_rotate = True

while True: 
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            exit()

        # uso do mouse é obrigatório
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]: # 0 botão esquedo 2, direito
                if campo_tetris.pause_btn.collidepoint(event.pos):
                    campo_tetris.pause()

        #caso queira usar levantar o mouse, descomente
        #elif event.type == pygame.MOUSEBUTTONUP:
        #      exit()

        # uso do teclado para controle é obrigatório
        elif event.type == pygame.KEYDOWN:
                #inclua outras funcionalidades para outras téclas
            if event.key == pygame.K_ESCAPE:
                exit()

            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                campo_tetris.move_x(-1)

            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                campo_tetris.move_x(+1)

            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                campo_tetris.move_y(+1)

            if event.key == pygame.K_r:
                campo_tetris.reset()

            if event.key == pygame.K_p:
                campo_tetris.pause()

            if event.key == pygame.K_w or event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                if can_rotate == True:
                    campo_tetris.rotate()
                    can_rotate = False

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                can_rotate = True   
            

    #atualiza
    for obj in objects:
        obj.update(1)

    # Desenha
    screen.fill((30, 30, 30))

    for obj in objects:
        obj.draw(screen)

    pygame.display.flip()

    clock.tick(FPS)