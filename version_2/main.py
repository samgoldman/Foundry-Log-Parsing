from copy import deepcopy
import json
import sys
from datetime import datetime
from typing import List

class Die(object):

    def __init__(self, options=None, evaluated=None, number=None, faces=None, modifiers=None, results=None):
        self.options = options
        self.evaluated = evaluated
        self.number = number
        self.faces = faces
        self.modifiers = modifiers
        self.results = results
        self.inactive_results = []
        self.advantage = False
        self.disadvantage = False

        for r in results:
            if r['active']:
                self.result = r['result']
            else:
                self.inactive_results.append(r['result'])

        if 'advantage' in self.options and self.options['advantage']:
            self.advantage = True
        if 'disadvantage' in self.options and self.options['disadvantage']:
            self.disadvantage = True

    def __str__(self):
        return f"adv={self.advantage} {self.result} ({self.inactive_results})"

    def __repr__(self):
        return self.__str__()

class Roll(object):
    options = None
    dice: List[Die] = []
    formula = None
    reliable_talent = None
    total = None
    roll_type = None
    def __init__(self, formula=None, roll_type=None, options=None, dice=None, terms=None, total=None, evaluated=None):
        _dice = dice # Ignore `dice` - it is extremely rare that it's used

        self.formula = formula
        self.roll_type = roll_type
        self.total = total
        self.dice = []
        self.terms = deepcopy(terms)

        for t in terms:
            if t['class'] == 'Die':
                del t['class']
                self.dice.append(Die(**t))

        # print("Options:", options, "\nTerms:", terms)

    def __str__(self):
        return f"{{{self.roll_type}: [{self.formula}] [{[d for d in self.dice]}] = [{self.total}]}}"

class Message(object):
    user = None
    roll = None
    timestamp = None
    content = None

    def __init__(self, user=None, data=None, timestamp=None, content=None):
        self.user = user
        if not data is None:
            self.roll = Roll(**data)
        self.timestamp = datetime.fromtimestamp(timestamp)
        self.content = content

    def __str__(self):
        return f"{self.timestamp} {self.user} {self.roll}"

def load_json_file(filename):
    file = open(filename)
    data = json.load(file)
    for d in data:
        if "data" in d and not d["data"] is None:
            if "class" in d["data"]:
                d["data"]["roll_type"] = d["data"]["class"]
                del d["data"]["class"]
    data = [Message(**d) for d in data]
    file.close()
    return data

def load_zip_file(filename: str):
    import zipfile
    archive = zipfile.ZipFile(filename, 'r')

    user_map = {None: 'UNKNOWN USER'}
    for line in archive.open('salocaia/data/users.db'):
        raw = json.loads(line)
        user_map[raw['_id']] = raw['name']

    raw_data = []
    for line in archive.open('salocaia/data/messages.db'):
        raw_data.append(json.loads(line))
    data = []
    for raw in raw_data:
        d = raw["roll"] if "roll" in raw else None
        if type(d) == str:
            d = json.loads(d)
        data.append({
            "user": user_map[raw['user']],
            "data": d,
            "timestamp": int(raw['timestamp'] / 1000),
            "content": raw['content']
        })
    for d in data:
        if "data" in d and not d["data"] is None:
            if "class" in d["data"]:
                d["data"]["roll_type"] = d["data"]["class"]
                del d["data"]["class"]
    data = [Message(**d) for d in data]
    data.sort(key=lambda d: d.timestamp)
    return data

def run(filename: str):
    if filename.endswith('zip'):
        data = load_zip_file(filename)
    else:
        data = load_json_file(filename)
    print(data[70])
    print(data[4936])
    print(data[-1])

if __name__ == "__main__":
    filename = sys.argv[1]
    run(filename)
