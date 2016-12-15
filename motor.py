# nxt.motor module

import time

PORT_A = 0x00
PORT_B = 0x01
PORT_C = 0x02
PORT_ALL = 0xFF

MODE_IDLE = 0x00
MODE_MOTOR_ON = 0x01
MODE_BRAKE = 0x02
MODE_REGULATED = 0x04

REGULATION_IDLE = 0x00
REGULATION_MOTOR_SPEED = 0x01
REGULATION_MOTOR_SYNC = 0x02

RUN_STATE_IDLE = 0x00
RUN_STATE_RAMP_UP = 0x10
RUN_STATE_RUNNING = 0x20
RUN_STATE_RAMP_DOWN = 0x40

LIMIT_RUN_FOREVER = 0

class BlockedException(Exception):
    pass

class OutputState(object):
    
    def __init__(self, values):
        (self.power, self.mode, self.regulation,
            self.turn_ratio, self.run_state, self.tacho_limit) = values
    
    def to_list(self):
        
        return [self.power, self.mode, self.regulation,
            self.turn_ratio, self.run_state, self.tacho_limit]
        
    def __str__(self):
        modes = []
        if self.mode & MODE_MOTOR_ON:
            modes.append('on')
        if self.mode & MODE_BRAKE:
            modes.append('brake')
        if self.mode & MODE_REGULATED:
            modes.append('regulated')
        if not modes:
            modes.append('idle')
        mode = '&'.join(modes)
        regulation = 'regulation: ' + \
                            ['idle', 'speed', 'sync'][self.regulation]
        run_state = 'run state: ' + {0: 'idle', 0x10: 'ramp_up',
                            0x20: 'running', 0x40: 'ramp_down'}[self.run_state]
        return ', '.join([mode, regulation, str(self.turn_ratio), run_state] + [str(self.tacho_limit)])


class TachoInfo:
    
    def __init__(self, values):
        self.tacho_count, self.block_tacho_count, self.rotation_count = values
    
    def get_target(self, tacho_limit, direction):
       
        if abs(direction) != 1:
            raise ValueError('Invalid direction')
        new_tacho = self.tacho_count + direction * tacho_limit
        return TachoInfo([new_tacho, None, None])
    
    def is_greater(self, target, direction):
        return direction * (self.tacho_count - target.tacho_count) > 0
    
    def is_near(self, target, threshold):
        difference = abs(target.tacho_count - self.tacho_count)
        return difference < threshold
    
    def __str__(self):
        return str((self.tacho_count, self.block_tacho_count,
                   self.rotation_count))


class SynchronizedTacho(object):
    def __init__(self, leader_tacho, follower_tacho):
        self.leader_tacho = leader_tacho
        self.follower_tacho = follower_tacho
        
    def get_target(self, tacho_limit, direction):

        leader_tacho = self.leader_tacho.get_target(tacho_limit, direction)
        return SynchronizedTacho(leader_tacho, None)
    
    def is_greater(self, other, direction):
        return self.leader_tacho.is_greater(other.leader_tacho, direction)

    def is_near(self, other, threshold):
        return self.leader_tacho.is_near(other.leader_tacho, threshold)

    def __str__(self):
        if self.follower_tacho is not None:
            t2 = str(self.follower_tacho.tacho_count)
        else:
            t2 = 'None'
        t1 = str(self.leader_tacho.tacho_count)
        return 'tacho: ' + t1 + ' ' + t2


def get_tacho_and_state(values):

    return OutputState(values[1:7]), TachoInfo(values[7:])


class BaseMotor(object):

    debug = 0
    def _debug_out(self, message):
        if self.debug:
            print message

    def turn(self, power, tacho_units, brake=True, timeout=5, emulate=True):
          
        tacho_limit = tacho_units
 
        if tacho_limit < 0:
            raise ValueError, "tacho_units must be greater than 0!"
       
        if self.method == 'bluetooth':
            threshold = 70
        elif self.method == 'usb':
            threshold = 5
        elif self.method == 'ipbluetooth':
            threshold = 80
        elif self.method == 'ipusb':
            threshold = 15
        else:
            threshold = 30 

        tacho = self.get_tacho()
        state = self._get_new_state()

        state.power = power
        if not emulate:
            state.tacho_limit = tacho_limit

        self._debug_out('Updating motor information...')
        self._set_state(state)
       
        direction = 1 if power > 0 else -1
        self._debug_out('tachocount: ' + str(tacho))
        current_time = time.time()
        tacho_target = tacho.get_target(tacho_limit, direction)
        
        blocked = False
        try:
            while True:
                time.sleep(self._eta(tacho, tacho_target, power) / 2)
                
                if not blocked: 
                    last_tacho = tacho
                    last_time = current_time
                
                tacho = self.get_tacho()
                current_time = time.time()
                blocked = self._is_blocked(tacho, last_tacho, direction)
                if blocked:
                    self._debug_out(('not advancing', last_tacho, tacho))
                 
                    if current_time - last_time > timeout:
                        if tacho.is_near(tacho_target, threshold):
                            break
                        else:
                            raise BlockedException("Blocked!")
                else:
                    self._debug_out(('advancing', last_tacho, tacho))
                if tacho.is_near(tacho_target, threshold) or tacho.is_greater(tacho_target, direction):
                    break
        finally:
            if brake:
                self.brake()
            else:
                self.idle()


class Motor(BaseMotor):
    def __init__(self, brick, port):
        self.brick = brick
        self.port = port
        self._read_state()
        self.sync = 0
        self.turn_ratio = 0
        try:
            self.method = brick.sock.type
        except:
            print "Warning: Socket did not report a type!"
            print "Please report this problem to the developers!"
            print "For now, turn() accuracy will not be optimal."
            print "Continuing happily..."
            self.method = None

    def _set_state(self, state):
        self._debug_out('Setting brick output state...')
        list_state = [self.port] + state.to_list()
        self.brick.set_output_state(*list_state)
        self._debug_out(state)
        self._state = state
        self._debug_out('State set.')

    def _read_state(self):
        self._debug_out('Getting brick output state...')
        values = self.brick.get_output_state(self.port)
        self._debug_out('State got.')
        self._state, tacho = get_tacho_and_state(values)
        return self._state, tacho
    
    
    
    def _get_state(self):
        
        return OutputState(self._state.to_list())
    
    def _get_new_state(self):
        state = self._get_state()
        if self.sync:
            state.mode = MODE_MOTOR_ON | MODE_REGULATED
            state.regulation = REGULATION_MOTOR_SYNC
            state.turn_ratio = self.turn_ratio
        else:
            state.mode = MODE_MOTOR_ON | MODE_REGULATED
            state.regulation = REGULATION_MOTOR_SPEED
        state.run_state = RUN_STATE_RUNNING
        state.tacho_limit = LIMIT_RUN_FOREVER
        return state
        
    def get_tacho(self):
        return self._read_state()[1]
        
    def reset_position(self, relative):
      
        self.brick.reset_motor_position(self.port, relative)

    def run(self, power=100, regulated=False):
       
        state = self._get_new_state()
        state.power = power
        if not regulated:
            state.mode = MODE_MOTOR_ON
        self._set_state(state)

    def brake(self):
       
        state = self._get_new_state()
        state.power = 0
        state.mode = MODE_MOTOR_ON | MODE_BRAKE | MODE_REGULATED
        self._set_state(state)

    def idle(self):
             state = self._get_new_state()
        state.power = 0
        state.mode = MODE_IDLE
        state.regulation = REGULATION_IDLE
        state.run_state = RUN_STATE_IDLE
        self._set_state(state)

    def weak_turn(self, power, tacho_units):
        
        tacho_limit = tacho_units
        tacho = self.get_tacho()
        state = self._get_new_state()

      
        state.mode = MODE_MOTOR_ON
        state.regulation = REGULATION_IDLE
        state.power = power
        state.tacho_limit = tacho_limit

        self._debug_out('Updating motor information...')
        self._set_state(state)
    
    def _eta(self, current, target, power):
        
        tacho = abs(current.tacho_count - target.tacho_count)
        return (float(tacho) / abs(power)) / 5
    
    def _is_blocked(self, tacho, last_tacho, direction):
      
        return direction * (last_tacho.tacho_count - tacho.tacho_count) >= 0


class SynchronizedMotors(BaseMotor):
  
    def __init__(self, leader, follower, turn_ratio):
       
        if follower.brick != leader.brick:
            raise ValueError('motors belong to different bricks')
        self.leader = leader
        self.follower = follower
        self.method = self.leader.method 
        
        if turn_ratio < 0:
            raise ValueError('Turn ratio <0. Change motor order instead!')

        if self.leader.port == self.follower.port:
            raise ValueError("The same motor passed twice")
        elif self.leader.port > self.follower.port:
            self.turn_ratio = turn_ratio
        else:
            self._debug_out('reversed')
            self.turn_ratio = -turn_ratio

    def _get_new_state(self):
        return self.leader._get_new_state()
        
    def _set_state(self, state):
        self.leader._set_state(state)
        self.follower._set_state(state)

    def get_tacho(self):
        leadertacho = self.leader.get_tacho()
        followertacho = self.follower.get_tacho()
        return SynchronizedTacho(leadertacho, followertacho)

    def reset_position(self, relative):
        self.leader.reset_position(relative)
        self.follower.reset_position(relative)

    def _enable(self):
       
        self.reset_position(True)
        self.leader.sync = True
        self.follower.sync = True
        self.leader.turn_ratio = self.turn_ratio
        self.follower.turn_ratio = self.turn_ratio        

    def _disable(self): 
        self.leader.sync = False
        self.follower.sync = False
      
        self.leader.idle()
        self.follower.idle()
        
    
    def run(self, power=100):
        
        self._enable()
        self.leader.run(power, True)
        self.follower.run(power, True)
    
    def brake(self):
        self._disable() 
        self._enable()
        self.leader.brake() 
        self.follower.brake()
        self._disable()
        self.leader.brake()
        self.follower.brake()

    def idle(self):
        self._disable()

    def turn(self, power, tacho_units, brake=True, timeout=1):
        self._enable()
        
        try:
            if power < 0:
                self.leader, self.follower = self.follower, self.leader
            BaseMotor.turn(self, power, tacho_units, brake, timeout, emulate=True)
        finally:
            if power < 0:
                self.leader, self.follower = self.follower, self.leader
    
    def _eta(self, tacho, target, power):
        return self.leader._eta(tacho.leader_tacho, target.leader_tacho, power)
    
    def _is_blocked(self, tacho, last_tacho, direction):
        
        return self.leader._is_blocked(tacho.leader_tacho, last_tacho.leader_tacho, direction)
