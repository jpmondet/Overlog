#! /usr/bin/env python3

import sys
from os import access, R_OK, system, name as nme
from time import sleep
import re
from argparse import ArgumentParser

def log_parsing(args):
    combat_pattern = re.compile('(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Combat] (?P<dude_hurt>[\S\s]+) took (?P<damages>\S+) damage from (?P<damage_dealer>[\S ]+)\s+')
    fighters = dict()
    fighters_criticals = dict()
    damages_taken = dict()
    heals_given = dict()
    heals_given_crits = dict()
    heals_received = dict()
    with open(args.logfile, "r") as clog:
        for line in clog:
            critical = False
            log_split = re.match(combat_pattern, line)
            if log_split:
                time = log_split.group("time")
                damages = (int)(log_split.group("damages"))
                dude_hurt = log_split.group("dude_hurt")
                damage_dealer = log_split.group("damage_dealer")
                if "(Critical)" in damage_dealer:
                    critical = True
                    damage_dealer = ''.join(damage_dealer.split()[:-1])
                if "(" in damage_dealer or "Unknown" in damage_dealer:
                    if "(" in dude_hurt:
                        # Bugged log line
                        continue

                    # The damage_dealer is a mob or a weird spell
                    # We update the damages_taken by players
                    if damages_taken.get(dude_hurt):
                        damages_taken[dude_hurt] = (int)(damages_taken[dude_hurt]) + damages
                    else:
                        damages_taken[dude_hurt] = damages
                    continue

                if damages > 0:
                    if fighters.get(damage_dealer):
                        fighters[damage_dealer] = (int)(fighters[damage_dealer]) + damages
                    else:
                        fighters[damage_dealer] = damages
                    if critical:
                        if fighters_criticals.get(damage_dealer):
                            fighters_criticals[damage_dealer] = (int)(fighters_criticals[damage_dealer]) + damages
                        else:
                            fighters_criticals[damage_dealer] = damages
                elif damages < 0:
                    damages = -damages
                    if heals_given.get(damage_dealer):
                        heals_given[damage_dealer] = (int)(heals_given[damage_dealer]) + damages
                    else:
                        heals_given[damage_dealer] = damages
                    if heals_received.get(dude_hurt):
                        heals_received[dude_hurt] = (int)(heals_received[dude_hurt]) + damages
                    else:
                        heals_received[dude_hurt] = damages
                    if critical:
                        if heals_given_crits.get(damage_dealer):
                            heals_given_crits[damage_dealer] = (int)(heals_given_crits[damage_dealer]) + damages
                        else:
                            heals_given_crits[damage_dealer] = damages


    sorted_fighters = sorted(fighters.items(), key=lambda kv: kv[1], reverse=True)
    sorted_fighters_crits = sorted(fighters_criticals.items(), key=lambda kv: kv[1], reverse=True)
    sorted_takers = sorted(damages_taken.items(), key=lambda kv: kv[1], reverse=True)
    sorted_healers = sorted(heals_given.items(), key=lambda kv: kv[1], reverse=True)
    sorted_healers_crits = sorted(heals_given_crits.items(), key=lambda kv: kv[1], reverse=True)
    sorted_healed = sorted(heals_received.items(), key=lambda kv: kv[1], reverse=True)

    print("\nOverall damages (crits included) dealt (ordered from most to least):")
    for guy, dmgs in sorted_fighters:
        print(" "*4,guy,dmgs)

    print("\nOverall critical dmgs dealt (ordered from most to least):")
    for guy, dmgs in sorted_fighters_crits:
        print(" "*4,guy,dmgs)

    print("\nOverall damages Received (ordered from most to least):")
    for guy, dmgs in sorted_takers:
        print(" "*4,guy,dmgs)

    print("\nOverall heals (crits included) given (ordered from most to least):")
    for guy, dmgs in sorted_healers:
        print(" "*4,guy,dmgs)

    print("\nOverall critical heals given (ordered from most to least):")
    for guy, dmgs in sorted_healers_crits:
        print(" "*4,guy,dmgs)

    print("\nOverall heals received (ordered from most to least):")
    for guy, dmgs in sorted_healed:
        print(" "*4,guy,dmgs)


def main():

    # TODO: Add possibility to show only some stats
    parser = ArgumentParser(description="Parse combat logs from OrbusVR.")
    parser.add_argument("logfile", type=str, help="The log file to parse", default="")
    parser.add_argument("-f", "--follow", help="Keep watching the file", action="store_true")
    parser.add_argument("-r", "--refresh", help="When watching the file, set the refresh time (by default, it refreshes every 30 sec)", type=int, default=3)
    #args_grp = parser.add_mutually_exclusive_group()
    #args_grp = 
    args = parser.parse_args()

    if not access(args.logfile, R_OK):
        print("The file {} is not readable. Please enter a valid file.\n".format(args.logfile))
        return sys.exit(1)

    if args.follow:
        print("Ok, going loopy (keeps looking the file & refreshing the stats accordingly)")
        while True:
            sleep(args.refresh)
            system('cls' if nme == 'nt' else 'clear')
            log_parsing(args)
    else:
        log_parsing(args)

    return sys.exit(0)

if __name__ == "__main__":
    main()
