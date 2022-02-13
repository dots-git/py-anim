# %%
from py_anim import *
from simple_pg import *
import os
'''
An example for how an image viewing interface might look with this library (best with touch input)
'''
os.environ['SDL_MOUSE_TOUCH_EVENTS'] = '1'
def avg_finger_pos():
    avg = np.array([0, 0])
    for key in touches.keys():
        avg = avg + touches[key]
    return avg / len(touches) if len(touches) > 0 else avg

def avg_finger_dist():
    avg = 0
    elements = 0
    for key1 in touches.keys():
        for key2 in touches.keys():
            if key1 != key2:
                distance = touches[key1] - touches[key2]
                value = np.sqrt(distance.dot(distance))
                avg += value
                elements += 1
    return avg / elements if elements > 0 else avg

def init():
    global x, y, on_edge_x_l, on_edge_y_l, original_surface, surface, moving_offset, touches, scale, starting_scale, scale_last_tick, smoothscaled
    # Create the independent vectors for x and y position as well as the one for xy position, that will by used in the corners
    x  = AnimVec(acceleration=2000, acceleration_modifier=1.3, drag=2.)
    y  = AnimVec(acceleration=2000, acceleration_modifier=1.3, drag=2.)
    # Create the variable that keeps track of whether the image is outside the bounds on both axes
    touches = {}
    on_edge_x_l, on_edge_y_l = False, False

    moving_offset = None
    starting_scale = None
    # Load in and upscale the image
    original_surface = pygame.image.load('./demo_img.png')
    scale = 1
    scale_last_tick = scale
    smoothscaled = True
    surface = original_surface.copy()
    config.scroll_step = 500

def events(event):
    global moving_offset, starting_scale, scale, on_edge_x_l, on_edge_y_l
    
    if event.type == pygame.MOUSEWHEEL:
        print(event.x, event.y)
        if not pygame.key.get_pressed()[pygame.K_LCTRL]:
            x.loose = False
            y.loose = False
            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                x[0] -= event.x * config.scroll_step
                x[0] += event.y * config.scroll_step
                x.acceleration = 1000
            else:
                x[0] -= event.x * config.scroll_step
                y[0] += event.y * config.scroll_step
                if event.x > 0:
                    x.acceleration = 1000
                if event.y > 0:
                    y.acceleration = 1000
        else:
            mouse_pos = pygame.mouse.get_pos()
            factor = np.exp(event.x * 0.05) * np.exp(event.y * 0.05)
            scale *= factor
            if scale > width()  / 3: scale = width() / 3
            elif scale > height() / 3: scale = height() / 3
            else:
                x.animate = False
                y.animate = False
                x[0] = mouse_pos[0] - (mouse_pos[0] - x[0]) * factor
                y[0] = mouse_pos[1] - (mouse_pos[1] - y[0]) * factor
                x.jump()
                y.jump()
        on_edge_x_l = False
        on_edge_y_l = False
    if event.type == pygame.FINGERDOWN:
        touches[event.finger_id] = np.asarray([event.x * width(), event.y * height()])
        pos = avg_finger_pos()
        x.animate, y.animate = False, False
        moving_offset = np.asarray([pos[0] - x[0], pos[1] - y[0]]) / scale
        if len(touches) >= 2:
            starting_scale = avg_finger_dist() / scale
            if scale > width()  / 3: scale = width() / 3
            if scale > height() / 3: scale = height() / 3
    if event.type == pygame.FINGERUP:
        touches.pop(event.finger_id, None)
        pos = avg_finger_pos()
        moving_offset = np.asarray([pos[0] - x[0], pos[1] - y[0]]) / scale
        if len(touches) >= 2:
            starting_scale = avg_finger_dist() / scale
        if len(touches) == 1:
            x.animate = False
            y.animate = False
    if event.type == pygame.FINGERMOTION:
        touches[event.finger_id] = np.asarray([event.x * width(), event.y * height()])
    
    # if event.type == pygame.MOUSEBUTTONDOWN:
    #     if event.button == pygame.BUTTON_LEFT:
    #         touches['mouse'] = np.asarray([event.pos[0] * width(), event.pos[1] * height()])
    #         pos = avg_finger_pos()
    #         x.animate, y.animate = False, False
    #         moving_offset = np.asarray([pos[0] - x[0], pos[1] - y[0]]) / scale
    #         if len(touches) >= 2:
    #             starting_scale = avg_finger_dist() / scale
    # if event.type == pygame.MOUSEBUTTONUP:
    #     if event.button == pygame.BUTTON_LEFT:
    #         touches.pop('mouse', None)
    #         pos = avg_finger_pos()
    #         moving_offset = np.asarray([pos[0] - x[0], pos[1] - y[0]]) / scale
    #         if len(touches) >= 2:
    #             starting_scale = avg_finger_dist() / scale
    #         if len(touches) == 1:
    #             x.animate = False
    #             y.animate = False
    # if event.type == pygame.MOUSEMOTION:
    #     if pygame.mouse.get_pressed()[pygame.BUTTON_LEFT]:
    #         touches['mouse' + str(event.button)] = np.asarray([event.pos[0] * width(), event.pos[1] * height()])

def tick(delta):
    global x, y, on_edge_x_l, on_edge_y_l, scale

    if len(touches) == 0:
        x.drag = 2
        y.drag = 2
        # Check if x or y is outside the bounds
        if original_surface.get_width() * scale > width():
            x_offset = 0
            on_edge = False
            if x[0] > 0 and x.target[0] >= 0:
                x_offset = x[0]
            if x[0] + original_surface.get_width() * scale < width() and x.target[0] + original_surface.get_width() * scale <= width():
                x_offset = x[0] + original_surface.get_width() * scale - width()
            if x_offset != 0: on_edge = True

            x.animate = True

            if x_offset != 0:
                x.loose = False
                x.drag = 3

            if x_offset < 0:
                x[0] = width() - original_surface.get_width() * scale
            if x_offset > 0:
                x[0] = 0

            if on_edge and not on_edge_x_l:
                change = abs(x.change[0])
                acceleration = (x_offset + change) * 0.6 + 1
                x.acceleration = acceleration
            on_edge_x_l = on_edge

        if original_surface.get_height() * scale > height():
            y_offset = 0
            on_edge = False
            if y[0] > 0 and y.target[0] >= 0:
                y_offset = y[0]
            if y[0] + original_surface.get_height() * scale < height() and y.target[0] + original_surface.get_height() * scale <= height():
                y_offset = y[0] + original_surface.get_height() * scale - height()

            y.animate = True

            if y_offset != 0:
                y.loose = False
                y.drag = 3
            
            if y_offset < 0:
                y[0] = height() - original_surface.get_height() * scale
            if y_offset > 0:
                y[0] = 0

            if on_edge and not on_edge_y_l:
                change = abs(y.change[0])
                acceleration = (y_offset + change) * 0.6 + 1
                y.acceleration = acceleration
            on_edge_y_l = on_edge
        
    else:
        if len(touches) >= 2:
            scale = avg_finger_dist() / starting_scale
            if scale > width()  / 3: scale = width() / 3
            if scale > height() / 3: scale = height() / 3
        
        pos = avg_finger_pos() - moving_offset * scale
        
        x[0] = pos[0]
        y[0] = pos[1]
        on_edge_x_l = False

    # Animate the values
    x.tick(delta)
    y.tick(delta)
    x.loose = True
    y.loose = True

def draw():
    global surface, scale_last_tick, smoothscaled, scale
    
    in_x = x[0] / scale
    in_y = y[0] / scale
    if in_x < 1: in_x -= 1
    if in_y < 1: in_y -= 1
    visible_rect = pygame.Rect(in_x, in_y, width() / scale + 2, height() / scale + 2)

    surface = pygame.Surface((visible_rect.width, visible_rect.height))
    surface.fill(WHITE)
    surface.blit(original_surface, visible_rect)
    surface = pygame.transform.smoothscale(surface, (surface.get_width() * scale, surface.get_height() * scale))

    image((x[0] / scale % 1 - 1) * scale, (y[0] / scale % 1 - 1) * scale, surface)
    scale_last_tick = scale

go(init, events, tick, draw)
# %%
