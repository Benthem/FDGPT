import math
import random

import Graphstuff as G
import arcade
from math import sin, cos, pi

SCREEN_HEIGHT = 1000
SCREEN_WIDTH = 1000
SCREEN_TITLE = "500"

FILE = "input/filetree.in"


def treeToList(root):
    newnodes = [root.data]
    if not root.children:
        return newnodes
    else:
        for child in root.children:
            newnodes.extend(treeToList(child))
        return newnodes


def generalizedPythagorasTree(H):
    R = H.data
    if not H.children:
        return
    f = pi / sum([n.w for n in H.children])
    a = []
    for i in range(len(H.children)):
        n = H.children[i]
        a.append(n.w * f)
        x = R.x * sin(a[i] / 2)
        y = R.y * sin(a[i] / 2)

        c = computeCenter(R.c, R.x, R.y, R.t, a, x, y)

        t = computeSlope(R.t, a)

        r = G.Rectangle(c, x, y, t)
        n.data = r
        generalizedPythagorasTree(n)


def drawGPT(H, focus):
    H.data.draw(arcade, focus[0], focus[1], focus[2],
                focus[3], focus[4], focus[5])
    if not H.children:
        return
    for n in H.children:
        drawGPT(n, focus)


def computeCenter(Rc, Rx, Ry, Rt, a, x, y):
    ap = sum(a[:-1]) + a[-1] / 2
    length = y / 2 + abs(cos(a[-1] / 2) * Rx / 2)
    print(length)
    dx = -cos(ap + Rt) * length
    dy = sin(ap + Rt) * length

    arcade.draw_circle_filled(
        Rc[0] + sin(Rt) * Rx / 2, Rc[1] + cos(Rt) * Ry / 2, 2, arcade.color.GREEN)
    return (Rc[0] + sin(Rt) * Rx / 2 + dx, Rc[1] + cos(Rt) * Ry / 2 + dy)


def computeSlope(Rt, a):
    return Rt + sum(a[:-1]) + a[-1] / 2 - pi / 2


class MyGame(arcade.Window):
    def interpolate(self, deltatime):
        # don't interpolate if finished
        if self.interpolationcounter >= self.interpolationtime:
            return
        # only interpolate if we have a start/end point (and status)
        if len(self.startfocus) == 0 or len(self.endfocus) == 0 or len(self.focus) == 0:
            return
        for i in range(0, len(self.focus)):
            self.focus[i] += (self.endfocus[i] - self.startfocus[i]) / self.interpolationtime
        self.interpolationcounter += 1
        # done interpolating
        if self.interpolationcounter == self.interpolationtime:
            self.startfocus = self.focus[:]

    def __init__(self, width, height, title, root):
        # Call the parent class's init function
        super().__init__(width, height, title)

        # Make the mouse disappear when it is over the window.
        # So we just see our object, not the pointer.
        self.set_mouse_visible(True)

        arcade.set_background_color(arcade.color.DUTCH_WHITE)

        self.root = root
        self.nodelist = treeToList(self.root)
        print(self.nodelist)
        self.r = 0

        self.startfocus = []
        self.endfocus = []
        self.focus = []
        self.interpolationtime = 60
        self.interpolationcounter = 0
        arcade.schedule(self.interpolate, 1 / 60)
        self.focusrect = self.nodelist[0]
        self.focus = self.setfocus(self.focusrect)
        self.startfocus = self.focus[:]
        self.focusstack = []

    # the offset for drawing, when focused on rect
    def setfocus(self, rect):
        # zoom constant, 0.5 means 50% of screen width must be covered by focused rectangle width
        zoomc = 0.2
        yoffset = SCREEN_HEIGHT / 4
        focus = [-rect.c[0] + SCREEN_WIDTH / 2, -rect.c[1] + SCREEN_HEIGHT / 2 - yoffset, rect.t, rect.c[0], rect.c[1], SCREEN_WIDTH / rect.x * zoomc]
        return focus

    def focus_on(self, rect):
        self.startfocus = self.focus[:]
        self.endfocus = self.setfocus(rect)
        self.interpolationcounter = 0

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            if len(self.focusstack) > 0:
                self.focusrect = self.focusstack.pop()
                self.focus_on(self.focusrect)

        if button == arcade.MOUSE_BUTTON_LEFT:
            # apply translation for focus in reverse
            newx = x - self.focus[0] - self.focus[3]
            newy = y - self.focus[1] - self.focus[4]
            newx /= self.focus[5]
            newy /= self.focus[5]
            oldx = newx * cos(-1 * self.focus[2]) - \
                newy * sin(-1 * self.focus[2])
            oldy = newx * sin(-1 * self.focus[2]) + \
                newy * cos(-1 * self.focus[2])
            oldx += self.focus[3]
            oldy += self.focus[4]

            clicked = None
            for rect in self.nodelist:
                # rotate locally per rect to check if it falls inside
                nx = oldx - rect.c[0]
                ny = oldy - rect.c[1]
                rx = nx * cos(rect.t) - ny * sin(rect.t)
                ry = nx * sin(rect.t) + ny * cos(rect.t)
                rx += rect.c[0]
                ry += rect.c[1]
                if math.fabs(rx - rect.c[0]) < rect.x / 2 and math.fabs(ry - rect.c[1]) < rect.y / 2:
                    clicked = rect

            if clicked is not None:
                # add previous to stack to go back to
                self.focusstack.append(self.focusrect)
                self.focusrect = clicked
                self.focus_on(self.focusrect)

    def on_draw(self):
        """ Called whenever we need to draw the window. """
        arcade.start_render()
        drawGPT(self.root, self.focus)


def main():
    with open(FILE, 'r') as f:
        s = f.read().split('\n')
        n = int(s.pop(0))
        nodes = [G.Node(i) for i in range(n)]
        root = nodes[0]
        for i in range(n):
            line = s.pop(0).split()
            w = line.pop(0)
            nodes[i].w = int(w)
            for j in range(int(line.pop(0))):
                nodes[i].addChild(nodes[int(line.pop(0))])

        root.data = G.Rectangle((250, 100), 100, 100, 0)
    generalizedPythagorasTree(root)
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, root)
    arcade.run()


if __name__ == "__main__":
    main()
