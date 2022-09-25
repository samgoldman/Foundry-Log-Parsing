import re

from time import strptime

RE_TIMESTAMP_LINE = re.compile(r"\[(\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}:\d{2} [AP]M)\](.*)")

def parse_timestamp(timestamp):
    return strptime(timestamp, "%m/%d/%Y, %I:%M:%S %p")

def parse_timestamp_line(line):
    ''' Returns (timestamp, speaker)'''

    match = RE_TIMESTAMP_LINE.match(line)
    
    if match is None:
        return None

    return (parse_timestamp(match.group(1)), match.group(2).strip())

def parse_roll(lines):
    if len(lines) < 2:
        return None

    # Expect first line to be a number
    match = re.match(r"^\d+$", lines[0])

    if match is None:
        return None

    possible_result = int(lines[0])

    formula_match = None
    for line in lines[1:]:
        formula_match = re.match(r"(.+) = (.+) = (\d+)", line)
        if not formula_match is None:
            break

    if formula_match is None:
        return None

    if int(formula_match.group(3)) != possible_result:
        print(f"Huh, formula result doesn't match 2nd line result: ({formula_match.group(3)}, {possible_result})")
        return None # Don't know what this is

    part_1_split = formula_match.group(1).split(" ")
    part_2_split = formula_match.group(2).split(" ")

    assert(len(part_1_split) == len(part_2_split))

    dice_rolled = []
    dice_values = []

    for (formula, result) in zip(part_1_split, part_2_split):
        if 'd' in formula:
            dice_rolled.append(formula)
            dice_values.append(int(result))

    return (possible_result, dice_rolled, dice_values)

class Message:
    def __init__(self, lines):
        if len(lines) == 0:
            raise Exception("No lines provided for message")

        self.raw = " ".join(lines)

        res = parse_timestamp_line(lines.pop(0))
        if res is None:
            raise Exception(f"First line of message does not match expected format: {self.raw}")
        
        (timestamp, speaker) = res
        self.timestamp = timestamp
        self.speaker = speaker

        roll_parsed = parse_roll(lines)
        if roll_parsed is None:
            self.is_roll = False
            self.roll_result = None
            self.dice_rolled = None
            self.dice_values = None
        else:
            self.is_roll = True
            (self.roll_result, self.dice_rolled, self.dice_values) = roll_parsed

    def is_d20_roll(self):
        return self.is_roll \
            and len(self.dice_rolled) == 1 \
            and (self.dice_rolled[0] == '1d20' \
                 or self.dice_rolled[0] == '2d20kl' \
                 or self.dice_rolled[0] == '2d20kh')

    def is_advantage(self):
        return self.is_roll \
            and len(self.dice_rolled) == 1 \
            and self.dice_rolled[0] == '2d20kh'

    def is_disadvantage(self):
        return self.is_roll \
            and len(self.dice_rolled) == 1 \
            and self.dice_rolled[0] == '2d20kl'

    def get_d20_value(self):
        if self.is_d20_roll():
            return self.dice_values[0]
        else:
            return 0

    def get_message_text(self):
        return self.raw

    def is_saving_throw(self):
        return "Saving Throw" in self.raw

    def is_death_save(self):
        return "Death Saving Throw" in self.raw

    def is_attack_roll(self):
        return "Attack Roll" in self.raw

    def is_skill_check(self):
        return "Skill Check" in self.raw

    def is_ability_check(self):
        return "Ability Check" in self.raw

    def get_speaker(self):
        return self.speaker
    
    def get_dice_rolled(self):
        return self.dice_rolled

    def get_dice_results(self):
        return self.dice_values

    def get_result(self):
        return self.roll_result

    def get_timestamp(self):
        return self.timestamp

    def __key(self):
        return self.raw

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Message):
            return self.__key() == other.__key()
        return NotImplemented
