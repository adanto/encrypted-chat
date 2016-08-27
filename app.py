#!/usr/bin/env python

from flask import *
from Queue import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import socket
import threading
import sys
import time
import binascii


###################################################################################################################################################
###################################################################################################################################################
############################################################    APP CONFIG     ####################################################################
###################################################################################################################################################
###################################################################################################################################################

app = Flask(__name__)

app.config["APP_IP"] = "0.0.0.0"
app.config["APP_PORT"] = 5000

app.config["BIND_IP"] = "0.0.0.0"
app.config["BIND_PORT"] = 8080
app.config["SERVER_RUNNING"] = False

app.config["TARGET_IP"] = None
app.config["TARGET_PORT"] = None

app.config["STARTED"] = False

app.config["MESSAGES"] = Queue() 

app.config["PRIV_CERT"] = None 
app.config["PUB_CERT"] = None 

app.config["REMOTE_CERT"] = None

app.config["REMOTE_CIPHER"] = None
app.config["LOCAL_CIPHER"] = None



###################################################################################################################################################
###################################################################################################################################################
###############################################################    AJAX     #######################################################################
###################################################################################################################################################
###################################################################################################################################################

@app.route('/new_msg', methods=["POST"])
def new_msg():

	app.config["MESSAGES"].put(((app.config["BIND_IP"], app.config["BIND_PORT"]), request.form['data']))
	send_text(request.form['data'])

	return "ACK!"



@app.route('/updates')
def update():


	if app.config["MESSAGES"].empty():
		return jsonify(0)


	return jsonify(app.config["MESSAGES"].get())

###################################################################################################################################################
###################################################################################################################################################
##############################################################     URLS     #######################################################################
###################################################################################################################################################
###################################################################################################################################################

@app.route("/test")
def test():
	return "hi<br/>hi hi"

@app.route("/", methods=['GET', 'POST'])
def salute():

	if not app.config["SERVER_RUNNING"]:

		server = threading.Thread(target=start_server)
		server.start()

		while not app.config["SERVER_RUNNING"]:
			time.sleep(1)

		app.config["PRIV_CERT"] = RSA.generate(4096)
		app.config["PUB_CERT"] = app.config["PRIV_CERT"].publickey()

	if request.method == 'POST':

		app.config["TARGET_IP"] = request.form['ip']
		app.config["TARGET_PORT"] = request.form['port']
		app.config["REMOTE_CERT"] = RSA.importKey(request.form['cert'])


		app.config["REMOTE_CIPHER"] = PKCS1_OAEP.new(app.config["REMOTE_CERT"])

		app.config["LOCAL_CIPHER"] = PKCS1_OAEP.new(app.config["PRIV_CERT"])


		return redirect(url_for("chat_handler"))



		app.config["STARTED"] = True

	return render_template('salute.html', test="", addr=(app.config["BIND_IP"], app.config["BIND_PORT"]), pub_key=app.config["PUB_CERT"].exportKey('PEM').split("\n"), priv_key=app.config["PRIV_CERT"].exportKey('PEM').split("\n"))



@app.route("/chat", methods=['GET', 'POST'])
def chat_handler():

	if request.method == "POST":
		
		send_text(request.form['usermsg'])
		return

	else:
		return render_template("chat.html")

###################################################################################################################################################
###################################################################################################################################################
#############################################################     SERVER     ######################################################################
###################################################################################################################################################
###################################################################################################################################################

def start_server():

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	while 1:

		try:
			server.bind((app.config["BIND_IP"], app.config["BIND_PORT"]))
			break
		except Exception, e:

			print e
			app.config["BIND_PORT"] += 1
			print "[*] New port:", app.config["BIND_PORT"]


	server.listen(5)

	app.config["SERVER_RUNNING"] = True
	print "[*] Listening on %s:%d..." % (app.config["BIND_IP"], app.config["BIND_PORT"])

	while True:
		client, addr = server.accept()

		client_handler = threading.Thread(target=handle_client, args=(client, addr,))
		client_handler.start()



def handle_client(client_socket, addr):
	request = client_socket.recv(4096)

	print request


	app.config["MESSAGES"].put((addr, request))

	print "\r[*] %s:%d: %s" % (addr[0], addr[1], request)

	client_socket.close()


###################################################################################################################################################
###################################################################################################################################################
#############################################################     CLIENT     ######################################################################
###################################################################################################################################################
###################################################################################################################################################


def send_text(text):

	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect((app.config["TARGET_IP"], int(app.config["TARGET_PORT"])))

	client.send(binascii.hexlify(app.config["LOCAL_CIPHER"].encrypt(text.encode('utf-8'))))


###################################################################################################################################################
###################################################################################################################################################
###################################################################################################################################################
###################################################################################################################################################
###################################################################################################################################################


if __name__ == "__main__":

	while 1:
		try:
			app.run(debug=False, host=app.config["APP_IP"], port=app.config["APP_PORT"], threaded=True)
			break
		except Exception, e:
			app.config["APP_PORT"] += 1