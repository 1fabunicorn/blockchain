import random
import subprocess
import requests
from time import sleep

num_of_nodes = 10

for i in range(0, num_of_nodes):
    print("[Blockchain Simulation] Running `docker run --rm -p {}:5000 -d blockchain`".format(80 + i))
    subprocess.call("docker run --rm -p {}:5000 -d blockchain".format(80 + i), shell=True)

node_ips = ["http://172.17.0.{}:5000".format(2 + i) for i in range(num_of_nodes)]  # create list of a node ips with port
data = {"nodes": [node_ips]}

sleep(1)
for node in node_ips:
    print("[Blockchain Simulation] POST:{} JSON:{}".format(node, node_ips))
    requests.post(node, data=data)  # send nodes all the nodes IP's


def exit_():
    print("[Blockchain Simulation] Exiting, stopping containers")
    subprocess.call("docker stop $(docker ps -q --filter ancestor=blockchain)", shell=True)


def help_():
    print("")


def tick():
    for node_ in node_ips:
        print(requests.get("{}/nodes/resolve".format(node_)).text)


def mine(n):
    for node_ in random.sample(node_ips, int(n)):
        print("[Blockchain Simulation] node {} mining".format(node_))
        requests.get("{}/mine".format(node_))
        tick()  # resolves


def transact(n):
    pass


def print_chain():
    print(requests.get("{}/chain".format(random.choice(node_ips))).text)  # send nodes all the nodes IP's


while True:
    sleep(.5)
    tick()
    command = input("[Blockchain Simulation] $ ")
    if command.split()[0].lower()[0] == "q":
        exit_()
        quit(0)
    if command.split()[0].lower()[0] == "h":
        help_()
    if command.split()[0].lower()[0] == "m":
        mine(command.split()[1])
    if command.split()[0].lower()[0] == "c":
        print_chain()
