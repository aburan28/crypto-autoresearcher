import json
import os

with open(os.path.dirname(os.path.realpath(__file__)) + '/mayo1.json', 'r') as jf:
    mayo1 = json.load(jf)
