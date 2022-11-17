import json
import sys
from copy import deepcopy
from datetime import datetime
from typing import Dict, List


class Die(object):
    def __init__(
        self,
        options=None,
        evaluated=None,
        number=None,
        faces=None,
        modifiers=None,
        results=None,
    ):
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
            if r["active"]:
                self.active_results.append(r["result"])
            else:
                self.inactive_results.append(r["result"])

        if "advantage" in self.options and self.options["advantage"]:
            self.advantage = True
        if "disadvantage" in self.options and self.options["disadvantage"]:
            self.disadvantage = True

    def is_dx(self, x: int) -> bool:
        return self.faces == x

    def get_all_dice_results(self):
        results: List[Dict] = self.results
        return list(map(lambda res: res["result"], results))

    def is_nat_20(self) -> bool:
        return self.active_results[0] == 20

    def is_nat_1(self) -> bool:
        return self.active_results[0] == 1

    def is_stolen_nat_20(self) -> bool:
        return (
            self.disadvantage
            and self.active_results[0] != 20
            and self.inactive_results[0] == 20
        )

    def is_super_nat_20(self) -> bool:
        return (
            self.advantage
            and self.active_results[0] == 20
            and self.inactive_results[0] == 20
        )

    def is_disadvantage_nat_20(self) -> bool:
        return (
            self.disadvantage
            and self.active_results[0] == 20
            and self.inactive_results[0] == 20
        )

    def is_dropped_nat_1(self) -> bool:
        return (
            self.advantage
            and self.active_results[0] != 1
            and self.inactive_results[0] == 1
        )

    def is_super_nat_1(self) -> bool:
        return (
            self.disadvantage
            and self.active_results[0] == 1
            and self.inactive_results[0] == 1
        )

    def is_advantage_nat_1(self) -> bool:
        return (
            self.advantage
            and self.active_results[0] == 1
            and self.inactive_results[0] == 1
        )

    def __str__(self):
        return f"{self.number}d{self.faces}"

    def __repr__(self):
        return self.__str__()


class Roll(object):
    def __init__(
        self,
        formula=None,
        roll_type=None,
        options=None,
        dice=None,
        terms=None,
        total=None,
        evaluated=None,
        **kwargs,
    ):
        _dice = dice  # Ignore `dice` - it is extremely rare that it's used

        self.formula = formula
        self.roll_type = roll_type
        self.total = total
        self.dice = []
        self.terms = deepcopy(terms)

        for t in terms:
            if t["class"] == "Die":
                del t["class"]
                self.dice.append(Die(**t))

    def __str__(self):
        return f"{{{self.roll_type}: [{self.formula}] [{[d for d in self.dice]}] = [{self.total}]}}"


class Message(object):
    def __init__(
        self,
        user=None,
        data=[],
        timestamp=None,
        content=None,
        alias=None,
        flags=None,
        raw=None,
    ):
        self.user = user
        self.alias = alias
        if not data is None:
            self.rolls = [Roll(**d) for d in data]
        else:
            self.rolls = []
        self.timestamp = datetime.fromtimestamp(timestamp)
        self.content = content
        self.raw = raw

        self.saving_throw = None
        self.skill_check = None
        self.ability_check = None
        self.attack = False
        self.damage = False
        self.hitDie = False
        self.deathSave = False
        self.attack_item = None
        self.damage_item = None
        self.initiative = False
        if "dnd5e" in flags:
            dnd_flags = flags["dnd5e"]
            if "roll" in dnd_flags:
                type = dnd_flags["roll"]["type"]
                if type == "ability":
                    self.ability_check = dnd_flags["roll"]["abilityId"]
                elif type == "attack":
                    self.attack = True
                    self.attack_item = dnd_flags["roll"]["itemId"]
                elif type == "damage":
                    self.damage = True
                    self.damage_item = dnd_flags["roll"]["itemId"]
                elif type == "death":
                    self.saving_throw = "death"
                    self.deathSave = True
                elif type == "hitDie":
                    self.hitDie = True
                elif type == "save":
                    self.saving_throw = dnd_flags["roll"]["abilityId"]
                elif type == "skill":
                    self.skill_check = dnd_flags["roll"]["skillId"]
        elif "core" in flags:
            if "initiativeRoll" in flags["core"] and flags["core"]["initiativeRoll"]:
                self.initiative = True

    def get_dice(self) -> List[Die]:
        dice = []
        for roll in self.rolls:
            dice += roll.dice
        return dice

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

    def is_initiative_roll(self) -> bool:
        return self.initiative

    def ability_type(self) -> str:
        return self.ability_check

    def is_attack(self) -> bool:
        return self.attack

    def is_damage(self) -> bool:
        return self.damage

    def is_hit_die(self) -> bool:
        return self.hitDie

    def __str__(self):
        return f"{self.timestamp} {self.user} {self.content} {self.rolls}"


def load_zip_file(filename: str, world_name: str) -> List[Message]:
    import zipfile

    archive = zipfile.ZipFile(filename, "r")

    user_map = {None: "UNKNOWN USER"}
    for line in archive.open(f"{world_name}/data/users.db"):
        raw = json.loads(line)
        user_map[raw["_id"]] = raw["name"]

    raw_data = []
    for line in archive.open(f"{world_name}/data/messages.db"):
        raw_data.append(json.loads(line))

    for line in open(f"chat.db"):
        raw_data.append(json.loads(line))
    data = []
    for raw in raw_data:
        if "$$deleted" in raw and raw["$$deleted"]:
            continue
        roll_data = []
        if "roll" in raw:
            roll_data.append(raw["roll"])
        if "rolls" in raw:
            roll_data = raw["rolls"]

        alias = raw["speaker"]["alias"] if "alias" in raw["speaker"] else None

        for i in range(len(roll_data)):
            if type(roll_data[i]) == str:
                roll_data[i] = json.loads(roll_data[i])
        data.append(
            {
                "user": user_map[raw["user"]],
                "data": roll_data,
                "timestamp": int(raw["timestamp"] / 1000),
                "content": raw["content"],
                "alias": alias,
                "flags": raw["flags"],
                "raw": raw,
            }
        )
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
        if "# April Fools Marker" in message.content:
            in_april_fools = True

        if "#End April Fools" in message.content:
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
        total_value = sum(
            flatten([die.get_all_dice_results() for die in dice if die.is_dx(die_type)])
        )
        data[die_type] = total_value / count
    return data


def get_d20s(messages: List[Message]) -> List[Die]:
    dice = get_all_dice(messages)
    return [die for die in dice if die.is_dx(20)]


def count_advantage(dice: List[Die]) -> int:
    return len([die for die in dice if die.advantage])


def count_disadvantage(dice: List[Die]) -> int:
    return len([die for die in dice if die.disadvantage])


def count_nat_20s(dice: List[Die]) -> int:
    return len([die for die in dice if die.is_nat_20()])


def count_nat_1s(dice: List[Die]) -> int:
    return len([die for die in dice if die.is_nat_1()])


def count_msgs_if(messages: List[Message], function, expected) -> int:
    return len(get_matching_msgs(messages, function, expected))


def get_matching_msgs(messages: List[Message], function, expected) -> int:
    return [message for message in messages if function(message) == expected]


def inverse_filter_user(messages: List[Message], user: str) -> List[Message]:
    return list(filter(lambda message: message.user != user, messages))


def average_raw_d20_roll(dice: List[Die]) -> float:
    all_active = [die.active_results[0] for die in dice]
    all_inactive = [
        die.inactive_results[0] for die in dice if len(die.inactive_results) > 0
    ]
    all = all_active + all_inactive
    total_value = sum(all)
    count = len(all)
    return total_value / count


def average_final_d20_roll(messages: List[Message]) -> float:
    dice = get_d20s(messages)
    all_active = [die.active_results[0] for die in dice]
    total_value = sum(all_active)
    count = len(all_active)
    return total_value / count


def average_d20_after_modifiers(messages: List[Message]) -> float:
    total_value = sum(
        flatten([[roll.total for roll in message.rolls] for message in messages])
    )
    count = len(messages)
    return total_value / count


def saving_throw_average(messages: List[Message], save_type: str) -> int:
    count = count_msgs_if(messages, Message.save_type, save_type)
    if count == 0:
        return 0.0
    return average_d20_after_modifiers(
        [message for message in messages if message.save_type() == save_type]
    )


def ability_check_average(messages: List[Message], ability_type: str) -> int:
    count = count_msgs_if(messages, Message.ability_type, ability_type)
    if count == 0:
        return 0.0
    return average_d20_after_modifiers(
        [message for message in messages if message.ability_type() == ability_type]
    )


def skill_check_average(messages: List[Message], skill_type: str) -> int:
    count = count_msgs_if(messages, Message.skill_type, skill_type)
    if count == 0:
        return 0.0
    return average_d20_after_modifiers(
        [message for message in messages if message.skill_type() == skill_type]
    )


def generate_skill_data(messages: List[Message]) -> Dict[str, float]:
    skills = [
        "acr",
        "ani",
        "arc",
        "ath",
        "dec",
        "his",
        "ins",
        "itm",
        "inv",
        "med",
        "nat",
        "prc",
        "prf",
        "per",
        "rel",
        "slt",
        "ste",
        "sur",
    ]
    data = {}
    for id in skills:
        data[f"{id}_skill_count"] = count_msgs_if(messages, Message.skill_type, id)
        data[f"{id}_skill_average"] = skill_check_average(messages, id)
    return data


def generate_ability_data(messages: List[Message]) -> Dict[str, int] | Dict[str, float]:
    abilities = ["str", "dex", "con", "wis", "int", "cha"]
    data = {}
    for id in abilities:
        data[f"{id}_ability_count"] = count_msgs_if(messages, Message.ability_type, id)
        data[f"{id}_ability_average"] = ability_check_average(messages, id)
    return data


def generate_save_data(messages: List[Message]) -> Dict[str, int] | Dict[str, float]:
    skills = ["str", "dex", "con", "wis", "int", "cha", "death"]
    data = {}
    for id in skills:
        data[f"{id}_save_count"] = count_msgs_if(messages, Message.save_type, id)
        data[f"{id}_save_average"] = saving_throw_average(messages, id)
    return data


def generate_d20_data(messages: List[Message], user=None) -> Dict[str, float]:
    if user == "All Players":
        messages = inverse_filter_user(messages, "Gamemaster")
    elif not user is None:
        messages = get_matching_msgs(messages, lambda m: m.user, user)

    d20s = get_d20s(messages)
    d20_messages = get_matching_msgs(messages, Message.has_d20, True)

    d20_attack_messages = get_matching_msgs(messages, Message.is_attack, True)
    d20_save_messages = get_matching_msgs(messages, Message.is_saving_throw, True)
    d20_skill_messages = get_matching_msgs(messages, Message.is_skill_check, True)
    d20_ability_messages = get_matching_msgs(messages, Message.is_ability_check, True)
    d20_initiative_messages = get_matching_msgs(
        messages, Message.is_initiative_roll, True
    )

    d20_count = sum([die.number for die in d20s])
    roll_count = len(d20s)  # Number of rolls (advantage and disadvantage count as 1)
    advantage_count = count_advantage(d20s)
    disadvantage_count = count_disadvantage(d20s)
    skill_check_count = count_msgs_if(d20_messages, Message.is_skill_check, True)
    ability_check_count = count_msgs_if(d20_messages, Message.is_ability_check, True)
    saving_throw_count = count_msgs_if(d20_messages, Message.is_saving_throw, True)
    attack_roll_count = count_msgs_if(d20_messages, Message.is_attack, True)
    initiative_roll_count = count_msgs_if(
        d20_messages, Message.is_initiative_roll, True
    )
    advantage_ratio = advantage_count / roll_count
    disadvantage_ratio = disadvantage_count / roll_count

    return (
        {
            "raw_count": d20_count,
            "roll_count": roll_count,
            "advantage_count": advantage_count,
            "disadvantage_count": disadvantage_count,
            "advantage_ratio": advantage_ratio,
            "disadvantage_ratio": disadvantage_ratio,
            "skill_check_count": skill_check_count,
            "skill_check_ratio": skill_check_count / roll_count,
            "ability_check_count": ability_check_count,
            "ability_check_ratio": ability_check_count / roll_count,
            "saving_throw_count": saving_throw_count,
            "saving_throw_ratio": saving_throw_count / roll_count,
            "attack_roll_count": attack_roll_count,
            "attack_roll_ratio": attack_roll_count / roll_count,
            "initiative_roll_count": initiative_roll_count,
            "initiative_roll_ratio": 0.0
            if initiative_roll_count == 0
            else initiative_roll_count / roll_count,
            "nat_20_count": count_nat_20s(d20s),
            "nat_20_ratio": count_nat_20s(d20s) / roll_count,
            "nat_1_count": count_nat_1s(d20s),
            "nat_1_ratio": count_nat_1s(d20s) / roll_count,
            "stolen_nat_20_count": len([die for die in d20s if die.is_stolen_nat_20()]),
            "super_nat_20_count": len([die for die in d20s if die.is_super_nat_20()]),
            "disadvantage_nat_20_count": len(
                [die for die in d20s if die.is_disadvantage_nat_20()]
            ),
            "dropped_nat_1_count": len([die for die in d20s if die.is_dropped_nat_1()]),
            "super_nat_1_count": len([die for die in d20s if die.is_super_nat_1()]),
            "advantage_nat_1_count": len(
                [die for die in d20s if die.is_advantage_nat_1()]
            ),
            "average_raw_d20_roll": average_raw_d20_roll(d20s),
            "average_final_d20_roll": average_final_d20_roll(d20_messages),
            "average_d20_after_modifiers": average_d20_after_modifiers(d20_messages),
            "average_attack_before_modifiers": average_final_d20_roll(
                d20_attack_messages
            ),
            "average_initiative_before_modifiers": average_final_d20_roll(
                d20_initiative_messages
            ),
            "average_save_before_modifiers": average_final_d20_roll(d20_save_messages),
            "average_skill_before_modifiers": average_final_d20_roll(
                d20_skill_messages
            ),
            "average_ability_before_modifiers": average_final_d20_roll(
                d20_ability_messages
            ),
            "average_attack_after_modifiers": average_d20_after_modifiers(
                d20_attack_messages
            ),
            "average_initiative_after_modifiers": average_d20_after_modifiers(
                d20_initiative_messages
            ),
            "average_save_after_modifiers": average_d20_after_modifiers(
                d20_save_messages
            ),
            "average_skill_after_modifiers": average_d20_after_modifiers(
                d20_skill_messages
            ),
            "average_ability_after_modifiers": average_d20_after_modifiers(
                d20_ability_messages
            ),
        }
        | generate_save_data(d20_save_messages)
        | generate_ability_data(d20_ability_messages)
        | generate_skill_data(d20_skill_messages)
    )


class Session(object):
    def __init__(self, message: Message):
        self.min_time = message.timestamp
        self.max_time = message.timestamp
        self.count = 1

    def in_session(self, message: Message):
        return (message.timestamp - self.max_time).total_seconds() < 6*3600

    def add_message(self, message: Message):
        self.max_time = message.timestamp
        self.count += 1

def run(filename: str, world_name: str, players: List[str]):
    messages = load_zip_file(filename, world_name)
    messages = apply_april_fools_filter(messages)

    all = generate_d20_data(messages, user=None)
    all["player"] = "All"
    d20_data = [all]

    users = ["All Players", "Gamemaster"] + players
    for user in users:
        user_data = generate_d20_data(messages, user=user)
        user_data["player"] = user
        d20_data.append(user_data)

    with open(f"./public/{world_name}_data.json", "w") as f:
        json.dump(d20_data, f, indent=4)

    sessions: List[Session] = []
    for message in messages:
        added_to_session = False
        for session in sessions:
            if session.in_session(message):
                session.add_message(message)
                added_to_session = True
                break
        if not added_to_session:
            sessions.append(Session(message))


if __name__ == "__main__":
    filename = sys.argv[1]
    world_name = sys.argv[2]
    players = sys.argv[3:]
    run(filename, world_name, players)
