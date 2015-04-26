from RPIO import PWM
from time import sleep

class PiServo(object):
	def __init__(self, Chan, Upper, Lower):
		self.chan = Chan
		self.upper = Upper
		self.lower = Lower
		self.servo = PWM.Servo()
		PWM.set_loglevel(1)
		self.servo.set_servo(self.chan, self.upper)
	
	def down(self):
		self.servo.set_servo(self.chan, self.lower)
	
	def up(self):
		self.servo.set_servo(self.chan, self.upper)
	
	def draw_dot(self):
		#standard wait times 0.6 0.7 0.3
		sleep(0.01)
		self.down()
		sleep(0.01)
		self.up()
		sleep(0.01)
