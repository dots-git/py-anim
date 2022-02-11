from glob import glob
from turtle import pos
from simple_pg import *
from py_anim import *

'''
Demo for showing the way changes in direction are handled specifically
'''

def init():
    global position, w, h
    position = AnimVec([0, 0], acceleration=15, drag=7)
    w = 100
    h = 100

def tick(delta):
    global position
    position[0:2] = pygame.mouse.get_pos()
    position.tick(delta)

def draw():
    rectangle(position[0] - w / 2, position[1] - h / 2, w, h, (0, 0, 0))

go(init, events, tick, draw)