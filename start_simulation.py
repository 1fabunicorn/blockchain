import random
import subprocess
import json
import requests
from concurrent.futures import ThreadPoolExecutor
from time import sleep

num_of_nodes = 25

print("Creating {} blockchain node containers".format(num_of_nodes))
for i in range(0, num_of_nodes):
    print("{:.2%} done".format(i / num_of_nodes), end="\r")
    subprocess.call("docker run --rm -p {}:5000 -d blockchain".format(80 + i), shell=True, stdout=subprocess.DEVNULL)

node_ips = ["http://172.17.0.{}:5000".format(2 + i) for i in range(num_of_nodes)]  # create list of a node ips with port
data = {"nodes": node_ips}


def exit_():
    print("[Blockchain Simulation] Exiting, stopping containers")
    subprocess.call("docker stop $(docker ps -q --filter ancestor=blockchain)", shell=True)


def help_():
    print("")


def register_node(node_url):
    return requests.post("{}/nodes/register".format(node_url), json=data)


def resolve_node(node_url):
    return requests.get("{}/nodes/resolve".format(node_url))


def register_all_nodes():
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(register_node, node_ips))


def resolve_all_nodes():
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(resolve_node, node_ips))


def mine(n):
    if n > num_of_nodes:
        return "Error: Told {} nodes to mine, only {} nodes on the network".format(n, num_of_nodes)
    register_all_nodes()
    for node_ in random.sample(node_ips, int(n)):
        print("[Blockchain Simulation] node {} mining".format(node_))
        json_object = json.loads(requests.get("{}/mine".format(node_)).text)
        print(json.dumps(json_object, indent=2))
        resolve_all_nodes()  # resolves


def transact(n):
    pass


def print_chain():
    print(requests.get("{}/chain".format(random.choice(node_ips))).text)  # send nodes all the nodes IP's


while True:
    sleep(.5)
    # tick()
    command = input("[Blockchain Simulation] $ ")
    if command.split()[0].lower()[0] == "q":
        exit_()
        quit(0)
    if command.split()[0].lower()[0] == "h":
        help_()
    if command.split()[0].lower()[0] == "m":
        mine(int(command.split()[1]))
    if command.split()[0].lower()[0] == "c":
        print_chain()
