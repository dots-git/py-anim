from simple_pg import *
from py_anim import *
'''
As used in debugging. Good visualization of the animation curve
'''
def init():
    global value, target, points, deltas, point_distance, paused

    value = AnimVec([0], acceleration=700, acceleration_modifier=1.2, drag=2)
    target = AnimVec([0], acceleration=4000, acceleration_modifier=1.5, drag=12)
    points = []
    deltas = []
    point_distance = 300
    paused = False

def events(event):
    global paused
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            paused = not paused
        else:
            value[0] = 1000 if value.target[0] < 500 else 0

def tick(delta):
    global points
    target[0] = value.target
    target.tick(delta)
    if not paused:
        value.tick(delta)
        points.insert(0, value[0])
        deltas.insert(0, delta)
        while sum(deltas) * point_distance > width() + 100:
            points.pop()
            deltas.pop()

def draw():
    # point_distance = width() / (len(points) - 1)
    circle(width() - 10, target[0] * height() / 1000, 10, (200, 200, 200))
    pos = width() - 10
    for i in range(len(points) - 1):
        point1 = (pos, points[i] * height() / 1000)
        pos -= deltas[i + 1] * point_distance
        point2 = (pos, points[i + 1] * height() / 1000)
        pg_line(point1[0], point1[1], point2[0], point2[1], (0, 0, 0))


    circle(width() - 10, value[0] * height() / 1000, 10, (0, 0, 0))

go(init, events, tick, draw)