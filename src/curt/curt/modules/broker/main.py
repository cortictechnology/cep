""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import socket

# from socket import *
import sys
import time
import os
import signal
import threading

cluster_brokers = []


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


os.system(
    "sed -i '/node.name = emqx@127.0.0.1/c\\node.name = emqx@"
    + get_ip_address()
    + "'  /root/emqx/etc/emqx.conf"
)

os.system("/root/emqx/bin/emqx start")

broadcast = True


def cleanup(sig, frame):
    global broadcast
    print("[INFO] You pressed `ctrl + c`! Exiting...")
    broadcast = False
    time.sleep(0.05)
    sys.exit()


def broadcast_fuc():
    global broadcast
    self_ip = get_ip_address()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)

    message = "curt_broker_available at " + self_ip
    try:
        while broadcast:
            #print("sending: " + message)
            for i in range(9):
                server_address = ("255.255.255.255", 9433 + i)
                sent = sock.sendto(message.encode(), server_address)
            time.sleep(3)
    finally:
        sock.close()


def receive_func():
    global cluster_brokers
    global broadcast
    self_ip = get_ip_address()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ("", 9434)
    sock.bind(server_address)
    while broadcast:
        data, address = sock.recvfrom(4096)
        data = str(data.decode("UTF-8"))
        if "curt_broker_available" in data and address[0] != self_ip:
            if address[0] not in cluster_brokers:
                print("Joining", address[0], " to form cluster")
                msg = os.popen(
                    "/root/emqx/bin/emqx_ctl cluster join emqx@" + address[0]
                ).read()
                if "already_in_cluster" in msg or "Join the cluster successfully":
                    cluster_brokers.append(address[0])
                    print("Join to cluster successed")


def main():
    signal.signal(signal.SIGINT, cleanup)
    broadcast_thread = threading.Thread(target=broadcast_fuc, daemon=True)
    receive_thread = threading.Thread(target=receive_func, daemon=True)
    broadcast_thread.start()
    receive_thread.start()
    broadcast_thread.join()
    receive_thread.join()


main()
