import math
from math import pi, cos, sin
from EllipseStuff import translateAtAngle
import csv
import sys

# let me use global variables mr python
graphstuff = sys.modules[__name__]

# should probably hand pick these colours, now a simple transition from R to B and B to G
colors = []
colortransition = 3
# R -> B
for i in range(0, colortransition + 1):
    colors.append((int(255 - (255 / colortransition) * i), 0, int(0 + (255 / colortransition) * i), 100))
# B-> G
for i in range(0, colortransition + 1):
    colors.append((0, int(0 + (255 / colortransition) * i), int(255 - (255 / colortransition) * i), 100))

alpha = 200
graphstuff.max_depth = 0
# load colors from plasma.csv
plasma = []
with open('plasma_mod.csv') as f:
    csv_reader = csv.reader(f, delimiter=',')
    for color in csv_reader:
        plasma.append((int(color[0]), int(color[1]), int(color[2]), alpha))
# reverse
plasma.reverse()

class Node(object):
    def __init__(self, id, weight=0, data=None, parent=None):
        self.id = id
        self.w = weight
        self.data = data
        self.children = []
        self.parent = parent
        self.name = ''
        self.e_b = 1.0
        self.e_b_cache = 1.0

        self.strat_one = {}
        self.strat_two = {}

    def nodeChanged(self):
        if self.e_b_cache != self.e_b:
            self.e_b_cache = self.e_b
            return True
        return False

    def addChild(self, child):
        self.children.append(child)

    def setName(self, name):
        self.name = name

    def __str__(self):
        return "i%d w%d : %s" % (self.id, self.w, [n.id for n in self.children])

    def __repr__(self):
        return "%s" % self


class Rectangle(object):

    def __init__(self, c, x, y, t, name, depth, node):
        self.c = c
        self.x = x
        self.y = y
        self.t = t
        self.depth = depth
        self.node = node
        self.setbbox()
        if depth > graphstuff.max_depth:
            graphstuff.max_depth = depth

    def update(self, c, x, y, t):
        self.c = c
        self.x = x
        self.y = y
        self.t = t
        self.setbbox()

    def setbbox(self):
        self.corners = [translateAtAngle(*self.c, -self.t, self.y / 2, self.x / 2)]
        self.corners += [translateAtAngle(*self.c, -self.t, -self.y / 2, self.x / 2)]
        self.corners += [translateAtAngle(*self.c, -self.t, self.y / 2, -self.x / 2)]
        self.corners += [translateAtAngle(*self.c, -self.t, -self.y / 2, -self.x / 2)]

        xs, ys = zip(*self.corners)
        self.bbox = (min(xs), min(ys), max(xs), max(ys))

    def overlaps(self, rect):
        return any([self.pointinside(*corner) for corner in rect.corners])

    def pointinside(self, x, y):
        # rotate locally per rect to check if it falls inside
        nx = x - self.c[0]
        ny = y - self.c[1]
        rx = nx * cos(self.t) - ny * sin(self.t)
        ry = nx * sin(self.t) + ny * cos(self.t)
        rx += self.c[0]
        ry += self.c[1]
        return math.fabs(rx - self.c[0]) < self.y / 2 and math.fabs(ry - self.c[1]) < self.x / 2

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
        # print(self.c)
        color_index = max(0, min(int(self.depth / graphstuff.max_depth * len(plasma)), len(plasma) - 1))
        color = plasma[color_index]
        arcade.draw_rectangle_filled(
            *self.offsetpoint(self.c[0], self.c[1], dx, dy, dt, (rx, ry), zoom),
            self.x * zoom,
            self.y * zoom,
            color=color,
            tilt_angle=(pi / 2 - self.t + dt) * 180 / 3.141592)

    def __str__(self):
        return "%d:\tc%d,%d x%d y%d t%f" % (self.node.id, *self.c, self.x, self.y, self.t)

    def __repr__(self):
        return "%s" % self
