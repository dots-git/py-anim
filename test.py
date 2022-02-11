from calendar import c
from math import dist
from tkinter.tix import Tree
from simple_pg import *
from py_anim import *
from py_anim import _circular_exponential

def init():
    global pos, moving_offset, colliding

    pos = AnimVec(length=2, acceleration=2, acceleration_modifier=5000, drag=2)
    pos.loose = True
    moving_offset = None
    colliding = False
    pos[0] = 300
    pos.jump()
    
def events(event):
    global moving_offset
    if event.type == pygame.MOUSEBUTTONDOWN:
        moving_offset = pos[0:2] - pygame.mouse.get_pos()
        pos.animate = False
    if event.type == pygame.MOUSEBUTTONUP:
        moving_offset = None
        pos.animate = True
    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        pos._change[1] = 2000

def tick(delta):
    global pos, colliding
    if moving_offset is not None:
        pos[1] = np.asarray(pygame.mouse.get_pos()[1]) + moving_offset[1]
        pos.tick(delta)
        pos.loose = True
        pos.drag = 2
        colliding = False
    else:
        pos.tick(delta)
        colliding_last_tick = colliding
        colliding = False
        collision_offset = 0
        if pos[0] < 50:
            pos[0] = 50
            colliding = True
        if pos[0] > width() - 50:
            pos[0] = width() - 50
            colliding = True
        if pos[1] < 50:
            collision_offset = 50 - pos[1]
            pos[1] = 50
            colliding = True
        if pos[1] > height() - 50:
            collision_offset = pos[1] - height() + 50
            pos[1] = height() - 50
            colliding = True
        pos.loose = not colliding
        pos.drag = 2.3 if not colliding else 2
        if colliding and not colliding_last_tick:
            pos.acceleration = (abs(pos.change[1]) + collision_offset + 1) * 0.0018

def draw():
    rectangle(pos[0] - 50, pos[1] - height() + 50, 500, 2 * height() - 100, (0, 0, 0))
    rectangle(pos[0] - 50, pos[1], 500, 200, (100, 100, 100))

go(init, events, tick, draw)