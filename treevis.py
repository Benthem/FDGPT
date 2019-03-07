from Graphstuff import *
import arcade
from math import sin, cos, pi

SCREEN_HEIGHT = 1000
SCREEN_WIDTH = 1000
SCREEN_TITLE = "500"

FILE = "input/course.in"


def ellipseCoord(a, b, phi, r):
    polar = (a*b)/(math.sqrt(math.pow(b * math.cos(phi), 2) + math.pow(a * math.sin(phi), 2)))
    x = polar * math.cos(phi) * r
    y = polar * math.sin(phi) * r
    return x, y


def treeToList(root):
    newnodes = [root.data]
    if not root.children:
        return newnodes
    else:
        for child in root.children:
            newnodes.extend(treeToList(child))
        return newnodes


def getLengthAngle(e_a, e_b, previous, current, y):
    # calculate width of child using ellipse coords
    startx, starty = ellipseCoord(e_a, e_b, previous, y)
    endx, endy = ellipseCoord(e_a, e_b, current, y)
    lwidth = math.sqrt(math.pow(endx - startx, 2) + math.pow(endy - starty, 2)) / 2
    # calculate angle of points for use in calculating the angle
    langle = math.atan2(endy - starty, endx - startx)
    return lwidth, langle


def getFixedAngles(e_a, e_b, angles, weights, y, precision):
    totalweights = sum(weights)
    # calculate lenghts
    for j in range(0, precision):
        lengths = []
        for i in range(0, len(angles)):
            width, angle = getLengthAngle(e_a, e_b, sum(angles[:i]), sum(angles[:i+1]), y)
            lengths.append(width)
        # calculate errors
        total = sum(lengths)
        for i in range(0, len(angles)):
            expected = weights[i] / totalweights
            real = lengths[i] / total
            deviation = real / expected
            # adjust
            angles[i] = angles[i] / deviation
        # adjust to make sure we still have pi in total
        overalldeviation = sum(angles) / pi
        for i in range(0, len(angles)):
            angles[i] = angles[i]/overalldeviation
    return angles


def generalizedPythagorasTree(H):
    R = H.data
    if not H.children:
        return
    f = pi / sum([n.w for n in H.children])
    a = []

    # ellipse shape for the children of this node, x²/a² + y²/b² = 1
    # you don't really wanna change a = 1 as this ensures the tree properly fits
    e_a = 1
    e_b = 2

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

        r = Rectangle(c, height, width, t, n.name, R.depth + 1)
        n.data = r
        generalizedPythagorasTree(n)


def drawGPT(H, focus):
    H.data.draw(arcade, focus[0], focus[1], focus[2], focus[3], focus[4], focus[5])
    #H.data.drawbbox(arcade, focus[0], focus[1], focus[2], focus[3], focus[4], focus[5])
    if not H.children:
        return
    for n in H.children:
        drawGPT(n, focus)


def computeSlopeEllipse(Rt, langle):
    t = (langle * -1 - pi + Rt) % (2 * pi)
    if t > pi:
        t -= 2 * pi
    return t


def computeCenterEllipse(Rc, Rx, Ry, Rt, a, width, height, t, e_a, e_b):
    r = Ry/2
    # print('Rx: ' + str(Rx) + ', Ry: ' + str(Ry) + ', Rt: ' + str(Rt) + ', sum(a[:-1]):' + str(sum(a[:-1])) + ', sum(a):' + str(sum(a)))
    # get top of rect
    x, y = translateAtAngle(Rc[0], Rc[1], Rt * -1, 0, Rx / 2)
    dxs, dys = ellipseCoord(e_a, e_b, sum(a[:-1]), r)
    dxe, dye = ellipseCoord(e_a, e_b, sum(a), r)
    # map to our coords
    sx, sy = translateAtAngle(x, y, Rt * -1, dxs, dys)
    ex, ey = translateAtAngle(x, y, Rt * -1, dxe, dye)

    # middle of 2 ellipse points
    mx = (ex + sx) / 2
    my = (ey + sy) / 2
    # offset them to new center
    fx, fy = translateAtAngle(mx, my, t * -1, 0, height / 2)
    # return
    return fx, fy


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
        self.fps = 60
        self.interpolationtime = 60
        self.interpolationcounter = 0
        arcade.schedule(self.interpolate, 1 / self.fps)
        self.focusrect = self.nodelist[0]
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
            for rect in self.nodelist:
                if rect.pointinside(oldx, oldy):
                    clicked = rect

            if clicked is not None:
                # add previous to stack to go back to
                self.focusstack.append(self.focusrect)
                self.focusrect = clicked
                self.focus_on(self.focusrect)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mousex = x
        self.mousey = y
        self.mousechanged = True


    def on_draw(self):
        # update highlighted element
        if self.mousechanged or self.viewchanged:
            self.highlighted = None
            for rect in self.nodelist:
                x, y = self.translateclick(self.mousex, self.mousey)
                if rect.pointinside(x, y):
                    self.highlighted = rect

        """ Called whenever we need to draw the window. """
        arcade.start_render()
        drawGPT(self.root, self.focus)
        if self.highlighted is not None:
            arcade.draw_text(self.highlighted.name, 50, 50, arcade.color.BLACK, 24)
        # processed mouse/view changes, set back to false
        self.mousechanged = False
        self.viewchanged = False


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

        root.data = Rectangle((250, 100), 100, 100, 0, root.name, 0)
    generalizedPythagorasTree(root)
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, root)
    arcade.run()


if __name__ == "__main__":
    main()
