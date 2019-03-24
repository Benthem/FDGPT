from Graphstuff import *
from WindowQuery import *
from EllipseStuff import *
import arcade
from math import sin, cos, pi
# pip install hurry.filesize
from hurry.filesize import size

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT
SCREEN_TITLE = "500"
DISPLAY_WEIGHT_AS_FILESIZE = True

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
    H.data.drawbbox(arcade, focus[0], focus[1], focus[2], focus[3], focus[4], focus[5])
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
        # stack of (focusrect, focustype) where 0 = rect, 1 = zoom (different focus functions)
        self.focusstack = []

        # true when mouse is moved
        self.mousechanged = False
        # true when view was translated
        self.viewchanged = False
        self.mousex = 0
        self.mousey = 0
        self.highlighted = None


        # for zoom selection
        self.startx = 0
        self.starty = 0
        self.middledown = False
        self.focusrectoutline = (0, 0, 0, 0)
        self.focus_type = 0

        # for adding to stack when translating view
        self.changedview = False
        self.a = 2

    # the offset for drawing, when focused on rect
    def setfocus(self, rect):
        # zoom constant, 0.5 means 50% of screen width must be covered by focused rectangle width
        zoomc = 0.2
        yoffset = SCREEN_HEIGHT / 4
        focus = [-rect.c[0] + SCREEN_WIDTH / 2, -rect.c[1] + SCREEN_HEIGHT / 2 - yoffset, rect.t, rect.c[0], rect.c[1], SCREEN_WIDTH / rect.y * zoomc]
        return focus

    def setfocus_selection(self, rect):
        focus = [-rect.c[0] + SCREEN_WIDTH / 2, -rect.c[1] + SCREEN_HEIGHT / 2, rect.t, rect.c[0], rect.c[1], SCREEN_WIDTH / rect.x]
        return focus

    def rect_with_focus(self, x, y, w, h, t):
        oldx, oldy = self.translateclick(x, y)
        rect = Rectangle((oldx, oldy), w/self.focus[5], h/self.focus[5], t + self.focus[2], '', 0, None)
        return rect

    def focus_on_selection(self, rect):
        self.startfocus = self.focus[:]
        self.endfocus = self.setfocus_selection(rect)
        self.interpolationcounter = 0
        self.focus_type = 1
        self.changedview = False

    def focus_on(self, rect):
        self.startfocus = self.focus[:]
        self.endfocus = self.setfocus(rect)
        self.interpolationcounter = 0
        self.focus_type = 0
        self.changedview = False

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
                stackelement = self.focusstack.pop()
                self.focusrect = stackelement[0]
                if stackelement[1] == 0:
                    self.focus_on(self.focusrect)
                else:
                    self.focus_on_selection(self.focusrect)
            # reset to current rect
            else:
                if self.focus_type == 0:
                    self.focus_on(self.focusrect)
                else:
                    self.focus_on_selection(self.focusrect)

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

                self.focusstack.append((self.focusrect, self.focus_type))
                self.focusrect = clicked
                self.focus_on(self.focusrect)

        if button == arcade.MOUSE_BUTTON_MIDDLE:
            self.startx = x
            self.starty = y
            self.middledown = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_MIDDLE:
            self.middledown = False
            # we want our rect to be at least 4 pixels to apply it
            if max(math.fabs(self.startx - self.mousex), math.fabs(self.starty - self.mousey)) > 4:
                focusrectoutline = self.rect_with_focus(*self.focusrectoutline, 0)
                self.focusstack.append((self.focusrect, self.focus_type))
                self.focusrect = focusrectoutline
                self.focus_on_selection(focusrectoutline)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mousex = x
        self.mousey = y
        self.mousechanged = True

    def changed_view(self):
        if not self.changedview:
            self.changedview = True
            # push current element on stack
            self.focusstack.append((self.focusrect, self.focus_type))

    # return the first common ancestor, the number of layers between this ancestor and the furthest child, and which one is the furthest
    def common_ancestor(self, node1, node2):
        parent1 = node1.parent
        parent2 = node2.parent
        node1parents = {parent1}
        node2parents = {parent2}
        number_of = 1
        foundcommon = parent1 == parent2
        if foundcommon:
            return parent1, number_of, node1
        while True:
            number_of += 1
            # get parent of node 1, if we are not at root
            if isinstance(parent1, Node):
                parent1 = parent1.parent
                if isinstance(parent1, Node):
                    node1parents.add(parent1)
                    # found first common ancestor
                    if parent1 in node2parents:
                        return parent1, number_of, node1
            # haven't found common: try on other side, if we are not at root here
            if isinstance(parent2, Node):
                parent2 = parent2.parent
                if isinstance(parent2, Node):
                    node2parents.add(parent2)
                    if parent2 in node1parents:
                        return parent2, number_of, node2
            if not isinstance(parent1, Node) and not isinstance(parent2, Node):
                # root
                return parent1, number_of, node1

    def get_ith_parent(self, node, i):
        while i > 0:
            node = node.parent
            i -= 1
        return node

    def force_iteration(self, a = 1):
        # a = 'strength' of iteration
        tree = TreeStruct()

        # build tree from current nodes
        for node in self.nodelist:
            tree.addRect(node.data)

        # get hits
        hits = []
        for node in self.nodelist:
            for rect in tree.query(node.data):
                if check_real_hit(node, rect.node):
                    hits.append((node, rect.node))
        if len(hits) == 0:
            # we are done
            print("No collisions!")
            return True
        print("Number of collisions = ", len(hits))

        # find nodes to modify, set their modification
        n_threshold = 5
        max_b = 3
        min_b = 0.1
        mark_to_increase = set()
        mark_to_decrease = set()
        for hit in hits:
            # find common ancestor
            ancestor, length, furthest_child = self.common_ancestor(hit[0], hit[1])
            # if too far, mark a node in the middle of the path from the furthest to decrease
            if length > n_threshold or ancestor.e_b >= max_b:
                single_ancestor = self.get_ith_parent(furthest_child, min(length/2, n_threshold))
                if single_ancestor.e_b > min_b:
                    mark_to_decrease.add(single_ancestor)
            else:
                # if not, mark to increase b
                mark_to_increase.add(ancestor)

        # set forces
        increaseforce = 0.2 * a
        decreaseforce = -0.2 * a

        forces = [1] * len(self.nodelist)
        for node in mark_to_decrease:
            forces[node.id] += decreaseforce
        for node in mark_to_increase:
            forces[node.id] += increaseforce

        # apply forces
        resetpower = math.pow(0.95, a)
        for i in range(0, len(self.nodelist)):
            self.nodelist[i].e_b *= forces[i]
            # go towards resting state, e_b = 1
            self.nodelist[i].e_b = math.pow(self.nodelist[i].e_b, resetpower)

        # redraw tree
        generalizedPythagorasTree(self.nodelist[0], True, False)
        return False


    def on_key_press(self, key, modifiers):
        """ Called whenever the user presses a key. """
        if key == arcade.key.SPACE:
            for i in range(0, 50):
                if self.force_iteration(max(0.2, self.a)):
                    break
            self.a -= 0.2


        # move camera around
        movespeed = 25
        if key == arcade.key.W:
            self.changed_view()
            self.focus[1] -= movespeed
            if len(self.endfocus) > 1:
                self.endfocus[1] -= movespeed
        if key == arcade.key.S:
            self.changed_view()
            self.focus[1] += movespeed
            if len(self.endfocus) > 1:
                self.endfocus[1] += movespeed
        if key == arcade.key.A:
            self.changed_view()
            self.focus[0] += movespeed
            if len(self.endfocus) > 1:
                self.endfocus[0] += movespeed
        if key == arcade.key.D:
            self.changed_view()
            self.focus[0] -= movespeed
            if len(self.endfocus) > 1:
                self.endfocus[0] -= movespeed

        # rotate camera
        rotation = pi/18
        if key == arcade.key.LEFT:
            self.changed_view()
            self.focus[2] -= rotation
            if len(self.endfocus) > 2:
                self.endfocus[2] -= rotation
        if key == arcade.key.RIGHT:
            self.changed_view()
            self.focus[2] += rotation
            if len(self.endfocus) > 2:
                self.endfocus[2] += rotation

        # zoom camera
        zoomratio = 1.1
        if key == arcade.key.UP:
            self.changed_view()
            self.focus[5] *= zoomratio
            if len(self.endfocus) > 4:
                self.endfocus[5] *= zoomratio
        if key == arcade.key.DOWN:
            self.changed_view()
            self.focus[5] /= zoomratio
            if len(self.endfocus) > 4:
                self.endfocus[5] /= zoomratio

    def set_focus_rect(self):
        rectw = self.startx - self.mousex
        recth = self.starty - self.mousey
        stretch_by_height = math.fabs(rectw) < math.fabs(recth) * SCREEN_RATIO
        if stretch_by_height:
            sign = 1
            if rectw < 0:
                sign = -1
            rectw = math.fabs(recth) * SCREEN_RATIO * sign
        else:
            sign = 1
            if recth < 0:
                sign = -1
            recth = math.fabs(rectw) / SCREEN_RATIO * sign
        rectx = self.startx + rectw * -1 / 2
        recty = self.starty + recth * -1 / 2
        rectw = math.fabs(rectw)
        recth = math.fabs(recth)
        self.focusrectoutline = (rectx, recty, rectw, recth)

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
            if DISPLAY_WEIGHT_AS_FILESIZE:
                arcade.draw_text("%d: %s | size: %s" % (self.highlighted.node.id, self.highlighted.node.name, size(self.highlighted.node.w)), 50, 50, arcade.color.BLACK, 24)
            else:
                arcade.draw_text("%d: %s" % (self.highlighted.node.id, self.highlighted.node.name), 50, 50,
                                 arcade.color.BLACK, 24)

        # draw selection box if applicable
        if self.middledown:
            self.set_focus_rect()
            arcade.draw_rectangle_outline(*self.focusrectoutline, (0, 0, 0, 255), 2, 0)

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
