import pygame
import random
from util import EventHandler

class PowerUp:
    TYPES = ['invincible', 'shotgun', 'smg', 'grenade', 'timeslow','heal']
    COLORS = {
        'invincible': pygame.Color("yellow"),
        'shotgun': pygame.Color("orange"),
        'smg': pygame.Color("cyan"),
        'grenade': pygame.Color("green"),
        'timeslow': pygame.Color("white"),
        'heal': pygame.Color("pink")
    }

    def __init__(self, pos, ptype=None):
        self.pos = pygame.Vector2(pos)
        self.type = ptype if ptype else random.choice(PowerUp.TYPES)
        self.radius = 12
        self.speed = 0.1  # Velocidade de queda em px/ms

    def update(self, dt):
        self.pos.y += self.speed * dt
        if self.pos.y > 600 + self.radius:
            EventHandler().notify("DestroyObj", self)

    def draw(self, screen):
        color = PowerUp.COLORS[self.type]
        pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(screen, pygame.Color("white"), (int(self.pos.x), int(self.pos.y)), self.radius, 2)