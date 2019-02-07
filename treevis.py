import Graphstuff as G
import arcade
from math import sin, cos, pi

SCREEN_HEIGHT = 500
SCREEN_WIDTH = 500
SCREEN_TITLE = "500"


def generalizedPythagorasTree(H, arcade):
    R = H.data
    R.draw(arcade)
    if not H.children: 
        return
    f = pi / sum([n.w for n in H.children])
    a = []
    for i in range(len(H.children)):
        n = H.children[i]
        a.append(n.w * f)
        x = R.x * sin(a[i]/2)
        y = R.y * sin(a[i]/2)
        c = computeCenter(R.c, R.x, R.y, R.t, a, x, y)
        t = computeSlope(R.t, a)
        r = G.Rectangle(c, x, y, t)
        n.data = r
        generalizedPythagorasTree(n, arcade)


def computeCenter(Rc, Rx, Ry, Rt, a, x, y):
    ap = sum(a[:-1]) + a[-1]/2
    l = y/2 + abs(cos(ap) * Rx/2)
    dx = cos(ap) * l
    dy = sin(ap) * l
    return (Rc[0] + sin(Rt)*Rx/2 + dx, Rc[1] + cos(Rt)*Ry/2 + dy)


def computeSlope(Rt, a):
    # yikes
    return Rt + sum(a[:-1]) + a[-1]/2 + 0.3


class MyGame(arcade.Window):
    def __init__(self, width, height, title, root):
        # Call the parent class's init function
        super().__init__(width, height, title)

        # Make the mouse disappear when it is over the window.
        # So we just see our object, not the pointer.
        self.set_mouse_visible(True)

        arcade.set_background_color(arcade.color.DUTCH_WHITE)

        self.root = root

    def on_draw(self):
        """ Called whenever we need to draw the window. """
        arcade.start_render()
        generalizedPythagorasTree(self.root, arcade)


def main():
    with open('sometree.in', 'r') as f:
        s = f.read().split('\n')
        n = int(s.pop(0))
        nodes = [G.Node(i) for i in range(n)]
        root = nodes[0]
        for i in range(n):
            l = s.pop(0).split()
            w = l.pop(0)
            nodes[i].w = int(w)
            for j in range(int(l.pop(0))):
                nodes[i].addChild(nodes[int(l.pop(0))])

    root.data = G.Rectangle((250, 100), 100, 100, 0)
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, root)
    arcade.run()


if __name__ == "__main__":
    main()
