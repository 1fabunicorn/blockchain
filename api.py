import subprocess
from concurrent.futures.thread import ThreadPoolExecutor
from itertools import product

import requests


class API:
    def __init__(self):
        self.node_count = 15
        self.docker_ip_offset = 1
        create_nodes = True
        if create_nodes:
            self.create_nodes(self.node_count, self.docker_ip_offset)
        self.node_ips = ["http://172.17.0.{}:5000".format(2 + i + self.docker_ip_offset) for i in
                         range(self.node_count)]
        self.node_data = {"nodes": self.node_ips}  # all node IPs for nodes to connect to each other

    def register_node(self, node_url):
        return requests.post("{}/nodes/register".format(node_url), json=self.node_data)

    def register_all_nodes(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(self.register_node, self.node_ips))

    def resolve_all_nodes(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(self.resolve_node, self.node_ips))

    @staticmethod
    def resolve_node(node_url):
        return requests.get("{}/nodes/resolve".format(node_url))

    @staticmethod
    def create_nodes(node_count, docker_ip_offset):
        print("Creating {} blockchain node containers".format(node_count))
        for i in range(0, node_count):
            print("{:.2%} done".format(i / node_count), end="\r")
            subprocess.call("docker run --rm -p {}:5000 -d blockchain".format(80 + i + docker_ip_offset), shell=True,
                            stdout=subprocess.DEVNULL)

    @staticmethod
    def transact_worker(sender, recipient, amount, extra_data, node_url):
        tx = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            extra_data: extra_data
        }
        return requests.post("{}/transactions/new".format(node_url), json=tx)

    def transact(self, sender, recipient, amount, extra_data):
        print("Broadcasting transaction with merkle root".format(extra_data))
        with ThreadPoolExecutor(max_workers=2) as pool:
            params = [sender, recipient, amount, self.node_ips]
            pool.starmap(self.transact_worker, product(params, repeat=5))
