import pygame

class Collide:

    @staticmethod
    def polygon(a, b):
        if not a.bounding_box.colliderect(b.bounding_box):
            return None

        min_overlap = float('inf')
        smallest_axis = None

        for shape_a in a.convex_shapes:
            for shape_b in b.convex_shapes:
                res = Collide.convex(shape_a.points, shape_b.points)
                if res is not None:
                    overlap, axis = res
                    if overlap < min_overlap:
                        min_overlap = overlap
                        smallest_axis = axis

        if smallest_axis is not None:
            center_a = Collide.get_center(a.points)
            center_b = Collide.get_center(b.points)
            if (center_a - center_b).dot(smallest_axis) < 0:
                smallest_axis = -smallest_axis

            return min_overlap, smallest_axis

        return None

    @staticmethod
    def convex(a, b):
        overlap = float('inf')
        smallest_axis = None

        axes = Collide.axes(a) + Collide.axes(b)
        for axis in axes:
            min_a, max_a = Collide.project(a,axis)
            min_b, max_b = Collide.project(b,axis)

            if max_a < min_b or max_b < min_a:
                return None

            o = min(max_a, max_b) - max(min_a, min_b)
            if o < overlap:
                overlap = o
                smallest_axis = axis

        return overlap, smallest_axis

    @staticmethod
    def axes(points):
        axes = []
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            edge = p2 - p1
            normal = pygame.Vector2(-edge.y, edge.x)
            if normal.length_squared() > 0:
                axes.append(normal.normalize())
        return axes

    @staticmethod
    def project(points, axis):
        values = [p.dot(axis) for p in points]
        return min(values), max(values)

    @staticmethod
    def get_center(points):
        x = sum(p.x for p in points) / len(points)
        y = sum(p.y for p in points) / len(points)
        return pygame.Vector2(x,y)