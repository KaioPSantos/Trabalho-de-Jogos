import pygame
import math
from shape import Polygon
from collision import Collide

class Ball:
    def __init__(self, x, y, sprite, radius=12, num_sides=12):
        self.spawn_pos = pygame.Vector2(x, y)
        self.launched = False
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.radius = radius
        self.num_sides = num_sides
        self.angle = 0
        
        self.gravity = pygame.Vector2(0, 600)

        self.image = sprite
        
        self.shape = Polygon(self.get_circle_points(), is_subshape=True)

    def get_circle_points(self):
        points = []
        for i in range(self.num_sides):
            angle = (2* math.pi / self.num_sides) * i
            px = self.pos.x + self.radius * math.cos(angle)
            py = self.pos.y + self.radius * math.sin(angle)
            points.append(pygame.Vector2(px, py))
        return points

    def launch(self, target_pos, min_speed=250, max_speed=900):
        if not self.launched:
            direction = pygame.Vector2(target_pos) - self.pos
            dist = direction.length()
            if dist > 0:
                clamped_dist = max(30, min(dist, 300))
                factor = (clamped_dist - 30) / (300 - 30)
                speed = min_speed + factor * (max_speed - min_speed)
                
                self.vel = direction.normalize() * speed
            else:
                self.vel = pygame.Vector2(0, min_speed)
            self.launched = True

    def reset(self):
        self.pos = pygame.Vector2(self.spawn_pos)
        self.vel = pygame.Vector2(0, 0)
        self.launched = False
        self.shape.points = self.get_circle_points()
        self.shape.update_geometry()
        self.angle = 0

    def update(self, dt):
        if not self.launched:
            return
        
        self.vel += self.gravity * dt

        self.pos += self.vel * dt

        rot_speed = self.vel.x if abs(self.vel.x) > 50 else 180
        self.angle -= rot_speed * dt

        self.shape.points = self.get_circle_points()
        self.shape.update_geometry()

    def draw(self, screen, mouse_pos=None):
        if not self.launched and mouse_pos is not None:
            direction = pygame.Vector2(mouse_pos) - self.pos
            dist = direction.length()
            if dist > 0:
                clamped_dist = max(30, min(dist, 300))
                factor = (clamped_dist - 30) / (300 - 30)
                
                aim_len = 30 + factor * 70
                aim_end = self.pos + direction.normalize() * aim_len
                
                r = int(255 * factor)
                g = int(255 * (1 - factor))
                
                pygame.draw.line(screen, (r, g, 50), self.pos, aim_end, 3)

        rotated_image = pygame.transform.rotate(self.image, self.angle)
        rect = rotated_image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        screen.blit(rotated_image, rect)

    def bounce_off_polygon(self, polygon):
        if not self.launched:
                    return
        
        collision = Collide.polygon(self.shape, polygon)
        if collision is not None:
            polygon.trigger_hit()
            overlap, normal = collision

            self.pos += normal * overlap

            vel_dot_normal = self.vel.dot(normal)
            if vel_dot_normal < 0:
                self.vel -= 1.8 * vel_dot_normal * normal

            self.shape.points = self.get_circle_points()
            self.shape.update_geometry()
            return True
        return False