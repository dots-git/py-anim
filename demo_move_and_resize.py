from re import T
from py_anim import *
from simple_pg import *
'''
Demo for showing a way of applying animated vectors in moving and resizing rectangles.
This highlights how all values are correlated and how they are animated in corresponding speed
'''
def rect_from_pos(pos1, pos2):
    left   = min(pos1[0], pos2[0])
    right  = max(pos1[0], pos2[0])
    top    = min(pos1[1], pos2[1])
    bottom = max(pos1[1], pos2[1])
    return [left, top, right - left, bottom - top]

def init():
    global rect, pos1, pos2
    rect = AnimVec([0, 0, width(), height()], acceleration=15, drag=7)
    # rect[0:4] = [width() / 2 - 50, height() / 2 - 50, 100, 100]
    rect[0:4] = [0, 0, 0, height()]
    pos1 = (0, 0)
    pos2 = (0, 0)

def events(event):
    global rect, pos1, pos2
    if event.type == pygame.MOUSEBUTTONDOWN:
        # Record the first of the rectangle's target corners
        pos1 = pygame.mouse.get_pos()
        pos2 = None
    if event.type == pygame.MOUSEBUTTONUP:
        pos2 = pygame.mouse.get_pos()
        rect[0:4] = rect_from_pos(pos1, pygame.mouse.get_pos())

def tick(delta):
    rect.tick(delta)

def draw():
    rectangle(round(rect[0]), round(rect[1]), round(rect[2]), round(rect[3]), (0, 0, 0))

    tmp_pos2 = pygame.mouse.get_pos() if pos2 is None else pos2
    target_rect = rect_from_pos(pos1, tmp_pos2)
    rectangle(round(target_rect[0]), round(target_rect[1]), round(target_rect[2]), round(target_rect[3]), (0, 0, 0, 100))


go(init, events, tick, draw)