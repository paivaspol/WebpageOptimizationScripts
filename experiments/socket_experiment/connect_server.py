import socket
import time
import os

pcap_filename = 'packet_log.pcap'
rm_tcpdump_cmd = 'rm {0}'.format(pcap_filename)
tcpdump_cmd = 'sudo tcpdump -i en0 -n -s 0 -w {0} &'.format(pcap_filename)

host = 'ec2-54-208-18-221.compute-1.amazonaws.com'
port = 80
request = 'GET / HTTP/1.0{0}Host: {1}{0}Connection: keep-alive{0}Accept: text/html{0}'.format('\r\n\r\n', host)

# Start tcpdump
os.system(rm_tcpdump_cmd)
os.system(tcpdump_cmd)

# Setup socket and download HTML
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the remote server.
print 'Connecting to {0}'.format(host)
start_time = time.time()
sock.connect((host, port))
print 'Connected to {0}'.format(host)
sock.send(request)
# result = sock.recv(1024)
# counter = 0
# 
# while True:
#     print str(time.time())
#     result = sock.recv(1024)
#     counter = counter + 1
#     if not result:
#         break
# 
# end_time = time.time()
# sock.close()

# print 'Total recv call: {0}'.format(counter)
print 'Start time: {0}, End time: {1}'.format(start_time, end_time)

# Kill tcpdump
time.sleep(5)
kill_tcpdump_cmd = 'sudo pkill tcpdump'
os.system(kill_tcpdump_cmd)
