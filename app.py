#!/usr/bin/env python
#-*- encode: utf-8 -*-

import socket
import threading
import sys
import time

bind_ip = "0.0.0.0"
bind_port = 8080


def main():
	server = threading.Thread(target=start_server)
	server.start()
	client = threading.Thread(target=start_client)
	client.start()


def start_client():

	time.sleep(1)
	target_host = raw_input("[*] Host to message with: ")
	target_port = int(raw_input("[*] Port: "))

	text = ""
	while text != "Exit":
		text = raw_input(">")

		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client.connect((target_host, target_port))

		client.send(text)


def start_server():
	global bind_port
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	while 1:

		try:
			server.bind((bind_ip, bind_port))
			break
		except Exception, e:

			print e
			bind_port += 1
			print "[*] New port:", bind_port


	server.listen(5)

	print "[*] Listening on %s:%d..." % (bind_ip, bind_port)

	while True:
		client, addr = server.accept()

		client_handler = threading.Thread(target=handle_client, args=(client, addr,))
		client_handler.start()



def handle_client(client_socket, addr):
	request = client_socket.recv(1024)

	print "\r[*] %s:%d: %s" % (addr[0], addr[1], request)

	client_socket.close()




if __name__ == "__main__":
	main()