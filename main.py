# Author: Inao Latourrette
# GitHub: https://github.com/InaoLatu
# LinkedIn: https://www.linkedin.com/in/inaolatourrette/
# Contact: inao.latourrette@gmail.com


import string

from treelib import Node, Tree
import math
import secrets
from PIL import Image
import json
from base64 import b64decode, b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

# Input values
with open('image.jpg', 'rb') as f:
    original_image_bytes = f.read()

n_devices = 8  # power of two
banned_devices = [9, 11]  # Ids of the banned devices, In case of 8 devices the ids are 8,9,10,11,12,13,14,15.
# In case of 4 devices the ids are: 4, 5, 6, 7. Always the nodes at the last level of hierarchy.

levels = math.log(n_devices, 2)
key_set_length = 0
for i in range(int(levels + 1)):
    key_set_length += pow(2, i)
print(f"Key size: {key_set_length}")

keys = {}
for n in range(key_set_length):
    keys[str(int(n + 1))] = get_random_bytes(16)
print(f"Keys: {keys}")

k = get_random_bytes(16)
print(f'Random key k: {k}')


def create_tree():
    # It builds the tree starting from the root node (n1) with the key 1
    tree = Tree()
    tree.create_node('root(n1)', 1, data=[keys['1']])  # root node
    for a in range(int(levels)):
        for n in range(pow(2, a + 1)):
            id = pow(2, a + 1) + n
            tree.create_node('n' + str(id), id, parent=int(id / 2), data=[keys[str(id)]])
    tree.show()
    return tree


def get_banned_nodes(tree):
    # It checks the path from each banned device to the root to determine which nodes are banned
    nodes_banned = banned_devices.copy()
    for device_id in banned_devices:
        node = tree.get_node(device_id)
        while True:
            node = tree.get_node(node.predecessor(tree.identifier))
            nodes_banned.append(node.identifier)
            if node.is_root(tree.identifier):
                break
    nodes_banned = list(dict.fromkeys(nodes_banned))
    nodes_banned.sort()
    print(f'Nodes banned: {nodes_banned}')
    return nodes_banned


def build_cover(tree, nodes_banned):
    node = tree.get_node(1)
    cover = []
    # If no devices are banned
    if not nodes_banned:
        cover.append(node.data[0])
        return cover
    # It builds the cover with the ids
    for a in range(int(levels)):
        for n in range(pow(2, a + 1)):
            id = pow(2, a + 1) + n
            if id not in nodes_banned:
                node = tree.get_node(id)
                if node.predecessor(tree.identifier) in nodes_banned:
                    cover.append(id)
    return cover


def encryption(tree, cover):
    # encrypt the key k with the keys that build the cover
    output = {}
    for id, key in enumerate(cover):
        cipher = AES.new(keys[str(key)], AES.MODE_CBC)
        key_bytes = cipher.encrypt((pad(k, AES.block_size)))
        output[id] = b64encode(key_bytes).decode('utf-8')
    # encrypt the image m with key k and output those ciphered bytes
    cipher = AES.new(k, AES.MODE_CBC)
    cipher_image_bytes = cipher.encrypt((pad(original_image_bytes, AES.block_size)))
    output[id + 1] = cipher_image_bytes
    return output


def main():
    tree = create_tree()
    nodes_banned = get_banned_nodes(tree)
    cover = build_cover(tree, nodes_banned)

    print(f'Cover: ')
    for key in cover:
        print(f'k{key}: {keys[str(key)]}')

    # The output contains the key k ciphered with each key in the cover and the image ciphered with the key k
    output = encryption(tree, cover)
    print(output)


if __name__ == '__main__':
    main()
