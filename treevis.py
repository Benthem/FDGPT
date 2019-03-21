from Graphstuff import *
from WindowQuery import *
from EllipseStuff import *
import arcade
from math import sin, cos, pi

SCREEN_HEIGHT = 1000
SCREEN_WIDTH = 1000
SCREEN_TITLE = "500"

FILE = "input/example.in"


def generalizedPythagorasTree(H, rebuild=False, changed=False):
    # no ancestor has changed yet, and we are rebuilding
    if rebuild and not changed:
        # check if this node was changed, and update cache if so
        changed = H.nodeChanged()

    # no changes still from here on, simply recurse on children
    if rebuild and not changed:
        for child in H.children:
            generalizedPythagorasTree(child, rebuild, changed)
        # then return
        return

    R = H.data
    if not H.children:
        return
    f = pi / sum([n.w for n in H.children])
    a = []

    # ellipse shape for the children of this node, x²/a² + y²/b² = 1
    # you don't really wanna change a = 1 as this ensures the tree properly fits
    e_a = 1
    # b moved to node object
    # e_b = list_2
    e_b = H.e_b

    weights = []
    angles = []
    for n in H.children:
        weights.append(n.w)
        angles.append(n.w * f)
    originalangles = angles[:]
    angles = getFixedAngles(e_a, e_b, angles, weights, R.y, 10)

    for i in range(len(H.children)):
        n = H.children[i]
        a.append(angles[i])

        lwidth, langle = getLengthAngle(e_a, e_b, sum(a[:-1]), sum(a), R.y)

        # width (now y-coordinate) of child
        width = lwidth
        # same ratio as before for height
        height = R.x * math.sin(originalangles[i] / 2)

        t = computeSlopeEllipse(R.t, langle)
        c = computeCenterEllipse(R.c, R.x, R.y, R.t, a, width, height, t, e_a, e_b)
        if rebuild:
            n.data.update(c, height, width, t)
        else:
            r = Rectangle(c, height, width, t, n.name, R.depth + 1, n)
            n.data = r
        n.parent = H
        generalizedPythagorasTree(n, rebuild, changed)


def drawGPT(H, focus):
    H.data.draw(arcade, focus[0], focus[1], focus[2], focus[3], focus[4], focus[5])
    # H.data.drawbbox(arcade, focus[0], focus[1], focus[2], focus[3], focus[4], focus[5])
    if not H.children:
        return
    for n in H.children:
        drawGPT(n, focus)


def check_real_hit(node, hit):
    if node.id == 0 or hit.id == 0:
        return False
    # if depth diff > 2
        # just go down both paths
        # keep list of nodes passed
    list_1 = []
    a = node
    while a.id != 0:
        list_1 += [a.parent.id]
        a = a.parent

    list_2 = []
    b = hit
    while b.id != 0:
        if b.id in list_1:
            break
        list_2 += [b.parent.id]
        b = b.parent

    if list_1.index(b.id) < 2 or len(list_2) < 3:
        return False
    '''
    print("---")
    print(node.id, hit.id)
    print(list_1.index(b.id))
    print(list_1, list_2)
    '''
    return True


class MyGame(arcade.Window):
    def interpolate(self, deltatime):
        # interpolate scales with fps
        dspeed = deltatime / (1 / self.fps)

        # don't interpolate if finished
        if self.interpolationcounter >= self.interpolationtime:
            return
        # only interpolate if we have a start/end point (and status)
        if len(self.startfocus) == 0 or len(self.endfocus) == 0 or len(self.focus) == 0:
            return
        # we move the view
        self.viewchanged = True

        for i in range(0, len(self.focus)):
            self.focus[i] += (self.endfocus[i] - self.startfocus[i]) / self.interpolationtime * dspeed
        self.interpolationcounter += 1 * dspeed
        # done interpolating
        if self.interpolationcounter >= self.interpolationtime:
            self.focus = self.endfocus[:]
            self.startfocus = self.focus[:]

    def __init__(self, width, height, title, root, nodes):
        # Call the parent class's init function
        super().__init__(width, height, title)

        # Make the mouse disappear when it is over the window.
        # So we just see our object, not the pointer.
        self.set_mouse_visible(True)

        #arcade.set_background_color(arcade.color.DUTCH_WHITE)
        arcade.set_background_color((255, 255, 255))

        self.root = root
        self.nodelist = nodes
        print(self.nodelist)
        self.r = 0

        self.startfocus = []
        self.endfocus = []
        self.focus = []
        self.fps = 60
        self.interpolationtime = 60
        self.interpolationcounter = 0
        arcade.schedule(self.interpolate, 1 / self.fps)
        self.focusrect = self.nodelist[0].data
        self.focus = self.setfocus(self.focusrect)
        self.startfocus = self.focus[:]
        self.focusstack = []

        # true when mouse is moved
        self.mousechanged = False
        # true when view was translated
        self.viewchanged = False
        self.mousex = 0
        self.mousey = 0
        self.highlighted = None

    # the offset for drawing, when focused on rect
    def setfocus(self, rect):
        # zoom constant, 0.5 means 50% of screen width must be covered by focused rectangle width
        zoomc = 0.2
        yoffset = SCREEN_HEIGHT / 4
        focus = [-rect.c[0] + SCREEN_WIDTH / 2, -rect.c[1] + SCREEN_HEIGHT / 2 - yoffset, rect.t, rect.c[0], rect.c[1], SCREEN_WIDTH / rect.y * zoomc]
        return focus

    def focus_on(self, rect):
        self.startfocus = self.focus[:]
        self.endfocus = self.setfocus(rect)
        self.interpolationcounter = 0

    def translateclick(self, x, y):
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
        return oldx, oldy

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            if len(self.focusstack) > 0:
                self.focusrect = self.focusstack.pop()
                self.focus_on(self.focusrect)

        if button == arcade.MOUSE_BUTTON_LEFT:
            # apply translation for focus in reverse
            oldx, oldy = self.translateclick(x, y)

            clicked = None
            for node in self.nodelist:
                rect = node.data
                if rect.pointinside(oldx, oldy):
                    clicked = rect

            if clicked is not None:
                # add previous to stack to go back to
                print(clicked.node.id)
                if clicked.node.parent != {}:
                    print(clicked.node.parent.id)

                self.focusstack.append(self.focusrect)
                self.focusrect = clicked
                self.focus_on(self.focusrect)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mousex = x
        self.mousey = y
        self.mousechanged = True

    def on_key_press(self, key, modifiers):
        """ Called whenever the user presses a key. """
        if key == arcade.key.SPACE:
            tree = TreeStruct()

            # build tree
            # TODO: handle adding/removing of rects
            for node in self.nodelist:
                tree.addRect(node.data)

            count = 0
            for node in self.nodelist:
                for rect in tree.query(node.data):
                    if check_real_hit(node, rect.node):
                        count += 1
                        handle_real_hit(node, rect.node)
            print(count)
            # self.nodelist[0].e_b += 0.1
            # generalizedPythagorasTree(self.nodelist[0], True, False)

    def on_draw(self):
        # update highlighted element
        if self.mousechanged or self.viewchanged:
            self.highlighted = None

            for node in self.nodelist:
                rect = node.data
                x, y = self.translateclick(self.mousex, self.mousey)
                if rect.pointinside(x, y):
                    self.highlighted = rect

        """ Called whenever we need to draw the window. """
        arcade.start_render()
        drawGPT(self.root, self.focus)
        if self.highlighted is not None:
            arcade.draw_text("%d: %s" % (self.highlighted.node.id, self.highlighted.node.name), 50, 50, arcade.color.BLACK, 24)
        # processed mouse/view changes, set back to false
        self.mousechanged = False
        self.viewchanged = False
        #print("rendered frame")
        #image = arcade.get_image()
        #image.save('screenshot.png', 'PNG')


def handle_real_hit(node, hit):
    hit_strat_one(node, hit)
    # hit_strat_two(node, hit)


# YOERI
def hit_strat_one(node, hit):
    pass


# TOON
def hit_strat_two(node, hit):
    pass


def main():
    with open(FILE, 'r') as f:
        s = f.read().split('\n')
        first = s.pop(0).split()
        n = int(first.pop(0))
        # check if there are names
        if len(first) > 0:
            named = int(first.pop(0)) == 1
        else:
            named = False
        print(named)
        nodes = [Node(i) for i in range(n)]
        root = nodes[0]
        for i in range(n):
            linetosplit = s.pop(0)
            if named:
                split = linetosplit.split('*')
                line = split[0].split()
                name = split[1]
                nodes[i].setName(name)
            else:
                line = linetosplit.split()
            w = line.pop(0)
            nodes[i].w = int(w)
            for j in range(int(line.pop(0))):
                nodes[i].addChild(nodes[int(line.pop(0))])
        #nodes[2].e_b = 0.5
        root.data = Rectangle((250, 100), 100, 100, 0, root.name, 0, nodes[0])
    generalizedPythagorasTree(root)
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, root, nodes)
    arcade.run()


if __name__ == "__main__":
    main()
