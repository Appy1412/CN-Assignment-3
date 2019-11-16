import socket
import time
import threading
import random
import select
import time
from random import randint
import time

def between(a, b, c):
	return a <= b and b < c or c < a and a <= b or b < c and c < a

def getMessage(s, next_frame_to_send, frame_expected):
	message = s + str(next_frame_to_send) + str(frame_expected)
	return str.encode(message)

def inc(x):
	return (x+1) % (MAX_SEQ+1)

def mysend(client, message):
	time.sleep(delay_in_sec)
	client.settimeout(5)
	temp = randint(1, 100)
	if temp >= drop_rate_in_percent:	
		client.send(message)
		print('Sent', ord(message.decode()[0]) - 97, 'at', time.time())
		return 1
	else:
		print('Dropped', ord(message.decode()[0]) - 97)
		return 0


delay_in_sec = 0.01
drop_rate_in_percent = 5
MAX_SEQ = 7
buff = [0]*(MAX_SEQ+1)
message_size = 32
for i in range(MAX_SEQ+1):
	buff[i] = chr(i+97)*message_size

next_frame_to_send = 0
ack_expected = 0
frame_expected = 0

num_buffered = 0
timeout_in_seconds = 1

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Connecting....')
client.settimeout(15)
client.connect(('127.0.0.1', 5002))
print('Connected')

cnt = 0
total = 0

while True:
	# network layer ready event
	if num_buffered < MAX_SEQ:
		message = getMessage(buff[next_frame_to_send], next_frame_to_send, frame_expected)
		if mysend(client, message):
			cnt += 1
		total += 1
		num_buffered += 1
		next_frame_to_send = inc(next_frame_to_send)
		continue

	# frame arrival
	try:
		data = client.recv(message_size+2)
		data = str(data)[2:-1]
		# try:	
		# 	ack = int(data[-1])
		# 	seq = int(data[-2])
		# except:
		# 	print('????',data)
		# 	continue
		ack = int(data[-1])
		seq = int(data[-2])

		if(seq == frame_expected):
			print('Accepted', ord(data[0]) - 107, 'at', time.time())
			frame_expected = inc(frame_expected)
		else:
			print('Packet', seq, 'is ignored!')

		while (between(ack_expected, ack, next_frame_to_send)):
			num_buffered -= 1
			ack_expected = inc(ack_expected)

	except socket.timeout:
		print('Timed Out')
		next_frame_to_send = ack_expected
		for i in range(1, num_buffered+1):
			message = getMessage(buff[next_frame_to_send], next_frame_to_send, ack_expected)
			mysend(client, message)
			next_frame_to_send = inc(next_frame_to_send)
