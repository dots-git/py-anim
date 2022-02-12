import math
import numpy as np
from collections.abc import *
from numpy.typing import _array_like, _scalars

def approx(a, b, variance):
    return a < b + variance and a > b - variance

def moving_toward(value, change_rate, drag):
    return value - change_rate / math.log(drag)

def _animate_value(value, change_rate, target, acceleration, acceleration_modifier, drag, delta_time):
    moving_twd = moving_toward(value, change_rate, drag)
    if moving_twd < target - 0.01:
        change_rate
        # Calculate animation progress
        progress = np.sign(change_rate) * np.power(abs(change_rate) / (acceleration_modifier + 1), 1 / acceleration_modifier)
        # Increment animation progress by delta time
        progress += delta_time * acceleration
        # Calculate new change rate
        change_rate = np.sign(progress) * (acceleration_modifier + 1) * np.power(abs(progress), acceleration_modifier)
        
        if moving_toward(value, change_rate, drag) > target:
            change_rate = (value - target) * math.log(drag)
        
        if value + change_rate * delta_time > target:
            change_rate = (target - value) / delta_time
    else:
        if target + change_rate > moving_twd > target:
            change_rate = (value - target) * math.log(drag)
        change_rate *= drag**delta_time
    return change_rate

# animate with circular growth, then exponential decay
def _animate_deprecated(value, change_rate, target, acceleration, acceleration_modifier, drag, delta_time):
    moving_twd = moving_toward(value, change_rate, drag)
    
    # Accelerate if change_rate is too small
    if moving_twd < target - 0.01:
        if math.atan(change_rate / acceleration_modifier) + acceleration * delta_time < math.pi/2:
            change_rate = acceleration_modifier * math.tan(math.atan(change_rate / acceleration_modifier) + acceleration * delta_time)
        else:
            change_rate += change_rate - acceleration_modifier * math.tan(math.atan(change_rate / acceleration_modifier) - acceleration * delta_time)
            if change_rate < 0:
                change_rate = (value - target) * math.log(drag)
        moving_twd = moving_toward(value, change_rate, drag)
    
    # Cap change_rate if it is too big
    if moving_twd > target + 0.01:
        change_rate = (value - target) * math.log(drag)
        moving_twd = moving_toward(value, change_rate, drag)

    # Slow down if that way you reach target precisely
    if approx(moving_twd, target, 0.01):
        change_rate *= drag**delta_time
        change_rate = ((value + change_rate * delta_time) - target) * math.log(drag)
    
    if value + change_rate * delta_time > target:
        change_rate = (target - value) / delta_time
    
    return change_rate

class AnimVec(Sequence):
    '''
    A vector of values that will be animated uniformly to allow
    animating multiple attributes with different target values in unison
    '''
    def __init__(self, vector: _array_like.ArrayLike = None, length: _scalars._IntLike_co = 1, acceleration: _scalars._FloatLike_co = 100, acceleration_modifier: _scalars._FloatLike_co = 1.3, drag: _scalars._FloatLike_co = 1):
        '''
        :attr vector: Initial vector to be used
        :attr length: Length of the vector to create if no vector is defined. Defaults to 1
        :attr acceleration: How quickly the values accelerate or change direction
        :attr acceleration_modifier: Modifier for the way the values are accelerated. 1 corresponds to a circular acceleration curve. The higher the value, the closer the curve gets to a parabola
        :attr drag: The drag to slow the movement of the values with. Curve will equate approximately to 10^(-drag*x)
        '''
        self._values: np.ndarray[np.float64] = np.array(vector) if vector is not None else np.zeros(length)
        self._target: np.ndarray[np.float64] = self._values.copy()
        self._change: np.ndarray[np.float64] = np.zeros(len(self))
        

        self._animate: bool = True
        self._loose: bool = False

        self._record_change = True
        self.keep_velocity: bool = False

        self._acceleration = 0.
        self._acceleration_modifier = 0.
        self._drag = 0.

        self.acceleration = acceleration
        self.acceleration_modifier = acceleration_modifier
        self.drag = drag
    
    def tick(self, delta):
        ''' Execute this every frame and pass the delta time to animate the values '''
        if self.animate:
            if self.loose:
                self._change = self._change * self._drag**delta
                self._target = self._values - self._change / math.log(self._drag)
            else:
                difference_vector: np.ndarray = self._target - self._values
                distance = np.sqrt(difference_vector.dot(difference_vector))
                if distance == 0: distance = 10e-100

                # Get the component of the change rate in the direction of the difference vector
                c_dot_d = self._change.dot(difference_vector)
                d_dot_d = difference_vector.dot(difference_vector)
                c_dot_c = self._change.dot(self._change)
                abs_c   = np.sqrt(c_dot_c)
                num     = c_dot_d * abs(c_dot_d)
                den     = d_dot_d * abs_c
                change  = num / den if den != 0 else 0
                
                # Animate the change vector's value
                change = _animate_value(0, change, distance, self._acceleration, self._acceleration_modifier, self._drag, delta)

                # Apply the change rate to the normalized difference vector
                self._change = change * difference_vector / distance
            self._values = self._values + self._change * delta
        else:
            if self._record_change:
                a = 1
                b = 2
                a = a / (a + b)
                b = b / (a + b)

                new_change = (self._target - self._values) / delta
                if new_change.dot(new_change) > self._change.dot(self._change):
                    self._change = new_change
                else:
                    self._change = self._change * a + new_change * b
            else:
                self._change = np.zeros(len(self))
            self._values = self._target.copy()

    def jump(self, i = None):
        ''' Immediately jump to the target values '''
        if i is None:
            self._values = self._target.copy()
            self._change = np.zeros(len(self))
        else:
            self._values[i] = self._target[i]
            self._change[i] = 0
    
    def cap_change(self, value, i = None):
        if i is None:
            self._change[np.abs(self._change) > value] = value
        else:
            if self.change[i] > value: self._change[i] = i

    def get_axis_from(self, source: 'AnimVec', axis, source_axis = None):
        if source_axis is None:
            source_axis = axis
        self._change[axis] = source._change[source_axis].copy()
        self._values[axis] = source._values[source_axis].copy()
        self._target[axis] = source._target[source_axis].copy()

# Setters and Getters
    @property
    def animate(self):
        ''' Whether or not to animate the position. Stops values where they are when set to False '''
        return self._animate
    
    @animate.setter
    def animate(self, value: _scalars._BoolLike_co):
        self._animate = value
        if not value:
            self._change = np.zeros(len(self))
            self._target = self._values.copy()

    @property
    def loose(self):
        ''' Whether or not the values should be left to move freely. If True, they will not be accelerated to animate toward the target '''
        return self._loose
    
    @loose.setter
    def loose(self, value):
        self._loose = value

    @property
    def record_change(self):
        return self._record_change
    
    @record_change.setter
    def record_change(self, value):
        self._record_change = value

    @property
    def acceleration(self):
        '''How quickly the values accelerate or change direction'''
        return self._acceleration
    
    @acceleration.setter
    def acceleration(self, value: _scalars._FloatLike_co):
        self._acceleration = value if value > 0 else 0

    @property
    def acceleration_modifier(self):
        '''Modifier for the way the values are accelerated. 1 corresponds to a circular acceleration curve. The higher the value, the closer the curve gets to a parabola'''
        return self._acceleration_modifier
    
    @acceleration_modifier.setter
    def acceleration_modifier(self, value: _scalars._FloatLike_co):
        self._acceleration_modifier = value if value > 0 else 0

    @property
    def drag(self):
        '''The drag to slow the movement of the values with. Curve will equate approximately to 10^(-drag*x)'''
        return np.log10(self._drag)

    @drag.setter
    def drag(self, value: _scalars._FloatLike_co):
        self._drag = 10**(-value) if value > 0 else 1

    @property
    def target(self):
        return self._target

    @property
    def change(self):
        return self._change
    
    @change.setter
    def change(self, value: _scalars._FloatLike_co):
        self._change = np.array(value)

    def __getitem__(self, i):
        return self._values[i]
    
    def __setitem__(self, i, value: _array_like.ArrayLike):
        self._target[i] = value

    def __len__(self):
        return self._values.shape[0]
    
    def __str__(self):
        return 'Values:  ' + str(self._values) + '\nTarget:  ' + str(self._target) + '\nChange:  ' + str(self._change) + '\nAnimate: ' + str(self._animate) + '\nLoose:   ' + str(self._loose)