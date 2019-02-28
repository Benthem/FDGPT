import math
from math import pi, cos, sin


def translateAtAngle(x, y, angle, dx, dy):
    x = x + dx * cos(angle) - dy * sin(angle)
    y = y + dx * sin(angle) + dy * cos(angle)
    return x, y


class Node(object):
    def __init__(self, id, weight=0, data={}):
        self.id = id
        self.w = weight
        self.data = data
        self.children = []

    def addChild(self, child):
        self.children.append(child)

    def __str__(self):
        return "i%d w%d : %s" % (self.id, self.w, [n.id for n in self.children])

    def __repr__(self):
        return "%s" % self


class Rectangle(object):

    def __init__(self, c, x, y, t):
        self.c = c
        self.x = x
        self.y = y
        self.t = t

        self.corners = [translateAtAngle(*c, t, y / 2, x / 2)]
        self.corners += [translateAtAngle(*c, t, -y / 2, x / 2)]
        self.corners += [translateAtAngle(*c, t, y / 2, -x / 2)]
        self.corners += [translateAtAngle(*c, t, -y / 2, -x / 2)]

        xs, ys = zip(*corners)
        self.bbox = (min(xs), min(ys), max(xs), max(ys))

    def offsetpoint(self, px, py, dx, dy, dt, rc, zoom):
        # print('Old values for rect (' + str(self.c[0]) + ', ' + str(self.c[1]) + ')')
        # rotate around rc
        cx = px - rc[0]
        cy = py - rc[1]
        newx = cx * math.cos(dt) - cy * math.sin(dt)
        newy = cx * math.sin(dt) + cy * math.cos(dt)
        # translate back and apply dx, dy
        newx *= zoom
        newy *= zoom
        newx += dx + rc[0]
        newy += dy + rc[1]
        # print('New values for rect (' + str(newx) + ', ' + str(newy) + ')')

        return newx, newy

    def drawbbox(self, arcade, dx, dy, dt, rx, ry, zoom):
        p1 = self.offsetpoint(self.bbox[0], self.bbox[1], dx, dy, dt, (rx, ry), zoom)
        p2 = self.offsetpoint(self.bbox[0], self.bbox[3], dx, dy, dt, (rx, ry), zoom)
        p3 = self.offsetpoint(self.bbox[2], self.bbox[3], dx, dy, dt, (rx, ry), zoom)
        p4 = self.offsetpoint(self.bbox[2], self.bbox[1], dx, dy, dt, (rx, ry), zoom)
        arcade.draw_polygon_filled((p1, p2, p3, p4), color=(0, 255, 0, 100))

    def draw(self, arcade, dx, dy, dt, rx, ry, zoom):
        print(self.c)
        arcade.draw_rectangle_filled(
            *self.offsetpoint(self.c[0], self.c[1], dx, dy, dt, (rx, ry), zoom),
            self.x * zoom,
            self.y * zoom,
            color=(255, 0, 0, 100),
            tilt_angle=(pi / 2 - self.t + dt) * 180 / 3.141592)

    def __str__(self):
        return "c%d,%d x%d y%d t%f" % (*self.c, self.x, self.y, self.t)

    def __repr__(self):
        return "%s" % self
