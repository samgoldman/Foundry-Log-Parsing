import json
import sys
from copy import deepcopy
from datetime import datetime
from typing import Dict, List


class Die(object):

    def __init__(self, options=None, evaluated=None, number=None, faces=None, modifiers=None, results=None):
        self.options = options
        self.evaluated = evaluated
        self.number = number
        self.faces = faces
        self.modifiers = modifiers
        self.results = results
        self.inactive_results = []
        self.active_results = []
        self.advantage = False
        self.disadvantage = False

        for r in results:
            if r['active']:
                self.active_results.append(r['result'])
            else:
                self.inactive_results.append(r['result'])

        if 'advantage' in self.options and self.options['advantage']:
            self.advantage = True
        if 'disadvantage' in self.options and self.options['disadvantage']:
            self.disadvantage = True

    def is_dx(self, x: int) -> bool:
        return self.faces == x

    def get_all_dice_results(self):
        results: List[Dict] = self.results
        return list(map(lambda res: res['result'], results))

    def __str__(self):
        return f"{self.number}d{self.faces}"

    def __repr__(self):
        return self.__str__()

class Roll(object):

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

    def __str__(self):
        return f"{{{self.roll_type}: [{self.formula}] [{[d for d in self.dice]}] = [{self.total}]}}"

class Message(object):
    def __init__(self, user=None, data=None, timestamp=None, content=None, alias=None):
        self.user = user
        self.alias = alias
        if not data is None:
            self.roll = Roll(**data)
        else:
            self.roll = None
        self.timestamp = datetime.fromtimestamp(timestamp)
        self.content = content

    def get_dice(self) -> List[Die]:
        if self.roll is None:
            return []
        roll: Roll = self.roll
        return roll.dice

    def __str__(self):
        return f"{self.timestamp} {self.user} {self.roll}"

def load_json_file(filename) -> List[Message]:
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

def load_zip_file(filename: str) -> List[Message]:
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
        alias = raw['speaker']['alias'] if 'alias' in raw['speaker'] else None
        if type(d) == str:
            d = json.loads(d)
        data.append({
            "user": user_map[raw['user']],
            "data": d,
            "timestamp": int(raw['timestamp'] / 1000),
            "content": raw['content'],
            "alias": alias
        })
    for d in data:
        if "data" in d and not d["data"] is None:
            if "class" in d["data"]:
                d["data"]["roll_type"] = d["data"]["class"]
                del d["data"]["class"]
    data = [Message(**d) for d in data]
    data.sort(key=lambda d: d.timestamp)
    return data

def flatten(l):
    return [item for sublist in l for item in sublist]

def apply_april_fools_filter(messages: List[Message]) -> List[Message]:
    filtered = []
    in_april_fools = False

    for message in messages:
        if '# April Fools Marker' in message.content:
            in_april_fools = True

        if '#End April Fools' in message.content:
            in_april_fools = False
        
        if not in_april_fools:
            filtered.append(message)

    return filtered

def get_all_dice(messages: List[Message]) -> List[Die]:
    dice = [m.get_dice() for m in messages]
    dice = flatten(dice)
    return dice

def generate_die_type_count(messages: List[Message]) -> Dict[int, int]:
    dice = get_all_dice(messages)
    unique_die_types = set([die.faces for die in dice])
    data = {}
    for die_type in unique_die_types:
        count = sum([die.number for die in dice if die.is_dx(die_type)])
        data[die_type] = count
    return data

def generate_die_type_average(messages: List[Message]) -> Dict[int, int]:
    dice = get_all_dice(messages)
    data = generate_die_type_count(messages)
    for die_type in data.keys():
        count = data[die_type]
        total_value = sum(flatten([die.get_all_dice_results() for die in dice if die.is_dx(die_type)]))
        data[die_type] = total_value / count
    return data

def get_d20s(messages: List[Message]) -> List[Die]:
    dice = get_all_dice(messages)
    return [die for die in dice if die.is_dx(20)]

def count_advantage(dice: List[Die]) -> List[Die]:
    return len([die for die in dice if die.advantage])

def count_disadvantage(dice: List[Die]) -> List[Die]:
    return len([die for die in dice if die.disadvantage])

def filter_user(messages: List[Message], user: str) -> List[Message]:
    return list(filter(lambda message: message.user == user, messages))

def generate_d20_data(messages: List[Message], user=None) -> Dict[str, float]:
    if not user is None:
        messages = filter_user(messages, user)

    d20s = get_d20s(messages)
    d20_count = sum([die.number for die in d20s])
    roll_count = len(d20s) # Number of rolls (advantage and disadvantage count as 1)
    advantage_count = count_advantage(d20s)
    disadvantage_count = count_disadvantage(d20s)
    advantage_ratio = advantage_count / roll_count
    disadvantage_ratio = disadvantage_count / roll_count

    return {
        'raw_count': d20_count,
        'roll_count': roll_count,
        'advantage_count': advantage_count,
        'disadvantage_count': disadvantage_count,
        'advantage_ratio': advantage_ratio,
        'disadvantage_ratio': disadvantage_ratio,
    }

def run(filename: str):
    if filename.endswith('zip'):
        messages = load_zip_file(filename)
    else:
        messages = load_json_file(filename)
    
    messages = apply_april_fools_filter(messages)

    d20_data = {
        'All': generate_d20_data(messages, user=None)
    }

    users = ['Gamemaster', 'threshprince', 'OneRandomThing', 'Igazsag', 'teagold']
    for user in users:
        d20_data[user] = generate_d20_data(messages, user=user)

    print(d20_data)

    # count_d347 = sum([d.number for d in dice if d.is_d347()])
    # count_d100 = sum([d.number for d in dice if d.is_d100()])
    # count_d20 = sum([d.number for d in dice if d.is_d20()])
    # count_d12 = sum([d.number for d in dice if d.is_d12()])
    # count_d10 = sum([d.number for d in dice if d.is_d10()])
    # count_d8 = sum([d.number for d in dice if d.is_d8()])
    # count_d6 = sum([d.number for d in dice if d.is_d6()])
    # count_d4 = sum([d.number for d in dice if d.is_d4()])
    # print(sorted([str(d) for d in dice if not (d.is_d347() or d.is_d100() or d.is_d20() or d.is_d12() or d.is_d10() or d.is_d8() or d.is_d6() or d.is_d4() ) ]))
    # print(count_d347)
    # print(count_d100)
    # print(count_d20)
    # print(count_d12)
    # print(count_d10)
    # print(count_d8)
    # print(count_d6)
    # print(count_d4)

    # total_value_d347 = sum(flatten([d.active_results + d.inactive_results for d in dice if d.is_d347()]))
    # total_value_d100 = sum(flatten([d.active_results + d.inactive_results for d in dice if d.is_d100()]))
    # total_value_d20 = sum(flatten([d.active_results + d.inactive_results for d in dice if d.is_d20()]))
    # total_value_d12 = sum(flatten([d.active_results + d.inactive_results for d in dice if d.is_d12()]))
    # total_value_d10 = sum(flatten([d.active_results + d.inactive_results for d in dice if d.is_d10()]))
    # total_value_d8 = sum(flatten([d.active_results + d.inactive_results for d in dice if d.is_d8()]))
    # total_value_d6 = sum(flatten([d.active_results + d.inactive_results for d in dice if d.is_d6()]))
    # total_value_d4 = sum(flatten([d.active_results + d.inactive_results for d in dice if d.is_d4()]))
    # print(total_value_d347 / count_d347)
    # print(total_value_d100 / count_d100)
    # print(total_value_d20 / count_d20)
    # print(total_value_d12 / count_d12)
    # print(total_value_d10 / count_d10)
    # print(total_value_d8 / count_d8)
    # print(total_value_d6 / count_d6)
    # print(total_value_d4 / count_d4)

    # aliases = filter(lambda a: not a is None, [message.alias for message in data])
    # unique_aliases = set(aliases)
    # for a in sorted(unique_aliases):
    #     print(a)
    # print(len(unique_aliases))

if __name__ == "__main__":
    filename = sys.argv[1]
    run(filename)
