from py_anim import *
from simple_pg import *

def init():
    global x, y, xy, cornered, surface
    x  = AnimVec(acceleration=2, acceleration_modifier=5000, drag=2.3)
    y  = AnimVec(acceleration=2, acceleration_modifier=5000, drag=2.3)
    xy = AnimVec(acceleration=2, acceleration_modifier=5000, drag=2.3, length=2)

    cornered = False
    surface = pygame.image.load()

def tick(delta):
    x .tick(delta)
    y .tick(delta)
    xy.tick(delta)
    

go(init, events, tick, draw)