#! /usr/bin/env python3

import sys
from os import access, R_OK, system, getenv, get_terminal_size, name as nme
from time import sleep
import re
from argparse import ArgumentParser

def log_parsing(args):
    if nme == 'nt':
        system('mode con: lines=800')
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

    all_stats = True
    if (args.dmgs or 
        args.dmgs_crits or 
        args.dmgs_received or 
        args.heals or 
        args.heals_crits or 
        args.heals_received):
        all_stats = False

    if args.dmgs or all_stats:
        print("\nOverall damages (crits included) dealt (ordered from most to least):")
        for guy, dmgs in sorted_fighters:
            print(" "*4,guy,dmgs)

    if args.dmgs_crits or all_stats:
        print("\nOverall critical dmgs dealt (ordered from most to least):")
        for guy, dmgs in sorted_fighters_crits:
            print(" "*4,guy,dmgs)

    if args.dmgs_received or all_stats:
        print("\nOverall damages Received (ordered from most to least):")
        for guy, dmgs in sorted_takers:
            print(" "*4,guy,dmgs)

    if args.heals_received or all_stats:
        print("\nOverall heals received (ordered from most to least):")
        for guy, dmgs in sorted_healed:
            print(" "*4,guy,dmgs)

    if args.heals or all_stats:
        print("\nOverall heals (crits included) given (ordered from most to least):")
        for guy, dmgs in sorted_healers:
            print(" "*4,guy,dmgs)

    if args.heals_crits or all_stats:
        print("\nOverall critical heals given (ordered from most to least):")
        for guy, dmgs in sorted_healers_crits:
            print(" "*4,guy,dmgs)

def main():

    if (nme == 'nt'):
        user_path = getenv("USERPROFILE")
    else:
        user_path = ""

    parser = ArgumentParser(prog="overlog.exe", description="Parse combat logs from OrbusVR and, by default, displays all the stats (overall dmgs,dmgs_received, heals and criticals). You can filter the stats with options.")
    parser.add_argument("-l", "--logfile", type=str, help="The log file to parse", default=user_path+"\AppData\LocalLow\Orbus Online, LLC\OrbusVR\combat.log")
    parser.add_argument("-f", "--follow", help="Keep watching the file", action="store_true")
    parser.add_argument("-r", "--refresh", help="When watching the file, set the refresh time (by default, it refreshes every 30 sec)", type=int, default=30)
    parser.add_argument("-d", "--dmgs", help="Display the overall dmgs", action="store_true")
    parser.add_argument("-dc", "--dmgs_crits", help="Display the overall critical dmgs", action="store_true")
    parser.add_argument("-dr", "--dmgs_received", help="Display the overall dmgs received", action="store_true")
    parser.add_argument("-hr", "--heals_received", help="Display the overall heals received", action="store_true")
    parser.add_argument("-hl", "--heals", help="Display the overall heals provided", action="store_true")
    parser.add_argument("-hlc", "--heals_crits", help="Display the overall critical heals provided", action="store_true")
    parser.add_argument('--version', action='version', version='%(prog)s v0.01')
    args = parser.parse_args()

    if not access(args.logfile, R_OK):
        print("The file {} is not readable. Please enter a valid file.\n".format(args.logfile))
        return sys.exit(1)

    if args.follow:
        print("Ok, going loopy (keeps looking the file & refreshing the stats accordingly)")
        while True:
            system('cls' if nme == 'nt' else 'clear')
            log_parsing(args)
            sleep(args.refresh)
    else:
        log_parsing(args)

    if nme == 'nt':
        system('pause')

    return sys.exit(0)

if __name__ == "__main__":
    main()
