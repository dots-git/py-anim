import pygame
from pygame import gfxdraw
import time
import numpy as np

def size(surface: pygame.Surface = None):
    ''' 
    Returns a tuple of the width and height of the window 
    '''
    if surface is None:
        surface = pygame.display.get_surface()
    return surface.get_size()

def width(surface: pygame.Surface = None):
    ''' 
    Returns the width of the window 
    '''
    if surface is None:
        surface = pygame.display.get_surface()
    return surface.get_size()[0]

def height(surface: pygame.Surface = None):
    ''' 
    Returns the height of the window 
    '''
    if surface is None:
        surface = pygame.display.get_surface()
    return surface.get_size()[1]

def circle(x: 'int | float', y: 'int | float', r: 'int | float', color, filled: bool = True, surface: pygame.Surface = None):
    ''' 
    Draw an antialiased circle 
    
    :param x: The x coordinate of the circle's center
    :param y: The y coordinate of the circle's center
    :param r: The radius of the circle
    :param color: The color of the circle
    :param filled: Whether or not the circle should be filled
    :param surface: The surface to draw the circle on
    '''
    x -= r
    y -= r
    if surface is None:
        surface = pygame.display.get_surface()
    if filled:
        s = pygame.Surface([2 * r + 1, 2 * r + 1], pygame.SRCALPHA)
        a = np.array([[i for i in range(2 * r + 1)] for _ in range(2 * r + 1)])
        b = np.array([[i for _ in range(2 * r + 1)] for i in range(2 * r + 1)])
        a -= r
        b -= r
        distance_map = np.sqrt(np.power(a, 2) + np.power(b, 2))
        for i in range(2 * r + 1):
            for j in range(2 * r + 1):
                distance = distance_map[i][j]
                alpha = 255
                if distance > r + 1:
                    alpha = 0
                elif distance > r:
                    alpha = -255 * distance + 255 * (r + 1)
                s.set_at((i, j), (color[0], color[1], color[2], alpha))
        surface.blit(s, (x, y))
    else:
        gfxdraw.aacircle(surface, int(x), int(y), int(r), color)

def pg_line(x1: 'int | float', y1: 'int | float', x2: 'int | float', y2: 'int | float', color, w = 1, surface: pygame.Surface = None):

    if surface is None:
        surface = pygame.display.get_surface()
    
    pygame.draw.aaline(surface, color, (x1, y1), (x2, y2))
    

def line(x1: 'int | float', y1: 'int | float', x2: 'int | float', y2: 'int | float', color, w = 1, surface: pygame.Surface = None):
    ''' 
    Draw an antialiased line 
    
    :param x1: The x coordinate of point 1 of the line
    :param y1: The y coordinate of point 1 of the line
    :param x2: The x coordinate of point 2 of the line
    :param y2: The y coordinate of point 2 of the line
    :param color: The color of the line
    :param surface: The surface to draw the line on
    '''
    if surface is None:
        surface = pygame.display.get_surface()
    
    w /= 2
    x_offset = 0
    if y1 > y2:
        tmp = x1, y1
        x1, y1 = x2, y2
        x2, y2 = tmp
        # x_offset = x2 - x1
    if y2 == y1:
        y1 += 10e-10
    slope = (x2 - x1) / (y2 - y1)
    y0 = 0
    if x2 < x1:
        y0 = x1 - x2
        x_offset = x2 - x1

    
    size_x = int(abs(x2 - x1) + w * 4)
    size_y = int(abs(y2 - y1) + w * 4)
    
    a1 = np.array([[i for i in range(size_y)] for _ in range(size_x)])
    b1 = np.array([[i for _ in range(size_y)] for i in range(size_x)])



    a2 = (a1 + b1 * slope - slope * y0) / (np.power(slope, 2) + 1)
    b2 = slope * a2 + y0

    distance_map = np.sqrt(np.power(a2 - a1, 2) + np.power(b2 - b1, 2))
    surface_width, surface_height = surface.get_size()
    for i in range(size_x):
        for j in range(size_y):
            x = int(x1 + x_offset + i)
            y = int(y1 + j)
            if x < surface_width and y < surface_height and x >= 0 and y >= 0:
                distance = distance_map[i][j]
                if distance < w:
                    surface.set_at((x, y), color)
                elif distance < w + 1:
                    alpha = -distance + (w + 1)
                    original_color = surface.get_at((x, y))
                    surface.set_at((x, y), (
                        color[0] * alpha + original_color[0] * (1 - alpha), 
                        color[1] * alpha + original_color[1] * (1 - alpha),
                        color[2] * alpha + original_color[2] * (1 - alpha)
                    ))

def polygon(points, color, filled: bool = True, surface: pygame.Surface = None):
    ''' 
    Draw an antialiased polygon 

    :param points: The list of points of the polygon
    :param color: The color of the polygon
    :param filled: Whether or not the polygon should be filled
    :param surface: The surface to draw the polygon on
    '''
    if surface is None:
        surface = pygame.display.get_surface()
    gfxdraw.aapolygon(surface, points, color)
    if filled:
        pygame.draw.polygon(surface, color, points)

def rectangle(x: 'float | int', y: 'float | int', width: 'float | int', height: 'float | int', color, outline: 'float | int' = 0, surface: pygame.Surface = None):
    ''' 
    Draw an axis-aligned rectangle. 
    
    :param x: The x coordinate of the rectangle
    :param y: The y coordinate of the rectangle
    :param width: The width of the rectangle
    :param height: The height of the rectangle
    :param color: The color of the rectangle
    :param outline: Width of the rectangle's outline. 0 for a filled rectangle
    :param surface: The surface to draw the rectangle on
    '''
    if surface is None:
        surface = pygame.display.get_surface()
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, color, rect, outline)

def rounded_rectangle(x: 'float | int', y: 'float | int', width: 'float | int', height: 'float | int', color, radius: 'float | int', surface: pygame.Surface = None):
    '''
    Draw a rounded rectangle

    :param x: The x coordinate of the rectangle
    :param y: The y coordinate of the rectangle
    :param width: The width of the rectangle 
    :param height: The height of the rectangle
    :param color: The color of the rectangle
    :param radius: The corner radius of the rectangle
    :param surface: The surface to draw the rectangle on
    '''
    if surface is None:
        surface = pygame.display.get_surface()

    s = pygame.Surface((width, height), pygame.SRCALPHA)
    s.fill(color)
    surface.blit(rounded(s, radius), (x, y))

def image(x, y, img, surface: pygame.Surface = None):
    '''
    Draw an image on the screen

    :param x: The x coordinate of the image
    :param y: The y coordinate of the image
    :param surface: The surface to draw the image on

    '''

    if surface is None:
        surface = pygame.display.get_surface()
    
    surface.blit(img, (x, y))

def text(x: int, y: int, text_str: str, color, typeface: str = 'Linux Biolinum G', font_size: int = 30, bold: bool = False, italic: bool = False, alignment_x: str = 'center', alignment_y: str = 'center', surface: pygame.Surface = None):
    '''
    Draw text on the screen

    :param x: The x coordinate of the text origin
    :param y: The y coordinate of the text origin
    :param text: The text to draw
    :param font: The font to draw the text in
    :param font_size: The font size of the text
    :param color: The color to draw the text in
    :param alignment_x: The horizontal alignment of the text ('left', 'center' or 'right')
    :param alignment_y: The vertical alignment of the text ('top', 'center' or 'bottom')
    :param surface: The surface to draw the text on
    '''
    if surface is None:
        surface = pygame.display.get_surface()
    
    font_obj = pygame.font.SysFont(typeface, font_size, bold, italic)
    text_surface = font_obj.render(text_str, True, color)
    if alignment_x == 'center':
        x = x - text_surface.get_width() * 0.5
    elif alignment_x == 'right':
        x = x - text_surface.get_width()
    if alignment_y == 'center':
        y = y - text_surface.get_height() * 0.5
    elif alignment_y == 'bottom':
        y = y - text_surface.get_height()

    surface.blit(text_surface, (x, y))

def fill(color, surface: pygame.Surface = None):
    ''' 
    Fill the canvas with the given color

    :param color: The color to fill the canvas with    
    '''
    if surface is None:
        surface = pygame.display.get_surface()
    surface.fill(color)

def rounded(surface: pygame.Surface, radius, rounded_corners: 'list[bool]' = [True, True, True, True]):
    rounded_surface = surface.copy()
    surface_width, surface_height = rounded_surface.get_size()
    if radius * 2 > surface_width:
        radius = int(surface_width / 2)
    if radius * 2 > surface_height:
        radius = int(surface_height / 2)

    a = np.array([[i for i in range(radius)] for _ in range(radius)])
    b = np.array([[i for _ in range(radius)] for i in range(radius)])
    distance_map = np.sqrt(np.power(a, 2) + np.power(b, 2))

    for i in range(radius):
        for j in range(radius):
            x = 0
            y = 0
            
            distance = distance_map[radius - i - 1, radius - j - 1]
            alpha = 1
            if distance > radius + 1:
                alpha = 0
            elif distance > radius:
                alpha = -distance + (radius + 1)
            for k in range(4):
                if rounded_corners[k]:
                    if k == 0:
                        x = i
                        y = j
                    elif k == 1:
                        x = rounded_surface.get_size()[0] - i - 1
                        y = j
                    elif k == 2:
                        x = i   
                        y = rounded_surface.get_size()[1] - j - 1
                    elif k == 3:
                        x = rounded_surface.get_size()[0] - i - 1
                        y = rounded_surface.get_size()[1] - j - 1
                    color = rounded_surface.get_at((x, y))
                    color = (color[0], color[1], color[2], color[3] * alpha)
                    rounded_surface.set_at((x, y), color)
    return rounded_surface

def set_at(x, y, color, surface: pygame.Surface = None):
    '''
    Set a pixel on the surface to the given color

    :param x: x coordinate of the pixel
    :param y: y coordinate of the pixel
    :param color: color of the pixel
    '''

    if surface is None:
        surface = pygame.display.get_surface()
    
    surface.set_at((x, y), color)

def init():
    pass

def events(event):
    pass

def tick(delta):
    pass

def draw():
    pass

# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class win_config():
    max_fps = 0
    min_delta = 0
    background_color = WHITE
    fps_update_interval = 0.5
    curr_fps = 0

    @staticmethod
    def set_max_fps(value):
        ''' Change the FPS limit. Exists to save resources '''
        win_config.max_fps = value
        win_config.min_delta = 1 / win_config.max_fps
        win_config.just_updated = True
    
    @staticmethod
    def set_fps_update_interval(value):
        ''' Change the FPS update interval. Makes FPS displays more readable '''
        win_config.fps_update_interval = value

win_config.set_max_fps(65)

def go(init_func = init, events_fuc = events, tick_func = tick, draw_func = draw, width = 1000, height = 600, name = 'New Project'):
    ''' Start the game loop '''
    pygame.init()
    pygame.mixer.init()  ## For sound
    pygame.font.init()

    screen = None
    if width == 0:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption(name)

    current_time = time.time()
    time_last_frame = current_time
    delta = win_config.min_delta
    delta_list = []
    fps_display_update_time = win_config.fps_update_interval

    init_func()
    running = True
    while running:
        for event in pygame.event.get():        # gets all the events which have occured till now and keeps tab of them. 
            # listening for the the X button at the top
            if event.type == pygame.QUIT:
                running = False
            if events_fuc(event) == False:
                running = False
        

        tick_func(delta)

        screen.fill(win_config.background_color)

        draw_func()
        
        pygame.display.flip()   

        current_time = time.time()
        delta = current_time - time_last_frame
        if delta < win_config.min_delta:
            time.sleep(win_config.min_delta - delta)
            current_time = time.time()
            delta = current_time - time_last_frame
        time_last_frame = current_time

        if delta == 0:
            delta += 10e-255
        delta_list.append(delta)
        fps_display_update_time -= delta
        


        if fps_display_update_time < 0:
            print("Fps: %i (Min: %i, Max: %i)" % (len(delta_list)/sum(delta_list), 1/max(delta_list), 1/min(delta_list)))
            win_config.curr_fps = 1 / delta
            delta_list = []
            fps_display_update_time = win_config.fps_update_interval

    pygame.quit()