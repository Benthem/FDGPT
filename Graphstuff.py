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

    def draw(self, arcade):
        print(self)
        arcade.draw_rectangle_filled(
                *self.c, 
                self.x,
                self.y, 
                color=(255, 0, 0, 100),
                tilt_angle=self.t*360/3.141592)

    def __str__(self):
        return "c%d,%d x%d y%d t%f" % (*self.c, self.x, self.y, self.t)

    def __repr__(self):
        return "%s" % self
