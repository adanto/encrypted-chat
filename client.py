#!/usr/bin/env python
#-*- encode: utf-8 -*-

import socket

target_host = "127.0.0.1"
target_port = 8080

def main():
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	client.connect((target_host, target_port))

	print "[*] Sending salutations"
	client.send("Hello there")

	response = client.recv(4096)

	print "[*] He says: %s" % response


if __name__ == "__main__":
	main()