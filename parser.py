#! /usr/bin/env python3

import re
from pprint import pprint

def main():

    # m = re.search(r'(?P<time>\d{2}:\d{2})<(?P<user>[@+]?[^>]*)>(?P<message>.*)', s)
    combat_pattern = re.compile('(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Combat] (?P<dude_hurt>[\S\s]+) took (?P<damages>\S+) damage from (?P<damage_dealer>[\S ]+)\s+')
    fighters = dict()
    #damages_taken = dict()
    with open("logs/combat-raid1.log", "r") as clog:
        for line in clog:
            log_split = re.match(combat_pattern, line)
            if log_split:
                if "Unknown" in log_split.group("damage_dealer"):
                    continue
                time = log_split.group("time")
                dude_hurt = log_split.group("dude_hurt")
                damage_dealer = log_split.group("damage_dealer")
                if "(Critical)" in damage_dealer:
                    damage_dealer = damage_dealer[:-11]
                if "(" in damage_dealer:
                    continue
                damages = (int)(log_split.group("damages"))

                if damages > 0:
                    #print(damage_dealer,damages,dude_hurt)
                    #print(log_split.groups())
                    if fighters.get(damage_dealer):
                        fighters[damage_dealer] = (int)(fighters[damage_dealer]) + damages
                    else:
                        fighters[damage_dealer] = damages

                    #if damages_taken.get(dude_hurt):
                    #    damages_taken[dude_hurt] = (int)(damages_taken[dude_hurt]) + damages
                    #else:
                    #    damages_taken[dude_hurt] = damages

            #words = line.split()
            #log_type = words[1]
            #if log_type == "[Combat]" and len(words) >= 8 :
            #    try:
            #        time = words[0]
            #        dude_hurt = words[2]
            #        damage_dealer = words[7]
            #        damages = (int)(words[4])
            #        critical = words[-1] if len(words) > 9 else ""
            #    except IndexError:
            #        pass
            #        #print("WEIRD LINE : ")
            #        #print(line)
            #    except ValueError:
            #        pass
            #        #print("WEIRD LINE : ")
            #        #print(line)
            #    if damages > 0:
            #        if fighters.get(damage_dealer):
            #            fighters[damage_dealer] = (int)(fighters[damage_dealer]) + damages
            #        else:
            #            fighters[damage_dealer] = damages

            #        if damages_taken.get(dude_hurt):
            #            damages_taken[dude_hurt] = (int)(damages_taken[dude_hurt]) + damages
            #        else:
            #            damages_taken[dude_hurt] = damages



    sorted_fighters = sorted(fighters.items(), key=lambda kv: kv[1])
    #print(fighters)
    pprint(sorted_fighters)
    #print(damages_taken)

if __name__ == "__main__":
    main()
