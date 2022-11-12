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
    def __init__(self, user=None, data=None, timestamp=None, content=None, alias=None, flags=None):
        self.user = user
        self.alias = alias
        if not data is None:
            self.roll = Roll(**data)
        else:
            self.roll = None
        self.timestamp = datetime.fromtimestamp(timestamp)
        self.content = content

        self.saving_throw = None
        self.skill_check = None
        self.ability_check = None
        self.attack = False
        self.damage = False
        self.hitDie = False
        self.deathSave = False
        self.attack_item = None
        self.damage_item = None
        if 'dnd5e' in flags:
            dnd_flags = flags['dnd5e']
            if 'roll' in dnd_flags:
                type = dnd_flags['roll']['type']
                if type == 'ability':
                    self.ability_check = dnd_flags['roll']['abilityId']
                elif type == 'attack':
                    self.attack = True
                    self.attack_item = dnd_flags['roll']['itemId']
                elif type == 'damage':
                    self.damage = True
                    self.damage_item = dnd_flags['roll']['itemId']
                elif type == 'death':
                    self.saving_throw = 'death'
                    self.deathSave = True
                elif type == 'hitDie':
                    self.hitDie = True
                elif type == 'save':
                    self.saving_throw = dnd_flags['roll']['abilityId']
                elif type == 'skill':
                    self.skill_check = dnd_flags['roll']['skillId']

    def get_dice(self) -> List[Die]:
        if self.roll is None:
            return []
        roll: Roll = self.roll
        return roll.dice

    def has_d20(self) -> bool:
        dice = self.get_dice()
        for die in dice:
            if die.is_dx(20):
                return True
        return False

    def is_saving_throw(self) -> bool:
        return not self.saving_throw is None

    def save_type(self) -> str:
        return self.saving_throw

    def is_skill_check(self) -> bool:
        return not self.skill_check is None

    def skill_type(self) -> str:
        return self.skill_check

    def is_ability_check(self) -> bool:
        return not self.ability_check is None

    def ability_type(self) -> str:
        return self.ability_check

    def is_attack(self) -> bool:
        return self.attack

    def is_damage(self) -> bool:
        return self.damage
    
    def is_hit_die(self) -> bool:
        return self.hitDie

    def __str__(self):
        return f"{self.timestamp} {self.user} {self.roll}"

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
            "alias": alias,
            "flags": raw['flags']
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

def get_d20_messages(messages: List[Message]) -> List[Message]:
    dice = get_all_dice(messages)
    return [message for message in messages if message.has_d20()]

def count_advantage(dice: List[Die]) -> int:
    return len([die for die in dice if die.advantage])

def count_disadvantage(dice: List[Die]) -> int:
    return len([die for die in dice if die.disadvantage])

def count_skill_check(messages: List[Message]) -> int:
    return len([message for message in messages if message.is_skill_check()])

def count_ability_check(messages: List[Message]) -> int:
    return len([message for message in messages if message.is_ability_check()])

def count_saving_throw(messages: List[Message]) -> int:
    return len([message for message in messages if message.is_saving_throw()])

def count_attack_roll(messages: List[Message]) -> int:
    return len([message for message in messages if message.is_attack()])

def filter_user(messages: List[Message], user: str) -> List[Message]:
    return list(filter(lambda message: message.user == user, messages))

def generate_d20_data(messages: List[Message], user=None) -> Dict[str, float]:
    if not user is None:
        messages = filter_user(messages, user)

    d20s = get_d20s(messages)
    d20s_messages = get_d20_messages(messages)
    d20_count = sum([die.number for die in d20s])
    roll_count = len(d20s) # Number of rolls (advantage and disadvantage count as 1)
    advantage_count = count_advantage(d20s)
    disadvantage_count = count_disadvantage(d20s)
    skill_check_count = count_skill_check(d20s_messages)
    ability_check_count = count_ability_check(d20s_messages)
    saving_throw_count = count_saving_throw(d20s_messages)
    attack_roll_count = count_attack_roll(d20s_messages)
    advantage_ratio = advantage_count / roll_count
    disadvantage_ratio = disadvantage_count / roll_count

    return {
        'raw_count': d20_count,
        'roll_count': roll_count,
        'advantage_count': advantage_count,
        'disadvantage_count': disadvantage_count,
        'advantage_ratio': advantage_ratio,
        'disadvantage_ratio': disadvantage_ratio,    
        'skill_check_count': skill_check_count,
        'skill_check_ratio': skill_check_count / roll_count,
        'ability_check_count': ability_check_count,
        'ability_check_ratio': ability_check_count / roll_count,
        'saving_throw_count': saving_throw_count,
        'saving_throw_ratio': saving_throw_count / roll_count,
        'attack_roll_count': attack_roll_count,
        'attack_roll_ratio': attack_roll_count / roll_count,
    }

def run(filename: str):
    messages = load_zip_file(filename)
    messages = apply_april_fools_filter(messages)

    all = generate_d20_data(messages, user=None)
    all['player'] = 'All'
    d20_data = [
        all
    ]

    users = ['Gamemaster', 'threshprince', 'OneRandomThing', 'Igazsag', 'teagold']
    for user in users:
        user_data = generate_d20_data(messages, user=user)
        user_data['player'] = user
        d20_data.append(user_data)

    with open('d20_data.json', 'w') as f:
        json.dump(d20_data, f, indent=4)


if __name__ == "__main__":
    filename = sys.argv[1]
    run(filename)
