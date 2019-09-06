#! /usr/bin/env python3

import sys
from os import access, R_OK, system, getenv, get_terminal_size, name as nme
from time import sleep
from datetime import timedelta
import re
from argparse import ArgumentParser
import tkinter as tk

class Gui:
    def __init__(self, master):
        self.master = master
        master.title("Overlog")

        #Menu
        self.menu = tk.Menu(master)
        self.menu.combat = tk.Menu(self.menu, tearoff=0)
        self.menu.combat.add_command(label="Damage", command= lambda :self.combat_type("Damage"))
        self.menu.combat.add_command(label="Heal", command= lambda :self.combat_type("Heal"))
        self.menu.combat.add_command(label="Tank", command= lambda :self.combat_type("Tank"))

        self.menu.settings = tk.Menu(self.menu, tearoff=0)
        self.menu.settings.add_command(label="Logfile", command=False)
        self.menu.settings.add_command(label="Follow", command=False)
        self.menu.settings.add_command(label="Refresh", command=False)
        self.menu.settings.add_command(label="Dmgs", command=False)
        self.menu.settings.add_command(label="Dmgs crits", command=False)
        self.menu.settings.add_command(label="Dmgs recieved", command=False)
        self.menu.settings.add_command(label="Heals recieved", command=False)
        self.menu.settings.add_command(label="Heals", command=False)
        self.menu.settings.add_command(label="Heals crits", command=False)
        self.menu.settings.add_command(label="Misc info", command=False)
        self.menu.settings.add_command(label="Loot", command=False)
        self.menu.settings.add_command(label="Version", command=False)

        self.menu.add_cascade(label="Combat type", menu=self.menu.combat)
        self.menu.add_cascade(label="Settings", menu=self.menu.settings)
        master.config(menu=self.menu)

        #Front
        self.mainframe = tk.Frame(master, bg="red", height=1000, width=2000)
        self.mainframe.pack()

    def combat_type(self, type):
        print(type)


def log_parsing(args):
    if nme == 'nt':
        system('mode con: lines=800')
    combat_pattern = re.compile('(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Combat] (?P<dude_hurt>[\S\s]+) took (?P<damages>\S+) damage from (?P<damage_dealer>[\S ]+)\s+')
    xp_pattern = re.compile('(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Gained (?P<pts>\S+) XP?')
    dram_pattern = re.compile('(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Gained (?P<pts>\S+) Dram?')
    rep_pattern = re.compile('(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Earned (?P<pts>\S+) Reputation?')
    loot_pattern = re.compile('(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Item Acquired: (?P<loot>.*)')
    enter_combat_pattern = re.compile('(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}):(?P<milsec>\d{3}) \[Combat] You are now in combat.')
    exit_combat_pattern = re.compile('(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}):(?P<milsec>\d{3}) \[Combat] You are no longer in combat.')
    fighters = dict()
    fighters_criticals = dict()
    damages_taken = dict()
    heals_given = dict()
    heals_given_crits = dict()
    heals_received = dict()
    tot_xp = 0
    tot_dram = 0
    tot_rep = 0
    tot_dungeons = 0
    loots = []
    tot_combat_time = timedelta()
    entered_time = timedelta()
    exited_time = timedelta()
    entered_combat = False
    exited_combat = False
    with open(args.logfile, "r") as clog:
        for line in clog:
            critical = False
            combat_log_split = re.match(combat_pattern, line)
            if combat_log_split:
                # Unpacking the log line
                time = combat_log_split.group("time")
                damages = (int)(combat_log_split.group("damages"))
                dude_hurt = combat_log_split.group("dude_hurt")
                damage_dealer = combat_log_split.group("damage_dealer")
                if "(Critical)" in damage_dealer:
                    critical = True
                    damage_dealer = ''.join(damage_dealer.split()[:-1])
                if "(" in damage_dealer or "Unknown" in damage_dealer:
                    # The damage_dealer is a mob or a weird spell

                    if "(" in dude_hurt:
                        # Bugged log line (players are not allowed to have
                        # parenthesis in their name)
                        continue

                    # We update the damages_taken by players
                    if damages_taken.get(dude_hurt):
                        total_dmgs = (int)(damages_taken[dude_hurt][0]) + damages
                        nbr_hits = damages_taken[dude_hurt][1] + 1
                        damages_taken[dude_hurt] = (total_dmgs, nbr_hits)
                    else:
                        damages_taken[dude_hurt] = (damages, 1)
                    continue

                if damages > 0:
                    if fighters.get(damage_dealer):
                        total_dmgs = (int)(fighters[damage_dealer][0]) + damages
                        nbr_hits = fighters[damage_dealer][1] + 1
                        fighters[damage_dealer] = (total_dmgs, nbr_hits)
                    else:
                        fighters[damage_dealer] = (damages, 1)
                    if critical:
                        if fighters_criticals.get(damage_dealer):
                            total_crits = (int)(fighters_criticals[damage_dealer][0]) + damages
                            nbr_crits = fighters_criticals[damage_dealer][1] + 1
                            fighters_criticals[damage_dealer] = (total_crits, nbr_crits)
                        else:
                            fighters_criticals[damage_dealer] = (damages, 1)
                elif damages < 0:
                    damages = -damages
                    if heals_given.get(damage_dealer):
                        tot_heals = (int)(heals_given[damage_dealer][0]) + damages
                        nbr_heals = heals_given[damage_dealer][1] + 1
                        heals_given[damage_dealer] = (tot_heals, nbr_heals)
                    else:
                        heals_given[damage_dealer] = (damages, 1)

                    if heals_received.get(dude_hurt):
                        tot_heals = (int)(heals_received[dude_hurt][0]) + damages
                        nbr_heals = heals_received[dude_hurt][1] + 1
                        heals_received[dude_hurt] = (tot_heals, nbr_heals)
                    else:
                        heals_received[dude_hurt] = (damages, 1)

                    if critical:
                        if heals_given_crits.get(damage_dealer):
                            tot_heals_crit = (int)(heals_given_crits[damage_dealer][0]) + damages
                            nbr_crit_heals = heals_given_crits[damage_dealer][1] + 1
                            heals_given_crits[damage_dealer] = (tot_heals_crit, nbr_crit_heals)
                        else:
                            heals_given_crits[damage_dealer] = (damages, 1)
                continue
            xp_log_split = re.match(xp_pattern, line)
            if xp_log_split:
                tot_xp = tot_xp + (int)(xp_log_split["pts"])
                continue
            dram_log_split = re.match(dram_pattern, line)
            if dram_log_split:
                tot_dram = tot_dram + (int)(dram_log_split["pts"])
                continue
            rep_log_split = re.match(rep_pattern, line)
            if rep_log_split:
                tot_rep = tot_rep + (int)(rep_log_split["pts"])
                continue
            loot_log_split = re.match(loot_pattern, line)
            if loot_log_split:
                loots.append(loot_log_split["loot"])
                continue
            entered_log_split = re.match(enter_combat_pattern, line)
            if entered_log_split:
                entered_combat = True
                hour=(int)(entered_log_split["hour"])
                minu=(int)(entered_log_split["min"])
                sec=(int)(entered_log_split["sec"])
                milsec=(int)(entered_log_split["milsec"])
                entered_time = timedelta(hours=hour, minutes=minu, seconds=sec, milliseconds=milsec)
            exited_log_split = re.match(exit_combat_pattern, line)
            if exited_log_split:
                hour=(int)(exited_log_split["hour"])
                minu=(int)(exited_log_split["min"])
                sec=(int)(exited_log_split["sec"])
                milsec=(int)(exited_log_split["milsec"])
                exited_time = timedelta(hours=hour, minutes=minu, seconds=sec, milliseconds=milsec)
                if not entered_combat:
                    print("Hmm something wrong here. Incomplete log file ? ")
                    print("I'm seeing that you left a combat you never started on time {}".format(exited_time))
                    print("Not counting it to avoid weird datas.")
                    continue
                exited_combat = True
                tot_combat_time = tot_combat_time + (exited_time - entered_time)
            if "Dungeon Completed" in line:
                tot_dungeons = tot_dungeons + 1
                continue

    sorted_fighters = sorted(fighters.items(), key=lambda kv: kv[1][0], reverse=True)
    sorted_fighters_crits = sorted(fighters_criticals.items(), key=lambda kv: kv[1][0], reverse=True)
    sorted_takers = sorted(damages_taken.items(), key=lambda kv: kv[1][0], reverse=True)
    sorted_healers = sorted(heals_given.items(), key=lambda kv: kv[1][0], reverse=True)
    sorted_healers_crits = sorted(heals_given_crits.items(), key=lambda kv: kv[1][0], reverse=True)
    sorted_healed = sorted(heals_received.items(), key=lambda kv: kv[1][0], reverse=True)

    # stats
    stats = {
        "sorted_fighters":sorted_fighters,
        "sorted_fighters_crits":sorted_fighters_crits,
        "sorted_takers":sorted_takers,
        "sorted_healers":sorted_healers,
        "sorted_healers_crits":sorted_healers_crits,
        "sorted_healed":sorted_healed,
        "loots":loots,
        "tot_xp":tot_xp,
        "tot_dram":tot_dram,
        "tot_rep":tot_rep,
        "tot_dungeons":tot_dungeons,
        "tot_combat_time":tot_combat_time
    }
    return stats


def log_print(args, stats):
    all_stats = True
    if (args.dmgs or
        args.dmgs_crits or
        args.dmgs_received or
        args.heals or
        args.heals_crits or
        args.heals_received or
        args.misc_infos or
        args.loots):
        all_stats = False

    if args.dmgs or all_stats:
        print("\nOverall damages (crits included) dealt (ordered from most to least):")
        for guy, dmgs in stats["sorted_fighters"]:
            print("    {0:15} {1:10} ({2:6} hits (or ticks from DoT))".format(guy,dmgs[0],dmgs[1]))

    if args.dmgs_crits or all_stats:
        print("\nOverall critical dmgs dealt (ordered from most to least):")
        for guy, dmgs in stats["sorted_fighters_crits"]:
            print("    {0:15} {1:10} ({2:6} crit hits (or ticks from DoT))".format(guy,dmgs[0],dmgs[1]))

    if args.dmgs_received or all_stats:
        print("\nOverall damages Received (ordered from most to least):")
        for guy, dmgs in stats["sorted_takers"]:
            print("    {0:15} {1:10} ({2:6} hits (or ticks from DoT))".format(guy,dmgs[0],dmgs[1]))

    if args.heals_received or all_stats:
        print("\nOverall heals received (ordered from most to least):")
        for guy, dmgs in stats["sorted_healed"]:
            print("    {0:15} {1:10} ({2:6} heals (or ticks from HoT))".format(guy,dmgs[0],dmgs[1]))

    if args.heals or all_stats:
        print("\nOverall heals (crits included) given (ordered from most to least):")
        for guy, dmgs in stats["sorted_healers"]:
            print("    {0:15} {1:10} ({2:6} heals (or ticks from HoT))".format(guy,dmgs[0],dmgs[1]))

    if args.heals_crits or all_stats:
        print("\nOverall critical heals given (ordered from most to least):")
        for guy, dmgs in stats["sorted_healers_crits"]:
            print("    {0:15} {1:10} ({2:6} crit heals (or ticks from HoT))".format(guy,dmgs[0],dmgs[1]))

    if args.loots:
        if stats.loots:
            print("\n\nWow, what a lucky person you are, you've acquired : ")
            for loot in stats["loots"]:
                print("    - {}".format(loot))
        else:
            print("Oh, no loots during this session :-(")

    if args.misc_infos:
        print("\n\nYou won {} XP, {} Dram and {} Reputation on this session! :-)".format(stats["tot_xp"], stats["tot_dram"], stats["tot_rep"]))
        if stats["tot_dungeons"] > 0:
            print("You even completed {} dungeons ! Amazing !".format(stats["tot_dungeons"]))
        print("And btw, you were in combat for {} hour(s)".format(stats["tot_combat_time"]))


def main():
    if (nme == 'nt'):
        user_path = getenv("USERPROFILE")
    else:
        user_path = ""

    parser = ArgumentParser(prog="overlog.exe", description="Parse combat logs from OrbusVR and, by default, displays all the stats (overall dmgs,dmgs_received, heals and criticals). You can filter the stats with options.")
    parser.add_argument("-l", "--logfile", type=str, help="The log file to parse", default=user_path+"\\AppData\\LocalLow\\Orbus Online, LLC\\OrbusVR\\combat.log")
    parser.add_argument("-f", "--follow", help="Keep watching the file", action="store_true")
    parser.add_argument("-r", "--refresh", help="When watching the file, set the refresh time (by default, it refreshes every 30 sec)", type=int, default=30)
    parser.add_argument("-d", "--dmgs", help="Display the overall dmgs", action="store_true")
    parser.add_argument("-dc", "--dmgs_crits", help="Display the overall critical dmgs", action="store_true")
    parser.add_argument("-dr", "--dmgs_received", help="Display the overall dmgs received", action="store_true")
    parser.add_argument("-hr", "--heals_received", help="Display the overall heals received", action="store_true")
    parser.add_argument("-hl", "--heals", help="Display the overall heals provided", action="store_true")
    parser.add_argument("-hlc", "--heals_crits", help="Display the overall critical heals provided", action="store_true")
    parser.add_argument("-m", "--misc_infos", help="Display some other infos we can find in the log file (like xp/gold/rep, nbr of dungeons, time in combat, maybe more?)", action="store_true")
    parser.add_argument("-lo", "--loots", help="Display all the loots acquired", action="store_true")
    parser.add_argument('--version', action='version', version='%(prog)s v0.02')
    args = parser.parse_args()

    if not access(args.logfile, R_OK):
        print("The file {} is not readable. Please enter a valid file.\n".format(args.logfile))
        return sys.exit(1)

    if args.follow:
        print("Ok, going loopy (keeps looking the file & refreshing the stats accordingly)")
        while True:
            system('cls' if nme == 'nt' else 'clear')
            log_print(args, log_parsing(args))
            sleep(args.refresh)
    else:
        log_print(args, log_parsing(args))
    if nme == 'nt':
        system('pause')

    return sys.exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    gui = Gui(root)
    root.mainloop()

    # main()
