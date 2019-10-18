#!/usr/bin/env python3

import os

from Graphstuff import *
from WindowQuery import *
from EllipseStuff import *
import arcade
import pickle
import codecs
import sys
from math import sin, cos, pi
# pip install hurry.filesize
from hurry.filesize import size

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT
DISPLAY_WEIGHT_AS_FILESIZE = True
ROOTID = 0
MAX_B = (1 + math.sqrt(5)) / 2

FILE = "input/selfsimilar_hierarchy_degree5_depth10_selfSimilar.in"
BESTFILE = ""
BESTFILE_LR = ""
BESTFILE_SCORE = ""
BESTFILE_ROOT = ""
BESTFILE_ROOT_LR = ""
BESTFILE_ROOT_SCORE = ""

# zoom constant, 0.5 means 50% of screen width must be covered by focused rectangle width
ZOOMC = 0.12
RENDER_UNTIL_DONE = False
# quadtree for calculating hits
tree = TreeStruct()

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
        #SQUARE
        height = lwidth
        #height = R.x * math.sin(originalangles[i] / 2)
        #height = min(height, width)

        t = computeSlopeEllipse(R.t, langle)
        c = computeCenterEllipse(R.c, R.x, R.y, R.t, a, width, height, t, e_a, e_b)
        if rebuild:
            if (n.data.c, n.data.x, n.data.y, n.data.t) != (c, height, width, t):
                tree.removeRect(n.data)
                n.data.update(c, height, width, t)
                tree.addRect(n.data)
        else:
            r = Rectangle(c, height, width, t, n.name, R.depth + 1, n)
            n.data = r
            tree.addRect(r)
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
    if node.id == hit.parent.id:
        return False
    if hit.id == node.parent.id:
        return False
    if hit.parent.id == node.parent.id:
        return False
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
        self.fps = 60

        # Make the mouse disappear when it is over the window.
        # So we just see our object, not the pointer.
        self.set_mouse_visible(True)

        # arcade.set_background_color(arcade.color.DUTCH_WHITE)
        arcade.set_background_color((255, 255, 255))

        self.root = root
        self.nodelist = nodes
        # print(self.nodelist)
        self.r = 0

        # STRAT STUFF
        arcade.schedule(self.force_strategy, 0.05)
        if RENDER_UNTIL_DONE:
            self.i = 1
        else:
            self.i = 0

        self.startfocus = []
        self.endfocus = []
        self.focus = []
        self.interpolationtime = 60
        self.interpolationcounter = 0
        arcade.schedule(self.interpolate, 1 / self.fps)
        self.focusrect = self.nodelist[ROOTID].data
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
        self.bestvalue = math.inf
        self.best = [1] * len(self.nodelist)

    # the offset for drawing, when focused on rect
    def setfocus(self, rect):
        yoffset = SCREEN_HEIGHT / 4
        focus = [-rect.c[0] + SCREEN_WIDTH / 2, -rect.c[1] + SCREEN_HEIGHT / 2 - yoffset, rect.t, rect.c[0], rect.c[1], SCREEN_WIDTH / rect.y * ZOOMC]
        return focus

    def setfocus_selection(self, rect):
        focus = [-rect.c[0] + SCREEN_WIDTH / 2, -rect.c[1] + SCREEN_HEIGHT / 2, rect.t, rect.c[0], rect.c[1], SCREEN_WIDTH / rect.x]
        return focus

    def rect_with_focus(self, x, y, w, h, t):
        oldx, oldy = self.translateclick(x, y)
        rect = Rectangle((oldx, oldy), w / self.focus[5], h / self.focus[5], t + self.focus[2], '', 0, None)
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

    def count_hits(self, handle=False):
        count = 0
        for node in self.nodelist:
            for rect in tree.query(node.data):
                if check_real_hit(node, rect.node):
                    count += 1
                    if handle:
                        handle_real_hit(node, rect.node)
        return math.ceil(count / 2)

    def force_strategy(self, dt):
        if self.i == 0:
            return
        print("counting hits")
        before = self.count_hits(True)
        print("it: %d\t%d collissions" % (self.i, before))
        if before == 0:
            self.i = 0
            print("No more collisions!")    
            return
        for node in self.nodelist:
            if node.strat_two.get('common', 0) > node.strat_two.get('path', 0):
                node.e_b = min(1.1 * node.e_b, MAX_B)
            elif node.strat_two.get('common', 0) < node.strat_two.get('path', 0):
                node.e_b *= 0.9
            node.e_b += (1 - node.e_b) * node.strat_two.get('LR', 0.1)
            node.strat_two['LR'] = node.strat_two.get('LR', 0.1) * 0.9
            node.strat_two['common'] = 0
            node.strat_two['path'] = 0
        # self.nodelist[ROOTID].e_b += 0.1
        generalizedPythagorasTree(self.nodelist[ROOTID], True, False)
        after = self.count_hits()
        self.update_best(after)
        if not RENDER_UNTIL_DONE:
            self.i -= 1
        if after == 0:
            self.i = 0
            print("No more collisions!")

    def reset(self):
        self.i = 0
        self.bestvalue = math.inf
        self.best = [1] * len(self.nodelist)
        for node in self.nodelist:
            node.strat_two['LR'] = 0.1
        self.set_best()

    def set_best(self, recount=False):
        for i in range(0, len(self.nodelist)):
            self.nodelist[i].e_b = self.best[i]
        generalizedPythagorasTree(self.nodelist[ROOTID], True, False)
        # setting best
        if recount:
            self.bestvalue = self.count_hits()
        print("Set to best configuration, " + str(self.bestvalue) + " hits")

    def update_best(self, hits):
        if hits < self.bestvalue:
            self.bestvalue = hits
            # check if this is better than what we have stored on disk
            savedscore = math.inf
            if os.path.exists(BESTFILE_SCORE):
                with open(BESTFILE_SCORE, 'r') as f:
                    savedscore = int(f.read())
            if self.bestvalue < savedscore:
                print("New best score found, writing to file")
                LR = []
                for node in self.nodelist:
                    LR.append(node.strat_two.get('LR', 0.1))
                with open(BESTFILE_LR, "wb") as f:
                    pickle.dump(LR, f)
                for i in range(0, len(self.nodelist)):
                    self.best[i] = self.nodelist[i].e_b
                with open(BESTFILE, "wb") as f:
                    pickle.dump(self.best, f)
                with open(BESTFILE_SCORE, 'w') as f:
                    f.write(str(self.bestvalue))

    def load_best(self):
        if os.path.isfile(BESTFILE):
            with open(BESTFILE, "rb") as f:
                self.best = pickle.load(f)
            if os.path.isfile(BESTFILE_LR):
                with open(BESTFILE_LR, "rb") as f:
                    LR = pickle.load(f)
                    for node in self.nodelist:
                        node.strat_two['LR'] = LR.pop(0)
            if os.path.isfile(BESTFILE_SCORE):
                with open(BESTFILE_SCORE, 'r') as f:
                    self.bestvalue = int(f.read())
            return True
        else:
            return False

    def load_best_from_root(self):
        if os.path.isfile(BESTFILE_ROOT):
            with open(BESTFILE_ROOT, "rb") as f:
                root_best = pickle.load(f)
        else:
            return False
        if os.path.isfile(BESTFILE_ROOT_LR):
            with open(BESTFILE_ROOT_LR, "rb") as f:
                LR = pickle.load(f)
        # new node array is sorted as well, merge in O(n)
        pointer = 0
        for i in range(0, len(root_best)):
            if pointer < len(self.nodelist) and self.nodelist[pointer].id == i:
                self.best[pointer] = root_best[i]
                if LR is not None:
                    self.nodelist[pointer].strat_two['LR'] = LR[i]
                pointer += 1
        return True

    def on_key_press(self, key, modifiers):
        """ Called whenever the user presses a key. """
        if key == arcade.key.SPACE:
            # run the force strategy for 50 iterations
            self.i = 50
        if key == arcade.key.LSHIFT:
            if self.bestvalue < math.inf:
                self.set_best()
            else:
                print("No best found")
        if key == arcade.key.LCTRL:
            success = self.load_best()
            print("Loaded best from " + BESTFILE)
            if success:
                self.set_best(False)
            else:
                print("No stored configuration found")
        if key == arcade.key.LALT:
            success = self.load_best_from_root()
            print("Loaded best from " + BESTFILE_ROOT)
            if success:
                self.set_best(False)
                self.update_best(self.count_hits())
            else:
                print("No stored configuration found")

        if key == arcade.key.R:
            self.reset()

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
        rotation = pi / 18
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
                arcade.draw_text("%d: %s | weight: %s" % (self.highlighted.node.id, self.highlighted.node.name, self.highlighted.node.w), 50, 50,
                                 arcade.color.BLACK, 24)

        # draw selection box if applicable
        if self.middledown:
            self.set_focus_rect()
            arcade.draw_rectangle_outline(*self.focusrectoutline, (0, 0, 0, 255), 2, 0)

        # processed mouse/view changes, set back to false
        self.mousechanged = False
        self.viewchanged = False
        if RENDER_UNTIL_DONE:
            screenshotname = FILE[:-3] + '_' + str(self.i) + '.png'
            print("rendered " + screenshotname)
            image = arcade.get_image()
            image.save(screenshotname, 'PNG')
            self.i += 1
        #self.focus[5] *= 0.8



# TOON
def handle_real_hit(node, hit):
    list_1 = []
    a = node
    while a.parent is not None:
        list_1 += [a.parent]
        a = a.parent

    list_2 = []
    b = hit
    while b is not None:
        if b.id in [n.id for n in list_1]:
            b.strat_two['common'] = b.strat_two.get('common', 0) + 1
            break
        list_2 += [b.parent]
        b = b.parent

    # mark nodes
    for node in list_2[:-1]:
        node.strat_two['path'] = node.strat_two.get('path', 0) + 1

    for node in list_1:
        if node.id == b.id:
            break
        node.strat_two['path'] = node.strat_two.get('path', 0) + 1


def main():
    global ROOTID
    global FILE, BESTFILE, BESTFILE_LR, BESTFILE_SCORE, BESTFILE_ROOT,BESTFILE_ROOT_LR, BESTFILE_ROOT_SCORE
    
    if (len(sys.argv) >= 2):
        FILE = sys.argv[1]
        if not os.path.isfile(FILE):
            print("File not found.")
            return
        if (len(sys.argv) >= 3):
            try:
                ROOTID = int(sys.argv[2])
            except ValueError:
                print("Invalid root ID.")
                return
    
    # filenames
    BESTFILE = FILE[:-3] + "_" + str(ROOTID) + ".pickle"
    BESTFILE_LR = FILE[:-3] + "_" + str(ROOTID) + "_LR.pickle"
    BESTFILE_SCORE = FILE[:-3] + "_" + str(ROOTID) + ".txt"
    BESTFILE_ROOT = FILE[:-3] + "_0.pickle"
    BESTFILE_ROOT_LR = FILE[:-3] + "_0_LR.pickle"
    BESTFILE_ROOT_SCORE = FILE[:-3] + "_0.txt"
    
    with open(FILE, 'r') as f:
        s = f.read().split('\n')
        first = s.pop(0).split()
        n = int(first.pop(0))
        # check if there are names
        if len(first) > 0:
            named = int(first.pop(0)) == 1
        else:
            named = False
        # print(named)
        nodes = [Node(i) for i in range(n)]
        if not (ROOTID >= 0 and ROOTID < len(nodes)):
            print("Root ID out of range.")
            return
        root = nodes[ROOTID]
        mock = Node(-1)
        root.parent = mock
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
        # nodes[2].e_b = 0.5
        root.data = Rectangle((250, 100), 100, 100, 0, root.name, 0, nodes[ROOTID])
    print("Total nodes:", len(nodes))
    print("Generating tree")
    generalizedPythagorasTree(root)
    print("Finding nodes to keep")
    newnodes = []
    for node in nodes:
        if node.data is not None:
            newnodes.append(node)
    print("Total nodes:", len(newnodes))
    ROOTID = newnodes.index(root)
    Screen_title = FILE[6:-3]
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, Screen_title, root, newnodes)
    arcade.run()


if __name__ == "__main__":
    main()
