import sys
from os import listdir
from os.path import isfile, join
from prettytable import PrettyTable

from message import Message

MESSAGE_DELIMITER = "---------------------------"

def parse_files(filename):
    message_lines = []
    messages = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line == MESSAGE_DELIMITER:
                messages.append(Message(message_lines))
                message_lines.clear()
            else:
                message_lines.append(line)

    # Last message
    if len(message_lines) > 0:
        messages.append(Message(message_lines))

    return messages

dirname = sys.argv[1]
filenames = [join(dirname, f) for f in listdir(dirname) if isfile(join(dirname, f))]
filenames = list(filter(lambda x: 'fvtt' in x, filenames))

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
        for s in split:
            speakers_to_player[s] = player

d20_rolls = list(filter(lambda m: m.is_d20_roll(), unique_messages))
print(f"Total d20 Rolls: {len(d20_rolls)}")

for roll in d20_rolls:
    if roll.get_speaker() in speakers_to_player:
        player = speakers_to_player[roll.get_speaker()]
    else:
        player = 'DM'
        print(f"Warning: '{roll.get_speaker()}' was not found in the speaker assignments. Assigning to DM.")

    rolls_by_player[player].append(roll)

print()

table = PrettyTable()

table.field_names = ["Player", "Total Rolls", "Average Raw Roll", "Average Total Roll", "Natural 20s", "% Natural 20s", "Natural 1s", "% Natural 1s"]
table.float_format["Average Raw Roll"] = "2.2"
table.float_format["Average Total Roll"] = "2.2"

for (player, rolls) in rolls_by_player.items():
    num_rolls = len(rolls)
    avg_raw_roll = sum(map(lambda r: r.get_d20_value(), rolls)) / num_rolls
    avg_tot_roll = sum(map(lambda r: r.get_result(), rolls)) / num_rolls
    nat_20_count = len(list(filter(lambda r: r.get_d20_value() == 20, rolls)))
    nat_01_count = len(list(filter(lambda r: r.get_d20_value() ==  1, rolls)))
    prcnt_nat_20 = nat_20_count / num_rolls
    prcnt_nat_01 = nat_01_count / num_rolls

    table.add_row([player, num_rolls, avg_raw_roll, avg_tot_roll, nat_20_count, f"{prcnt_nat_20:2.2%}", nat_01_count, f"{prcnt_nat_01:2.2%}"])

table.reversesort = True
print(table.get_string(sortby="Average Total Roll"))
