from math import sin, cos, pi, sqrt, pow, atan2

def computeSlopeEllipse(Rt, langle):
    t = (langle * -1 - pi + Rt) % (2 * pi)
    if t > pi:
        t -= 2 * pi
    return t


def computeCenterEllipse(Rc, Rx, Ry, Rt, a, width, height, t, e_a, e_b):
    r = Ry / 2
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


def ellipseCoord(a, b, phi, r):
    polar = (a * b) / (sqrt(pow(b * cos(phi), 2) + pow(a * sin(phi), 2)))
    x = polar * cos(phi) * r
    y = polar * sin(phi) * r
    return x, y


def translateAtAngle(x, y, angle, dx, dy):
    x = x + dx * cos(angle) - dy * sin(angle)
    y = y + dx * sin(angle) + dy * cos(angle)
    return x, y
    

def getLengthAngle(e_a, e_b, previous, current, y):
    # calculate width of child using ellipse coords
    startx, starty = ellipseCoord(e_a, e_b, previous, y)
    endx, endy = ellipseCoord(e_a, e_b, current, y)
    lwidth = sqrt(pow(endx - startx, 2) + pow(endy - starty, 2)) / 2
    # calculate angle of points for use in calculating the angle
    langle = atan2(endy - starty, endx - startx)
    return lwidth, langle


def getFixedAngles(e_a, e_b, angles, weights, y, precision):
    totalweights = sum(weights)
    # calculate lenghts
    for j in range(0, precision):
        lengths = []
        for i in range(0, len(angles)):
            width, angle = getLengthAngle(e_a, e_b, sum(angles[:i]), sum(angles[:i + 1]), y)
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
            angles[i] = angles[i] / overalldeviation
    return angles
