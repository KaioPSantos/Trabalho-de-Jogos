import pygame
import math
from abc import ABC, abstractmethod
from util import colored_sprite, EventHandler


import math

def rotate(pos, angle, axis = (0,0)):
    angle = math.radians(angle)
    x, y = pos
    ax, ay = axis

    # Translate so axis is the origin
    x -= ax
    y -= ay

    # Rotate
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    rx = x * cos_a - y * sin_a
    ry = x * sin_a + y * cos_a

    # Translate back
    return rx + ax, ry + ay

class Bullet(ABC):
    def __init__(self, pos, angle=0, radius=16, life_time=None, owner="enemy", color=pygame.Color("red")):
        self.pos = pygame.Vector2(pos)
        self.origin = pygame.Vector2(pos)
        self.life_time = life_time
        self.angle = angle
        self.elapsed = 0
        self.radius = radius
        self.owner = owner
        self.color = color

        self.sprite = colored_sprite(color, (self.radius * 2, self.radius * 2))

    def update(self, dt):
        self.elapsed += dt
        if self.life_time and self.elapsed >= self.life_time:
            self.destroy()

        self.pos = rotate(self.move(), self.angle) + self.origin

    def draw(self, screen):
        screen.blit(self.sprite, self.pos)

    @abstractmethod
    def move(self):
        pass

    def destroy(self):
        EventHandler().notify("DestroyObj", self)

class sinBullet(Bullet):
    def move(self):
        return pygame.Vector2(self.elapsed, math.sin(self.elapsed / 50) * 50)

class straightBullet(Bullet):
    def __init__(self, pos, angle=0, radius=16, life_time=None, owner="enemy", color=(255, 0, 0), speed=6):
        super().__init__(pos, angle=angle, radius=radius, life_time=life_time, owner=owner, color=color)
        self.speed = speed

    def move(self):
        return pygame.Vector2(0, -self.elapsed * self.speed)

class ExplosiveBullet(Bullet):
    def __init__(self, pos, angle=0, radius=8, life_time=1200, owner="player", color=pygame.Color("green"), speed=0.5):
        super().__init__(pos, angle=angle, radius=radius, life_time=life_time, owner=owner, color=color)
        self.speed = speed

    def move(self):
        return pygame.Vector2(0, -self.elapsed * self.speed)

    def explode(self):
        for a in range(0, 360, 45):
            b = straightBullet(
                pos=(self.pos.x, self.pos.y),
                angle=a,
                radius=4,
                life_time=1000,
                owner=self.owner,
                color=pygame.Color("orange"),
                speed=0.6
            )
            EventHandler().notify("SpawnObj", b)
        self.destroy()

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)