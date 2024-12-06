import json
import sys
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Mapping, Union
import plyvel

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

        assert(self.number == (len(self.active_results) + len(self.inactive_results)))

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
                    if "itemId" in dnd_flags["roll"]:
                        self.attack_item = dnd_flags["roll"]["itemId"]
                    elif "item" in dnd_flags["roll"]:
                        self.attack_item = dnd_flags["roll"]["item"]
                    else:
                        self.attack_item = dnd_flags["item"]["id"]
                elif type == "damage":
                    self.damage = True
                    if "itemId" in dnd_flags["roll"]:
                        self.damage_item = dnd_flags["roll"]["itemId"]
                    elif "item" in dnd_flags["roll"]:
                        self.damage_item = dnd_flags["roll"]["item"]
                    elif "item" in dnd_flags:
                        self.damage_item = dnd_flags["item"]["id"]
                elif type == "death":
                    self.saving_throw = "death"
                    self.deathSave = True
                elif type == "hitDie":
                    self.hitDie = True
                elif type == "save":
                    if "abilityId" in dnd_flags["roll"]:
                        self.saving_throw = dnd_flags["roll"]["abilityId"]
                    else:
                        self.saving_throw = dnd_flags["roll"]["ability"]
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

    def save_type(self) -> str | None:
        return self.saving_throw

    def is_skill_check(self) -> bool:
        return not self.skill_check is None

    def skill_type(self) -> str | None:
        return self.skill_check

    def is_ability_check(self) -> bool:
        return not self.ability_check is None

    def is_initiative_roll(self) -> bool:
        return self.initiative

    def ability_type(self) -> str | None:
        return self.ability_check

    def is_attack(self) -> bool:
        return self.attack

    def is_damage(self) -> bool:
        return self.damage

    def is_hit_die(self) -> bool:
        return self.hitDie

    def __str__(self):
        return f"{self.timestamp} {self.user} {self.content} {self.rolls}"


def load_zip_files(world_name: str) -> List[Message]:
    # import zipfile

    user_map = {None: "UNKNOWN USER"}
    ids = set()
    raw_data = []

    users_db = plyvel.DB(f"./{world_name}/data/users", create_if_missing=False)
    for key, value in users_db:
        user_map[key.decode().split('!')[-1]] = json.loads(value.decode())["name"]

    msgs_db = plyvel.DB(f"./{world_name}/data/messages", create_if_missing=False)
    for key, value in msgs_db:
        raw_data.append(value.decode())
    data = []
    for raw in raw_data:
        if "$$deleted" in raw and raw["$$deleted"]:
            continue
        raw = json.loads(raw)
        roll_data = []
        if "roll" in raw:
            roll_data.append(raw["roll"])
        if "rolls" in raw:
            roll_data = raw["rolls"]

        alias = raw["speaker"]["alias"] if "alias" in raw["speaker"] else None

        for i in range(len(roll_data)):
            if type(roll_data[i]) == str:
                roll_data[i] = json.loads(roll_data[i])
        if "author" not in raw:
            continue
        data.append(
            {
                "user": user_map[raw["author"]],
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


def flatten(l: List[List[Any]]) -> List[Any]:
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
    dice_nested = [m.get_dice() for m in messages]
    dice = flatten(dice_nested)
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


def get_matching_msgs(messages: List[Message], function, expected) -> List[Message]:
    return [message for message in messages if function(message) == expected]


def inverse_filter_user(messages: List[Message], user: str) -> List[Message]:
    return list(filter(lambda message: message.user != user, messages))


def average_raw_roll(dice: List[Die]) -> float:
    all_active = flatten([die.active_results for die in dice])
    all_inactive = flatten([
        die.inactive_results for die in dice
    ])
    all = all_active + all_inactive
    total_value = sum(all)
    count = len(all)
    if count == 0:
        return 0
    return total_value / count


def average_final_d20_roll(messages: List[Message]) -> float:
    dice = get_d20s(messages)
    all_active = [die.active_results[0] for die in dice]
    total_value = sum(all_active)
    count = len(all_active)
    if count == 0:
        return 0
    return total_value / count


def average_d20_after_modifiers(messages: List[Message]) -> float:
    total_value = sum(
        flatten([[roll.total for roll in message.rolls] for message in messages])
    )
    count = len(messages)
    if count == 0:
        return 0
    return total_value / count


def saving_throw_average(messages: List[Message], save_type: str) -> float:
    count = count_msgs_if(messages, Message.save_type, save_type)
    if count == 0:
        return 0.0
    return average_d20_after_modifiers(
        [message for message in messages if message.save_type() == save_type]
    )


def ability_check_average(messages: List[Message], ability_type: str) -> float:
    count = count_msgs_if(messages, Message.ability_type, ability_type)
    if count == 0:
        return 0.0
    return average_d20_after_modifiers(
        [message for message in messages if message.ability_type() == ability_type]
    )


def skill_check_average(messages: List[Message], skill_type: str) -> float:
    count = count_msgs_if(messages, Message.skill_type, skill_type)
    if count == 0:
        return 0.0
    return average_d20_after_modifiers(
        [message for message in messages if message.skill_type() == skill_type]
    )


def generate_skill_data(messages: List[Message]) -> Mapping[str, Union[float, str, int]]:
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
        data[f"{id}_skill_average"] = skill_check_average(messages, id)
        data[f"{id}_skill_count"] = count_msgs_if(messages, Message.skill_type, id)
    return data


def generate_ability_data(messages: List[Message]) -> Mapping[str, Union[float, str]]:
    abilities = ["str", "dex", "con", "wis", "int", "cha"]
    data = {}
    for id in abilities:
        data[f"{id}_ability_average"] = ability_check_average(messages, id)
        data[f"{id}_ability_count"] = count_msgs_if(messages, Message.ability_type, id)
    return data


def generate_save_data(messages: List[Message]) -> Mapping[str, Union[float, str]]:
    skills = ["str", "dex", "con", "wis", "int", "cha", "death"]
    data = {}
    for id in skills:
        data[f"{id}_save_average"] = saving_throw_average(messages, id)
        data[f"{id}_save_count"] = count_msgs_if(messages, Message.save_type, id)
    return data


def get_dx_raw_count(messages: List[Message], x: int) -> int:
    dice = get_all_dice(messages)
    dxs = [die for die in dice if die.is_dx(x)]
    all_active = flatten([die.active_results for die in dxs])
    all_inactive = flatten([
        die.inactive_results for die in dxs
    ])
    all = all_active + all_inactive
    count = len(all)

    return count


def generate_raw_die_stats(messages: List[Message]) -> Mapping[str, Union[float, str]]:
    dice = [347, 100, 20, 12, 10, 8, 6, 4]

    data = {}
    for x in dice:
        count = get_dx_raw_count(messages, x)
        data[f"d{x}_raw_count"] = count
        all_dice = get_all_dice(messages)
        dxs = [die for die in all_dice if die.is_dx(x)]
        data[f"d{x}_raw_average"] = average_raw_roll(dxs)
    return data


def generate_data(messages: List[Message], user=None) -> Dict[str, Union[float, str]]:
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
    roll_count = len(d20_messages)  # Number of rolls (advantage and disadvantage count as 1)
    advantage_count = count_advantage(d20s)
    disadvantage_count = count_disadvantage(d20s)
    skill_check_count = len(d20_skill_messages)
    ability_check_count = len(d20_ability_messages)
    saving_throw_count = len(d20_save_messages)
    attack_roll_count = len(d20_attack_messages)
    initiative_roll_count = len(d20_initiative_messages)
    advantage_ratio = 0 if roll_count == 0 else advantage_count / roll_count
    disadvantage_ratio = 0 if roll_count == 0 else disadvantage_count / roll_count

    return (
        {
            "d20_roll_count": roll_count,
            "advantage_count": advantage_count,
            "disadvantage_count": disadvantage_count,
            "advantage_ratio": advantage_ratio,
            "disadvantage_ratio": disadvantage_ratio,
            "skill_check_count": skill_check_count,
            "skill_check_ratio": 0
            if roll_count == 0
            else skill_check_count / roll_count,
            "ability_check_count": ability_check_count,
            "ability_check_ratio": 0
            if roll_count == 0
            else ability_check_count / roll_count,
            "saving_throw_count": saving_throw_count,
            "saving_throw_ratio": 0
            if roll_count == 0
            else saving_throw_count / roll_count,
            "attack_roll_count": attack_roll_count,
            "attack_roll_ratio": 0
            if roll_count == 0
            else attack_roll_count / roll_count,
            "initiative_roll_count": initiative_roll_count,
            "initiative_roll_ratio": 0.0
            if initiative_roll_count == 0
            else initiative_roll_count / roll_count,
            "nat_20_count": count_nat_20s(d20s),
            "nat_20_ratio": 0 if roll_count == 0 else count_nat_20s(d20s) / roll_count,
            "nat_1_count": count_nat_1s(d20s),
            "nat_1_ratio": 0 if roll_count == 0 else count_nat_1s(d20s) / roll_count,
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
            "average_raw_d20_roll": average_raw_roll(d20s),
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
        | generate_raw_die_stats(messages)
    )


class Session(object):
    def __init__(self, message: Message):
        self.messages = [message]
        self.min_time = message.timestamp
        self.max_time = message.timestamp
        self.count = 1

    def in_session(self, message: Message):
        return (message.timestamp - self.max_time).total_seconds() < 24 * 3600

    def add_message(self, message: Message):
        self.messages.append(message)
        self.max_time = message.timestamp
        self.count += 1


def run(world_name: str, players: List[str]):
    messages = load_zip_files(world_name)
    messages = apply_april_fools_filter(messages)

    all = generate_data(messages, user=None)
    all["player"] = "All"
    d20_data = [all]

    users = ["All Players", "Gamemaster"] + players
    for user in users:
        user_data = generate_data(messages, user=user)
        user_data["player"] = user
        d20_data.append(user_data)

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

    sessions = [s for s in sessions if s.count > 10]

    prev_session_messages = sessions[-1].messages
    all = generate_data(prev_session_messages, user=None)
    all["player"] = "All"
    d20_data_prev_session = [all]

    users = ["All Players", "Gamemaster"] + players
    for user in users:
        user_data = generate_data(prev_session_messages, user=user)
        user_data["player"] = user
        d20_data_prev_session.append(user_data)

    for i in range(len(d20_data)):
        for (key, value) in d20_data_prev_session[i].items():
            if "count" in key:
                d20_data[i][f"{key}_prev"] = value


    with open(f"./public/{world_name}_data.json", "w") as f:
        print(f"./public/{world_name}_data.json")
        json.dump(d20_data, f, indent=4)

    field_metadata = {
        "d20_raw_count": {
            "pretty": "D20s Rolled",
            "explanation": "Raw number of d20s rolled, including those dropped"
        },
        "d20_roll_count": {
            "pretty": "D20 Rolls",
            "explanation": "The number of rolls that include a d20"
        },
        "d20_raw_average": {
            "pretty": "Average Raw D20",
            "explanation": "Average value of d20s rolled, including those dropped"
        },
        "d100_raw_count": {
            "pretty": "D100s Rolled",
        },
        "d12_raw_count": {
            "pretty": "D12s Rolled",
        },
        "d10_raw_count": {
            "pretty": "D10s Rolled",
        },
        "d10_raw_average": {
            "pretty": "Average Raw D10",
            "explanation": "Average value of d10s rolled, including those dropped"
        },
        "d8_raw_count": {
            "pretty": "D8s Rolled",
        },
        "d8_raw_average": {
            "pretty": "Average Raw D8",
            "explanation": "Average value of d8s rolled, including those dropped"
        },
        "d6_raw_count": {
            "pretty": "D6s Rolled",
        },
        "d6_raw_average": {
            "pretty": "Average Raw D6",
            "explanation": "Average value of d6s rolled, including those dropped"
        },
        "d4_raw_count": {
            "pretty": "D4s Rolled",
        },
        "d4_raw_average": {
            "pretty": "Average Raw D4",
            "explanation": "Average value of d4s rolled, including those dropped"
        },
        "d347_raw_count": {
            "pretty": "D347s Rolled",
        },
        "attack_roll_ratio": {
            "pretty": "% Attacks",
            "is_percent": True,
        },
        "saving_throw_ratio": {
            "pretty": "% Saves",
            "is_percent": True,
        },
        "ability_check_ratio": {
            "pretty": "% Ability Checks",
            "is_percent": True,
        },
        "skill_check_ratio": {
            "pretty": "% Skill Checks",
            "is_percent": True,
        },
        "initiative_roll_ratio": {
            "pretty": "% Init Rolls",
            "is_percent": True,
        },
        "attack_roll_count": {
            "pretty": "# Attacks",
        },
        "saving_throw_count": {
            "pretty": "# Saves",
        },
        "ability_check_count": {
            "pretty": "# Ability Checks",
        },
        "skill_check_count": {
            "pretty": "# Skill Checks",
        },
        "initiative_roll_count": {
            "pretty": "# Init Rolls",
        },
        "nat_20_count": {
            "pretty": "# Nat 20s",
            "explanation": "After advantage or disadvantage, was the number on the die a 20?"
        },
        "nat_20_ratio": {
            "pretty": "% Nat 20s",
            "explanation": "After advantage or disadvantage, was the number on the die a 20?",
            "is_percent": True,
        },
        "stolen_nat_20_count": {
            "pretty": "Stolen Nat 20s",
            "explanation": "Number of times that a natural 20 was lost to disadvantage",
        },
        "super_nat_20_count": {
            "pretty": "Super Nat 20s",
            "explanation": "Number of times that with advantage, both dice were 20s",
        },
        "disadvantage_nat_20_count": {
            "pretty": "Disadvantage Nat 20s",
            "explanation": "Number of times that with even with disadvantage, the result was a 20",
        },
        "nat_1_count": {
            "pretty": "# Nat 1s",
            "explanation": "After advantage or disadvantage, was the number on the die a 1?"
        },
        "nat_1_ratio": {
            "pretty": "% Nat 1s",
            "explanation": "After advantage or disadvantage, was the number on the die a 1?",
            "is_percent": True,
        },
        "dropped_nat_1_count": {
            "pretty": "Dropped Nat 1s",
            "explanation": "Number of times that a natural 1 was avoided because of advantage",
        },
        "super_nat_1_count": {
            "pretty": "Super Nat 1s",
            "explanation": "Number of times that with disadvantage, both dice were 1s",
        },
        "advantage_nat_1_count": {
            "pretty": "Advantage Nat 1s",
            "explanation": "Number of times that with even with advantage, the result was a 1 (oof)",
        },
    }

    v2_structure = {
        "world": world_name,
        "players": players,
        "field_metadata": field_metadata,
    }
    for i in d20_data:
        v2_structure[i["player"]] = i

    with open(f"./public/{world_name}_data_v2.json", "w") as f:
        print(f"./public/{world_name}_data_v2.json")
        json.dump(v2_structure, f, indent=4)


if __name__ == "__main__":
    world_name = sys.argv[1]
    players = sys.argv[2:]
    run(world_name, players)
