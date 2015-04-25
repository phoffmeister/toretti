from Toretti import Abmessungen
from Toretti import draw
from Stepper import PiStepper
from Servo import PiServo
import os, os.path
import cherrypy
import cv2

class MotorControl(object):
	@cherrypy.expose
	def index(self):
		return file('index.html')

class MotorControlWebService(object):
	exposed = True
	
	stepper_l = PiStepper([14,15,18,23],0.002)
	stepper_r = PiStepper([17,27,22,10],0.002)
	stift = PiServo(7, 1700, 1800)
	
	def PUT(self,motor,steps,direction):
		if motor == 'servo':
			if direction == 'up':
				self.stift.up()
			else:
				self.stift.down()
		elif motor == 'left':
			for st in range(int(steps)):
				self.stepper_l.step(direction == 'ccw')
		elif motor == 'right':
			for st in range(int(steps)):
				self.stepper_r.step(direction == 'ccw')
	
	def POST(self, Alpha1, Alpha2, Beta, P, B , A, R, S, L1_alt, L2_alt):
		self.M = Abmessungen(float(Alpha1), float(Alpha2), float(Beta), float(P), float(B) ,float(A), float(R),float(S), float(L1_alt), float(L2_alt))
		print self.M.l2_alt
		draw(self.M, self.stift, self.stepper_l, self.stepper_r)
		return 'done'

class PictureUpload(object):
	@cherrypy.expose
	def index(self):
		return """<html><body><form action="upload" method="post" enctype="multipart/form-data"><input type="file" name="myFile" /> <br /><input type="submit" /></form></body></html>"""

	@cherrypy.expose
	def upload(self, myFile):
		out = open("public/pics/img.jpg", "w")
		while True:
			data = myFile.file.read(8192)
			if not data:
				break
			out.write(data)
		out.close()
		
		img = cv2.imread("public/pics/img.jpg",0)

		## <-------------- scale img here

		# edges
		can = cv2.Canny(img, 200,200)
		
		cv2.imwrite("public/pics/canny.jpg",can)
		return """<html><body>done<a href="/">back<a/>"""

if __name__ == '__main__':
	conf = {
		'global': { 
			'server.socket_host': '0.0.0.0',
			'server.socket_port': 8080,
			},
		'/' : {
			'tools.sessions.on': True,
			'tools.staticdir.root': os.path.abspath(os.getcwd())
		},
		'/picupload' : {
			'tools.sessions.on': True
		},
		'/control': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.response_headers.on': True,
			'tools.response_headers.headers': [('Content-Type', 'text/plain')],
		},
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': './public'
		}
	}
	
	webapp = MotorControl();
	webapp.control = MotorControlWebService()
	webapp.picupload = PictureUpload()
	cherrypy.quickstart(webapp,'/', conf)
