import RPi.GPIO as GPIO
from time import sleep

class PiStepper(object):
	def __init__(self, pin_assoc, speed):
		GPIO.setmode(GPIO.BCM)
		self.Speed = speed
		self.A = pin_assoc[0]
		self.B = pin_assoc[1]
		self.C = pin_assoc[2]
		self.D = pin_assoc[3]
		
		GPIO.setup(self.A, GPIO.OUT)
		GPIO.setup(self.B, GPIO.OUT)
		GPIO.setup(self.C, GPIO.OUT)
		GPIO.setup(self.D, GPIO.OUT)
		GPIO.output(self.A, False)
		GPIO.output(self.B, False)
		GPIO.output(self.C, False)
		GPIO.output(self.D, True)
	
	def off(self):
		GPIO.output(self.D, False)
		
	def on(self):
		GPIO.output(self.D, True)
		
	def step(self, clockwise):
		if not  clockwise:
			GPIO.output(self.C, True)
			sleep(self.Speed)			## D, C
			GPIO.output(self.D, False)
			sleep(self.Speed)			## C
			GPIO.output(self.B, True)
			sleep(self.Speed)			## C, B
			GPIO.output(self.C, False)
			sleep(self.Speed)			## B
			GPIO.output(self.A, True)
			sleep(self.Speed)			## B, A
			GPIO.output(self.B, False)
			sleep(self.Speed)			## A
			GPIO.output(self.D, True)
			sleep(self.Speed)			## A, D
			GPIO.output(self.A, False)
			sleep(self.Speed)			## D
		else:
			GPIO.output(self.A, True)
			sleep(self.Speed)			## A, D
			GPIO.output(self.D, False)
			sleep(self.Speed)			## A
			GPIO.output(self.B, True)
			sleep(self.Speed)			## B, A
			GPIO.output(self.A, False)
			sleep(self.Speed)			## B
			GPIO.output(self.C, True)
			sleep(self.Speed)			## C, B
			GPIO.output(self.B, False)
			sleep(self.Speed)			## C
			GPIO.output(self.D, True)
			sleep(self.Speed)			## D, C
			GPIO.output(self.C, False)
			sleep(self.Speed)			## D
