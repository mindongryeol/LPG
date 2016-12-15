# nxt.sensor module -- 

from .common import *
from .digital import BaseDigitalSensor
from .analog import BaseAnalogSensor


class Touch(BaseAnalogSensor):
    

    def __init__(self, brick, port):
        super(Touch, self).__init__(brick, port)
        self.set_input_mode(Type.SWITCH, Mode.BOOLEAN)
    
    def is_pressed(self):
        return bool(self.get_input_values().scaled_value)
    
    get_sample = is_pressed


class Light(BaseAnalogSensor):
   
    def __init__(self, brick, port, illuminated=True):
        super(Light, self).__init__(brick, port)

    def set_illuminated(self, active):
        if active:
            type_ = Type.LIGHT_ACTIVE
        else:
            type_ = Type.LIGHT_INACTIVE
        self.set_input_mode(type_, Mode.RAW)

    def get_lightness(self):
        return self.get_input_values().scaled_value	
    
    get_sample = get_lightness


class Sound(BaseAnalogSensor):
  

    def __init__(self, brick, port, adjusted=True):
        super(Sound, self).__init__(brick, port)
        self.set_adjusted(adjusted)

    def set_adjusted(self, active):
        if active:
            type_ = Type.SOUND_DBA
        else:
            type_ = Type.SOUND_DB
        self.set_input_mode(type_, Mode.RAW)
    
    def get_loudness(self):
        return self.get_input_values().scaled_value
    
    get_sample = get_loudness


class Ultrasonic(BaseDigitalSensor):
    
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'measurement_units': (0x14, '7s'),
        'continuous_measurement_interval': (0x40, 'B'),
        'command': (0x41, 'B'),
        'measurement_byte_0': (0x42, 'B'),
        'measurements': (0x42, '8B'),
        'actual_scale_factor': (0x51, 'B'),
        'actual_scale_divisor': (0x52, 'B'),
    })
    
    class Commands:
        'These are for passing to command()'
        OFF = 0x00
        SINGLE_SHOT = 0x01
        CONTINUOUS_MEASUREMENT = 0x02
        EVENT_CAPTURE = 0x03 
        REQUEST_WARM_RESET = 0x04
    
    def __init__(self, brick, port, check_compatible=True):
        super(Ultrasonic, self).__init__(brick, port, check_compatible)
        self.set_input_mode(Type.LOW_SPEED_9V, Mode.RAW)

    def get_distance(self):
        
        return self.read_value('measurement_byte_0')[0]
    
    get_sample = get_distance
            
    def get_measurement_units(self):
        return self.read_value('measurement_units')[0].split('\0')[0]

    def get_all_measurements(self):
        
        return self.read_value('measurements')
    
    def get_measurement_no(self, number):
       
        if not 0 <= number < 8:
            raise ValueError('Measurements are numbered 0 to 7, not ' + str(number))
        base_address, format = self.I2C_ADDRESS['measurement_byte_0']
        return self._i2c_query(base_address + number, format)[0]

    def command(self, command):
        self.write_value('command', (command, ))
    
    def get_interval(self):
      
        return self.read_value('continuous_measurement_interval')
    
    def set_interval(self, interval):
       
        self.write_value('continuous_measurement_interval', interval)

Ultrasonic.add_compatible_sensor(None, 'LEGO', 'Sonar') 


class Color20(BaseAnalogSensor):
    def __init__(self, brick, port):
        super(Color20, self).__init__(brick, port)
        self.set_light_color(Type.COLORFULL)

    def set_light_color(self, color):
       
        self.set_input_mode(color, Mode.RAW)

    def get_light_color(self):
        
        return self.get_input_values().sensor_type

    def get_reflected_light(self, color):
        self.set_light_color(color)
        return self.get_input_values().scaled_value
    
    def get_color(self):
        self.get_reflected_light(Type.COLORFULL)
        return self.get_input_values().scaled_value
    
    get_sample = get_color
