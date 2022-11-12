import sys
from os import listdir
from os.path import isfile, join
from prettytable import PrettyTable

from message import Message

MESSAGE_DELIMITER = "---------------------------"

def parse_files(filename):
    message_lines = []
    messages = []

    in_april = False

    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line == MESSAGE_DELIMITER:
                m = Message(message_lines)
                
                if "April" in m.get_message_text():
                    in_april = not in_april
                if in_april:
                    message_lines.clear()
                    continue

                messages.append(m)
                message_lines.clear()
            else:
                message_lines.append(line)

    # Last message
    if len(message_lines) > 0:
        messages.append(Message(message_lines))

    return messages

dirname = sys.argv[1]
filenames = [join(dirname, f) for f in listdir(dirname) if isfile(join(dirname, f))]
filenames = list(filter(lambda x: 'fvtt' in x.split("/")[-1], filenames))

messages = []
for filename in filenames:
    messages += parse_files(filename)

unique_messages = list(set(messages))

speaker_assignments_filename = join(dirname, 'speaker_assignments.csv')
rolls_by_player = {}
speakers_to_player = {}
with open(speaker_assignments_filename) as f:
    for line in f:
        split = line.strip().split(',')
        player = split[0]
        
        rolls_by_player[player] = []
        first_escaped = None
        for s in split:
            if s.startswith('"'):
                first_escaped = s[1:]
                continue
            if s.endswith('"'):
                speakers_to_player[first_escaped + ',' + s[:-1]] = player
                continue
            speakers_to_player[s] = player

d20_rolls = list(filter(lambda m: m.is_d20_roll(), unique_messages))
print(f"Total d20 Rolls: {len(d20_rolls)}")

rolls_by_player['All'] = []

missing = set()
for roll in d20_rolls:
    if roll.get_speaker() in speakers_to_player:
        player = speakers_to_player[roll.get_speaker()]
    else:
        player = 'DM'
        missing.add(roll.get_speaker())
        print(f"Warning: '{roll.get_speaker()}' was not found in the speaker assignments. Assigning to DM.")

    rolls_by_player[player].append(roll)
    rolls_by_player['All'].append(roll)

print()

table = PrettyTable()

table.field_names = ["Player", "# Rolls", "Avg Raw Roll", "Avg w/ Mod", "Nat 20s", "% Nat 20s", "Nat 1s", "% Nat 1s", "# Adv", "Adv %", "# Dis", "Dis %", "# Save (# Death)", "Save %", "# Atk", "Atk %", "# Ability", "Ability %", "# Skill", "Skill %"]
table.float_format["Average Raw Roll"] = "2.2"
table.float_format["Average Total Roll"] = "2.2"

for (player, rolls) in rolls_by_player.items():
    num_rolls = len(rolls)
    avg_raw_roll = sum(map(lambda r: r.get_d20_value(), rolls)) / num_rolls
    avg_tot_roll = sum(map(lambda r: r.get_result(), rolls)) / num_rolls
    nat_20_count = len(list(filter(lambda r: r.get_d20_value() == 20, rolls)))
    nat_01_count = len(list(filter(lambda r: r.get_d20_value() ==  1, rolls)))
    percent_nat_20 = nat_20_count / num_rolls
    percent_nat_01 = nat_01_count / num_rolls
    advantage_count = sum(map(lambda r: 1 if r.is_advantage() else 0, rolls))
    percent_advantage = advantage_count / num_rolls
    disadvantage_count = sum(map(lambda r: 1 if r.is_disadvantage() else 0, rolls))
    percent_disadvantage = disadvantage_count / num_rolls
    saving_throw_count = sum(map(lambda r: 1 if r.is_saving_throw() else 0, rolls))
    death_save_count = sum(map(lambda r: 1 if r.is_death_save() else 0, rolls))
    percent_saving_throw = saving_throw_count / num_rolls
    attack_roll_count = sum(map(lambda r: 1 if r.is_attack_roll() else 0, rolls))
    percent_attack_roll = attack_roll_count / num_rolls
    skill_check_count = sum(map(lambda r: 1 if r.is_skill_check() else 0, rolls))
    percent_skill_check = skill_check_count / num_rolls
    ability_check_count = sum(map(lambda r: 1 if r.is_ability_check() else 0, rolls))
    percent_ability_check = ability_check_count / num_rolls


    table.add_row([player, num_rolls, f"{avg_raw_roll:.2f}", f"{avg_tot_roll:.2f}", nat_20_count, f"{percent_nat_20:2.2%}", nat_01_count, f"{percent_nat_01:2.2%}", advantage_count, f"{percent_advantage:2.2%}", disadvantage_count, f"{percent_disadvantage:2.2%}", f"{saving_throw_count} ({death_save_count})", f"{percent_saving_throw:2.2%}", attack_roll_count, f"{percent_attack_roll:2.2%}", skill_check_count, f"{percent_skill_check:2.2%}", ability_check_count, f"{percent_ability_check:2.2%}"])

table.reversesort = True
print(table.get_string(sortby="# Rolls"))

if len(missing) > 0:
    print()
    print('Missing: ' + ','.join(missing))
