import pygame
import math
import random
from abc import ABC, abstractmethod
from util import colored_sprite, EventHandler
from bullet import straightBullet
from powerup import PowerUp

class Enemy(ABC):
    def __init__(self, pos, hp=1, radius=16):
        self.target_pos = pygame.Vector2(pos)
        self.pos = pygame.Vector2(pos[0], pos[1] - 300)
        self.hp = hp
        self.max_hp = hp
        self.radius = radius
        self.shoot_timer = 0

    def take_damage(self, amount=1):
        self.hp -= amount
        if self.hp <= 0:
            self.destroy()

    def destroy(self):
        if random.random() < 0.5:
            EventHandler().notify("SpawnObj", PowerUp(self.pos))
        EventHandler().notify("DestroyObj", self)

    def update_position(self,dt):
        if self.pos.y < self.target_pos.y:
            self.pos.y += 0.25 * dt
            if self.pos.y > self.target_pos.y:
                self.pos.y = self.target_pos.y

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def draw(self, screen):
        pass

class BasicEnemy(Enemy):
    def __init__(self, pos):
        super().__init__(pos, hp=3, radius=16)
        self.sprite = colored_sprite(pygame.Color("orange"),(32,32), circle=True)
        self.shoot_cooldown = 1000

    def update(self, dt):
        self.update_position(dt)
        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            self.shoot()

    def shoot(self):
        spawn_pos = (self.pos[0]+10, self.pos[1]+30)
        bullet = straightBullet(
            pos=spawn_pos,
            angle=180,
            radius=6,
            life_time=3000,
            owner="enemy",
            color=pygame.Color("red"),
            speed=0.4
        )
        EventHandler().notify("SpawnObj", bullet)

    def draw(self, screen):
        screen.blit(self.sprite, self.pos)

class ShotgunEnemy(Enemy):
    def __init__(self, pos):
            super().__init__(pos, hp=3, radius=20)
            self.shoot_cooldown = 2000
            self.sprite = pygame.Surface((40,40))
            self.sprite.set_colorkey((0,0,0))
            pygame.draw.polygon(self.sprite, pygame.Color("magenta"),[(20, 35), (5, 5), (35, 5)])
    
    def update(self, dt):
        self.update_position(dt)
        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            self.shoot()

    def shoot(self):
        spawn_pos = (self.pos[0] + 15, self.pos[1] + 35)
        angles = [180-30,180-10,180+10,180+30]
        for angle in angles:
            bullet = straightBullet(
                pos=spawn_pos,
                angle=angle,
                radius=5,
                life_time=3000,
                owner="enemy",
                color=pygame.Color("red"),
                speed=0.5
        )
            EventHandler().notify("SpawnObj", bullet)

    def draw(self, screen):
        screen.blit(self.sprite, self.pos)

class SpinnerEnemy(Enemy):
    def __init__(self, pos):
        super().__init__(pos, hp=6, radius=18)
        self.sprite = colored_sprite(pygame.Color("yellow"), (36, 36), circle=True)
        self.min_angle = -30
        self.max_angle = 30
        self.current_angle_offset = self.min_angle
        self.sweep_direction = 1  
        self.sweeps_completed = 0
        self.max_sweeps = 3       
        self.angle_step = 6       

        self.shoot_cooldown = 200 
        self.reload_cooldown = 4000 
        self.is_reloading = False

    def update(self, dt):
        self.update_position(dt)
        self.shoot_timer += dt

        if self.is_reloading:
            if self.shoot_timer >= self.reload_cooldown:
                self.shoot_timer = 0
                self.is_reloading = False
                self.sweeps_completed = 0
                self.current_angle_offset = self.min_angle
                self.sweep_direction = 1
        else:
            if self.shoot_timer >= self.shoot_cooldown:
                self.shoot_timer = 0
                self.shoot()

    def shoot(self):
        spawn_pos = (self.pos.x + 18, self.pos.y + 18)
        fire_angle = 180 + self.current_angle_offset
        
        bullet = straightBullet(
            pos=spawn_pos, 
            angle=fire_angle, 
            radius=5, 
            life_time=3500, 
            owner="enemy", 
            color=pygame.Color("yellow"), 
            speed=0.35
        )
        EventHandler().notify("SpawnObj", bullet)

        self.current_angle_offset += self.angle_step * self.sweep_direction

        if self.sweep_direction == 1 and self.current_angle_offset >= self.max_angle:
            self.current_angle_offset = self.max_angle
            self.sweep_direction = -1
            self.sweeps_completed += 1
        elif self.sweep_direction == -1 and self.current_angle_offset <= self.min_angle:
            self.current_angle_offset = self.min_angle
            self.sweep_direction = 1
            self.sweeps_completed += 1

        if self.sweeps_completed >= self.max_sweeps:
            self.is_reloading = True
            self.shoot_timer = 0

    def draw(self, screen):
        screen.blit(self.sprite, self.pos)

class ShieldEnemy(Enemy):
    def __init__(self, pos):
        super().__init__(pos, hp=8, radius=22)
        self.sprite = colored_sprite(pygame.Color("blue"), (44, 44), circle=False)
        self.shield_active = True
        self.shield_timer = 0
        self.shield_cycle = 3000
        self.shoot_cooldown = 2000

    def take_damage(self, amount=1):
        if self.shield_active:
            return
        super().take_damage(amount)

    def update(self, dt):
        self.update_position(dt)
        self.shield_timer += dt
        if self.shield_timer >= self.shield_cycle:
            self.shield_timer = 0
            self.shield_active = not self.shield_active
            self.shield_cycle = 3000 if self.shield_active else 2000

        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            self.shoot()

    def shoot(self):
        spawn_pos = (self.pos.x + 18, self.pos.y + 35)
        bullet = straightBullet(pos=spawn_pos, angle=180, radius=6, life_time=3000, owner="enemy", color=pygame.Color("cyan"), speed=0.4)
        EventHandler().notify("SpawnObj", bullet)

    def draw(self, screen):
        screen.blit(self.sprite, self.pos)
        if self.shield_active:
            pygame.draw.rect(screen, pygame.Color("cyan"), (self.pos.x, self.pos.y + 60, 50, 5))

class BossState(ABC):
    def __init__(self, boss):
        self.boss = boss

    @abstractmethod
    def update(self, dt):
        pass

class SMGState(BossState):
    def __init__(self, boss):
        super().__init__(boss)
        self.shoot_timer = 0
        self.shoot_cooldown = 150
        self.shots_fired = 0
        self.max_shots = 10

    def update(self, dt):
        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            self.boss.shoot_smg()
            self.shots_fired += 1
            if self.shots_fired >= self.max_shots:
                self.boss.change_state(TransitionState(self.boss, ShotgunState))

class ShotgunState(BossState):
    def __init__(self, boss):
        super().__init__(boss)
        self.shoot_timer = 0
        self.shoot_cooldown = 450
        self.shots_fired = 0
        self.max_shots = 5

    def update(self, dt):
        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            self.boss.shoot_shotgun()
            self.shots_fired += 1
            if self.shots_fired >= self.max_shots:
                self.boss.change_state(TransitionState(self.boss, SMGState))

class TransitionState(BossState):
    def __init__(self, boss, next_state_class):
        super().__init__(boss)
        self.next_state_class = next_state_class
        self.timer = 0
        self.cooldown = 5000

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.cooldown:
            self.boss.change_state(self.next_state_class(self.boss))

class BossEnemy(Enemy):
    def __init__(self, pos):
        super().__init__(pos, hp=40, radius=50)
        self.sprite = colored_sprite(pygame.Color("purple"), (80, 50), circle=False)

        self.speed_x = 0.12
        self.dir_x = 1

        self.state = SMGState(self)

    def change_state(self, new_state):
        self.state = new_state
        
    def update(self, dt):
        self.update_position(dt)
        if self.pos.y >= self.target_pos.y:
            self.pos.x += self.speed_x * self.dir_x * dt
            if self.pos.x <= 50:
                self.pos.x = 50
                self.dir_x = 1
            elif self.pos.x >= 800 - 130:
                self.pos.x = 800 - 130
                self.dir_x = -1

            self.state.update(dt)

    def shoot_smg(self):
        center_x = self.pos.x + 40
        spawn_y = self.pos.y + 50
        for offset_x in [-20, 0, 20]:
            bullet = straightBullet(
                pos=(center_x + offset_x, spawn_y),
                angle=180,
                radius=6,
                life_time=3500,
                owner="enemy",
                color=pygame.Color("red"),
                speed=0.5
            )
            EventHandler().notify("SpawnObj", bullet)

    def shoot_shotgun(self):
        left_spawn = (self.pos.x + 5, self.pos.y + 40)
        right_spawn = (self.pos.x + 75, self.pos.y + 40)
        
        angles_left = [180 - 35, 180 - 15, 180 + 15, 180 + 35]
        angles_right = [180 - 35, 180 - 15, 180 + 15, 180 + 35]

        for angle in angles_left:
            bullet = straightBullet(
                pos=left_spawn,
                angle=angle,
                radius=5,
                life_time=3000,
                owner="enemy",
                color=pygame.Color("red"),
                speed=0.45
            )
            EventHandler().notify("SpawnObj", bullet)

        for angle in angles_right:
            bullet = straightBullet(
                pos=right_spawn,
                angle=angle,
                radius=5,
                life_time=3000,
                owner="enemy",
                color=pygame.Color("red"),
                speed=0.45
            )
            EventHandler().notify("SpawnObj", bullet)

    def draw(self, screen):
        screen.blit(self.sprite, self.pos)
        bar_width = 80
        bar_height = 8
        fill = (self.hp / self.max_hp) * bar_width
        outline_rect = pygame.Rect(self.pos[0], self.pos[1] - 15, bar_width, bar_height)
        fill_rect = pygame.Rect(self.pos[0], self.pos[1] - 15, fill, bar_height)
        
        pygame.draw.rect(screen, pygame.Color("red"), outline_rect)
        pygame.draw.rect(screen, pygame.Color("green"), fill_rect)