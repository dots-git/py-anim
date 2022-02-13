# %%
from py_anim import *
from simple_pg import *
'''
An example for how an image viewing interface might look with this library (Currently requires touch input, for windows, run $env:SDL_MOUSE_TOUCH_EVENTS = 1 to use with mouse)
'''
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
    global x, y, on_edge_l, on_side_l, original_surface, surface, moving_offset, touches, scale, starting_scale, scale_last_tick, smoothscaled
    # Create the independent vectors for x and y position as well as the one for xy position, that will by used in the corners
    x  = AnimVec(acceleration=2000, acceleration_modifier=1.3, drag=2.)
    y  = AnimVec(acceleration=2000, acceleration_modifier=1.3, drag=2.)
    # Create the variable that keeps track of whether the image is outside the bounds on both axes
    touches = {}
    on_edge_l, on_side_l = False, False

    moving_offset = None
    starting_scale = None
    # Load in and upscale the image
    original_surface = pygame.image.load('./demo_img.png')
    scale = 1
    scale_last_tick = scale
    smoothscaled = True
    surface = original_surface.copy()
    

def events(event):
    global moving_offset, starting_scale, scale
    
    if event.type == pygame.MOUSEWHEEL:
        if not pygame.key.get_pressed()[pygame.K_LCTRL]:
            x.loose = False
            x._change[0] = -event.x * 500
            x._values[0] -= np.sign(event.x)
            y.loose = False
            y._change[0] = event.y * 500
            y._values[0] += np.sign(event.y)
        else:
            scale *= np.exp(event.x * 0.05) * np.exp(event.y * 0.05)
    if event.type == pygame.FINGERDOWN:
        touches[event.finger_id] = np.asarray([event.x * width(), event.y * height()])
        pos = avg_finger_pos()
        x.animate, y.animate = False, False
        moving_offset = np.asarray([pos[0] - x[0], pos[1] - y[0]]) / scale
        if len(touches) >= 2:
            starting_scale = avg_finger_dist() / scale
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
    global x, y, on_edge_l, scale

    if len(touches) == 0:
        x.loose = True
        y.loose = True
        x.drag = 2
        y.drag = 2
        # Check if x or y is outside the bounds
        x_offset = 0
        y_offset = 0
        if x[0] > 0:
            x_offset = x[0]
        if x[0] + surface.get_width() < width():
            x_offset = x[0] + surface.get_width() - width()
        if y[0] > 0:
            y_offset = y[0]
        if y[0] + surface.get_height() < height():
            y_offset = y[0] + surface.get_height() - height()
        on_edge  = x_offset != 0 or  y_offset != 0

        x.animate = True
        y.animate = True
        if on_edge and not on_edge_l:
            change = np.array([x.change[0], y.change[0]])
            acceleration = (np.sqrt((x_offset)**2 + (y_offset)**2) + np.sqrt(change.dot(change))) * 0.6 + 1
            x.acceleration = acceleration
            y.acceleration = acceleration

        if x_offset != 0:
            x.loose = False
            x.drag = 3
        if y_offset != 0:
            y.loose = False
            y.drag = 3
        if x_offset < 0:
            x[0] = width() - surface.get_width()
        if x_offset > 0:
            x[0] = 0
        if y_offset < 0:
            y[0] = height() - surface.get_height()
        if y_offset > 0:
            y[0] = 0
        on_edge_l = on_edge
    else:
        if len(touches) >= 2:
            scale = avg_finger_dist() / starting_scale
        
        pos = avg_finger_pos() - moving_offset * scale
        
        x[0] = pos[0]
        y[0] = pos[1]
        on_edge_l = False

    # Animate the values
    x.tick(delta)
    y.tick(delta)

def draw():
    global surface, scale_last_tick, smoothscaled
    if scale_last_tick != scale:
        surface = pygame.transform.scale(original_surface, (original_surface.get_width() * scale, original_surface.get_height() * scale))
        smoothscaled = False
    elif not smoothscaled:
        smooth_limit = 4
        if scale < smooth_limit:
            surface = pygame.transform.smoothscale(original_surface, (original_surface.get_width() * scale, original_surface.get_height() * scale))
        else:
            # surface = pygame.transform.smoothscale(original_surface, (original_surface.get_width() * smooth_limit, original_surface.get_height() * smooth_limit))
            # surface = pygame.transform.scale(surface, (surface.get_width() * scale / smooth_limit, surface.get_height() * scale / smooth_limit))
            surface = pygame.transform.scale(original_surface, (original_surface.get_width() * scale, original_surface.get_height() * scale))

        smoothscaled = True

    image(x[0], y[0], surface)
    scale_last_tick = scale

go(init, events, tick, draw)
# %%
