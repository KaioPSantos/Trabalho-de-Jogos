import pygame
import random
import math
from player import Player
from powerup import PowerUp
from enemy import Enemy, BasicEnemy, ShotgunEnemy, BossEnemy, SpinnerEnemy, ShieldEnemy
from bullet import Bullet, ExplosiveBullet
from util import EventHandler, circle_collistiion

pygame.init()
WIDTH = 800
HEIGHT = 600
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))  
font = pygame.font.SysFont("Consolas", 16)
large_font = pygame.font.SysFont("Consolas", 36, bold=True)

ROAD_LEFT = 140
ROAD_RIGHT = 660

# Variáveis globais de controle de estado e onda
game_state = "PLAYING"
is_paused = False
time_slow_remaining = 0

current_wave_index = 0
transitioning_wave = False
transition_timer = 0
bg_speed_multiplier = 1.0

player = None
objects = []

def toggle_pause(data):
    global is_paused
    is_paused = not is_paused

def on_time_slow(duration):
    global time_slow_remaining
    time_slow_remaining = duration

def on_game_over(data):
    global game_state
    game_state = "GAMEOVER"

def remove_obj(obj):
    if obj in objects:
        objects.remove(obj) 

def add_obj(obj):
    if obj not in objects:
        objects.append(obj)

EventHandler().subscribe("DestroyObj", remove_obj)
EventHandler().subscribe("SpawnObj", add_obj)
EventHandler().subscribe("TogglePause", toggle_pause)
EventHandler().subscribe("TimeSlow", on_time_slow)
EventHandler().subscribe("GameOver", on_game_over)

road_particles = [
    [random.randint(ROAD_LEFT + 10, ROAD_RIGHT - 10), random.randint(0, HEIGHT), random.uniform(2, 5), random.randint(2, 4)]
    for _ in range(50)
]

def generate_non_overlapping_pos(existing_positions, min_dist=50):
    for _ in range(100): 
        rx = random.randint(ROAD_LEFT + 40, ROAD_RIGHT - 40)
        ry = random.randint(50, 160)
        
        valid = True
        for pos in existing_positions:
            dist = math.hypot(rx - pos[0], ry - pos[1])
            if dist < min_dist:
                valid = False
                break
        if valid:
            existing_positions.append((rx, ry))
            return (rx, ry)
    return (random.randint(ROAD_LEFT + 40, ROAD_RIGHT - 40), random.randint(50, 160))

def generate_wave(wave_num):
    existing_positions = []
    wave_enemies = []
    shotgun_count = 0
    
    if wave_num % 5 == 0:
        wave_enemies.append(BossEnemy((360, 60)))
        extra_count = 2 + (wave_num // 5)
        available_types = [BasicEnemy, ShotgunEnemy, SpinnerEnemy, ShieldEnemy]
        for _ in range(extra_count):
            pos = generate_non_overlapping_pos(existing_positions, min_dist=60)
            enemy_cls = random.choice(available_types)
            if enemy_cls == ShotgunEnemy:
                shotgun_count += 1
            wave_enemies.append(enemy_cls(pos))
    else:
        enemy_count = min(12, 3 + wave_num)
        available_types = [BasicEnemy, ShotgunEnemy]
        if wave_num >= 2:
            available_types.append(SpinnerEnemy)
        if wave_num >= 3:
            available_types.append(ShieldEnemy)

        for _ in range(enemy_count):
            pos = generate_non_overlapping_pos(existing_positions, min_dist=45)
            valid_types = [t for t in available_types if t != ShotgunEnemy or shotgun_count < 2]
            enemy_cls = random.choice(valid_types)
            if enemy_cls == ShotgunEnemy:
                shotgun_count += 1
            wave_enemies.append(enemy_cls(pos))

    return wave_enemies

def reset_game():
    global game_state, is_paused, time_slow_remaining, current_wave_index, transitioning_wave, transition_timer, bg_speed_multiplier, player, objects
    
    game_state = "PLAYING"
    is_paused = False
    time_slow_remaining = 0
    current_wave_index = 0
    transitioning_wave = False
    transition_timer = 0
    bg_speed_multiplier = 1.0

    objects.clear()
    player = Player((WIDTH // 2, HEIGHT - 80))
    objects.append(player)
    
    initial_enemies = generate_wave(current_wave_index + 1)
    for enemy in initial_enemies:
        objects.append(enemy)

def handle_input(player_ref):
    global game_state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if game_state == "PLAYING":
                if event.key == pygame.K_SPACE:
                    player_ref.time_slow()
                if event.key == pygame.K_p:
                    player_ref.pause() 
            elif game_state in ["GAMEOVER", "WIN"]:
                if event.key == pygame.K_r:
                    reset_game()

def check_collisions():
    bullets = [o for o in objects if isinstance(o, Bullet)]
    enemies = [o for o in objects if isinstance(o, Enemy)]
    powerups = [o for o in objects if isinstance(o, PowerUp)]

    p_center = (player.pos[0] + player.radius, player.pos[1] + player.radius)
    for p in powerups:
        p_pos = (p.pos.x, p.pos.y)
        if circle_collistiion(p_pos, p.radius, p_center, player.radius):
            player.apply_powerup(p.type)
            EventHandler().notify("DestroyObj", p)

    for b in bullets:
        if b.owner == "player":
            for e in enemies:
                b_center = (b.pos[0] + b.radius, b.pos[1] + b.radius)
                e_center = (e.pos[0] + e.radius, e.pos[1] + e.radius)
                if circle_collistiion(b_center, b.radius, e_center, e.radius):
                    e.take_damage(1)
                    if isinstance(b, ExplosiveBullet):
                        b.explode()
                    else:
                        b.destroy()
                    break
        elif b.owner == "enemy":
            b_center = (b.pos[0] + b.radius, b.pos[1] + b.radius)
            if circle_collistiion(b_center, b.radius, p_center, player.radius):
                player.take_damage(1)
                b.destroy()

def draw_hud():
    for i in range(max(0, player.hp)):
        pygame.draw.circle(screen, pygame.Color("lime"), (25 + i * 25, 25), 8)

    if time_slow_remaining > 0:
        txt = font.render(f"SLOW TIME: {time_slow_remaining / 1000:.1f}s", True, pygame.Color("cyan"))
    else:
        ratio = min(1.0, player.time_slow_timer / player.time_slow_cooldown)
        if ratio >= 1.0:
            txt = font.render("SLOW TIME: PRONTO (ESPAÇO)", True, pygame.Color("cyan"))
        else:
            txt = font.render(f"SLOW TIME: {ratio * 100:.0f}%", True, pygame.Color("gray"))
    screen.blit(txt, (10, 45))

    wave_txt = font.render(f"WAVE {current_wave_index + 1}", True, pygame.Color("white"))
    screen.blit(wave_txt, (WIDTH - 100, 10))

    if transitioning_wave and game_state == "PLAYING":
        adv_txt = font.render("AVANÇANDO PARA A PRÓXIMA LINHA INIMIGA...", True, pygame.Color("yellow"))
        screen.blit(adv_txt, (WIDTH // 2 - adv_txt.get_width() // 2, HEIGHT // 2))

    if is_paused and game_state == "PLAYING":
        pause_txt = font.render("JOGO PAUSADO", True, pygame.Color("white"))
        screen.blit(pause_txt, (WIDTH // 2 - pause_txt.get_width() // 2, HEIGHT // 2 - 40))

    if game_state == "GAMEOVER":
        go_txt = large_font.render("GAME OVER", True, pygame.Color("red"))
        restart_txt = font.render("Pressione 'R' para Reiniciar", True, pygame.Color("white"))
        screen.blit(go_txt, (WIDTH // 2 - go_txt.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 10))

def draw_background():
    screen.fill((45, 55, 30))
    pygame.draw.rect(screen, (95, 70, 45), (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
    pygame.draw.line(screen, (35, 25, 15), (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
    pygame.draw.line(screen, (35, 25, 15), (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)
    
    for particle in road_particles:
        px, py, speed, size = particle
        pygame.draw.circle(screen, (120, 95, 60), (int(px), int(py)), size)

# Inicialização da partida
reset_game()

running = True
while running:
    dt = clock.tick(60)

    handle_input(player)

    if game_state == "PLAYING" and not is_paused:
        for particle in road_particles:
            particle[1] += particle[2] * bg_speed_multiplier
            if particle[1] > HEIGHT:
                particle[1] = 0
                particle[0] = random.randint(ROAD_LEFT + 10, ROAD_RIGHT - 10)

        active_enemies = [o for o in objects if isinstance(o, Enemy)]
        if len(active_enemies) == 0 and not transitioning_wave:
            transitioning_wave = True
            transition_timer = 2000
            bg_speed_multiplier = 6.0

        if transitioning_wave:
            transition_timer -= dt
            if transition_timer <= 0:
                transitioning_wave = False
                bg_speed_multiplier = 1.0
                current_wave_index += 1
                wave_objs = generate_wave(current_wave_index + 1)
                for enemy in wave_objs:
                    add_obj(enemy)

        if time_slow_remaining > 0:
            time_slow_remaining -= dt
            enemy_dt = dt * 0.25
        else:
            enemy_dt = dt

        for obj in list(objects):
            if isinstance(obj, Player) or (isinstance(obj, Bullet) and obj.owner == "player"):
                obj.update(dt)
            else:
                obj.update(enemy_dt)

        check_collisions()

    draw_background()

    for obj in objects:
        obj.draw(screen)

    draw_hud()
    
    pygame.display.flip()