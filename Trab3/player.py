import pygame
import random
from abc import ABC, abstractmethod
from util import colored_sprite, EventHandler
from bullet import straightBullet, ExplosiveBullet

class Player:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 16
        self.max_hp = 5
        self.hp = self.max_hp

        self.time_slow_cooldown = 60000  
        self.time_slow_timer = 60000      
        self.time_slow_duration = 5000   

        self.invincible_timer = 0

        self.sprite = colored_sprite(pygame.Color("lime"))
        self.last_mouse_pos = pygame.mouse.get_pos()

        self.state = NormalState(self)

    def update(self, dt):
        if self.time_slow_timer < self.time_slow_cooldown:
            self.time_slow_timer += dt

        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        self.update_movement()
        
        self.state.update(dt)

    def update_movement(self):
        keys = pygame.key.get_pressed()
        moving_keyboard = (keys[pygame.K_LEFT] or keys[pygame.K_a] or
                           keys[pygame.K_RIGHT] or keys[pygame.K_d] or
                           keys[pygame.K_UP] or keys[pygame.K_w] or
                           keys[pygame.K_DOWN] or keys[pygame.K_s])

        if moving_keyboard:
            speed = 5
            x, y = self.pos.x, self.pos.y
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                x -= speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                x += speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                y -= speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                y += speed

            x = max(0, min(800, x))
            y = max(0, min(600, y))

            self.pos = pygame.Vector2(x, y)
            self.last_mouse_pos = pygame.mouse.get_pos()
        else:
            current_mouse_pos = pygame.mouse.get_pos()
            if current_mouse_pos != self.last_mouse_pos:
                self.pos = pygame.Vector2(current_mouse_pos)
                self.last_mouse_pos = current_mouse_pos

    def draw(self, screen):
        if self.invincible_timer > 0 and (int(self.invincible_timer / 100) % 2 == 0):
            return
        screen.blit(self.sprite, self.pos)

    def take_damage(self, amount=1):
        if self.invincible_timer > 0:
            return

        self.hp -= amount
        self.invincible_timer = 1500  
        if self.hp <= 0:
            EventHandler().notify("GameOver", None)

    def apply_powerup(self, ptype):
        if ptype == 'timeslow':
            self.time_slow_timer = self.time_slow_cooldown
        elif ptype == 'invincible':
            self.invincible_timer = 10000  
        elif ptype == 'shotgun':
            self.change_state(ShotgunState(self))
        elif ptype == 'smg':
            self.change_state(SMGState(self))
        elif ptype == 'grenade':
            self.change_state(GrenadeState(self))
        elif ptype == 'heal':
            self.hp = self.max_hp

    def time_slow(self):
        if self.time_slow_timer >= self.time_slow_cooldown:
            self.time_slow_timer = 0
            EventHandler().notify("TimeSlow", self.time_slow_duration)

    def pause(self):
        EventHandler().notify("TogglePause", None)

    def change_state(self, new_state):
        self.state = new_state

    # --- Padrões de Disparo (Métodos da Entidade Player) ---

    def shoot_normal(self):
        spawn_pos = (self.pos.x + 12, self.pos.y)
        bullet = straightBullet(
            pos=spawn_pos, 
            angle=0, 
            radius=4, 
            life_time=2000, 
            owner="player", 
            color=pygame.Color("cyan"), 
            speed=0.8
        )
        EventHandler().notify("SpawnObj", bullet)

    def shoot_shotgun(self):
        angles = [-30, -15, 0, 15, 30]
        spawn_pos = (self.pos.x + 12, self.pos.y)
        for ang in angles:
            b = straightBullet(
                pos=spawn_pos, 
                angle=ang, 
                radius=4, 
                life_time=1800, 
                owner="player", 
                color=pygame.Color("orange"), 
                speed=0.8
            )
            EventHandler().notify("SpawnObj", b)

    def shoot_smg(self):
        spawn_pos_x = (self.pos.x + 10 + random.randint(-4, 4))
        for offset_x in [-20, 0, 20]:
            b = straightBullet(
                pos= (self.pos.x + 10 + offset_x, self.pos.y + 10), 
                angle=0, 
                radius=3, 
                life_time=1500, 
                owner="player", 
                color=pygame.Color("cyan"), 
                speed=0.9
            )
            EventHandler().notify("SpawnObj", b)

    def shoot_grenade(self):
        spawn_pos = (self.pos.x + 12, self.pos.y)
        b = ExplosiveBullet(
            pos=spawn_pos, angle=0, radius=8, life_time=1200, 
            owner="player", color=pygame.Color("green"), speed=0.5
        )
        EventHandler().notify("SpawnObj", b)


# --- Estados Lógicos do Player (Apenas Controlam Temporizadores e Invocam o Player) ---

class PlayerState(ABC):
    def __init__(self, player):
        self.P = player

    @abstractmethod
    def update(self, dt):
        pass


class NormalState(PlayerState):
    def __init__(self, player):
        super().__init__(player)
        self.shoot_timer = 0
        self.shoot_cooldown = 150

    def update(self, dt):
        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            self.P.shoot_normal()


class ShotgunState(PlayerState):
    def __init__(self, player, duration=20000):
        super().__init__(player)
        self.timer = duration
        self.shoot_timer = 0
        self.shoot_cooldown = 600

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.P.change_state(NormalState(self.P))
            return

        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            self.P.shoot_shotgun()


class SMGState(PlayerState):
    def __init__(self, player, duration=20000):
        super().__init__(player)
        self.timer = duration
        self.shoot_timer = 0
        self.shoot_cooldown = 150

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.P.change_state(NormalState(self.P))
            return

        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            self.P.shoot_smg()


class GrenadeState(PlayerState):
    def __init__(self, player, duration=10000):
        super().__init__(player)
        self.timer = duration
        self.shoot_timer = 0
        self.shoot_cooldown = 900

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.P.change_state(NormalState(self.P))
            return

        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            self.P.shoot_grenade()