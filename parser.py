#! /usr/bin/env python3

import sys
from os import access, R_OK, system, getenv, get_terminal_size, path, SEEK_END, name as nme
from time import sleep
from datetime import timedelta
import re
from argparse import ArgumentParser
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
from collections import namedtuple

class Gui:
    def __init__(self, master):
        self.window = {
            "name":"Overlog",
            "size":"2000x1000"
            }
        self.settings = {
            "logfile":tk.StringVar(value=user_path+"\\AppData\\LocalLow\\Orbus Online, LLC\\OrbusVR\\combat.log"),
            "refresh":tk.IntVar(value=30),
            "follow":tk.BooleanVar(),
            "dmgs":tk.BooleanVar(),
            "dmgs_crits":tk.BooleanVar(),
            "dmgs_recieved":tk.BooleanVar(),
            "heals":tk.BooleanVar(),
            "heals_crits":tk.BooleanVar(),
            "heals_recieved":tk.BooleanVar(),
            "misc_info":tk.BooleanVar(),
            "loot":tk.BooleanVar()
        }
        self.parse = Parser()



        self.master = master
        master.title(self.window["name"])
        master.geometry(self.window["size"])

        # Menu (Dynamic?)
        self.menu_parse = tk.Menu(master)
        self.menu_parse.combat = tk.Menu(self.menu_parse, tearoff=0)
        self.menu_parse.combat.add_command(label="Button", command= lambda :self.code_test("Test"))

        self.menu_parse.file = tk.Menu(self.menu_parse, tearoff=0)
        self.menu_parse.file.add_command(label="Open Logfile...", command= lambda :self.settings_logfile(filedialog.askopenfilename(initialdir = user_path+"\\AppData\\LocalLow\\Orbus Online, LLC\\OrbusVR\\", title="Select .log file", filetypes=(("Log files", "*.log"),("All files", "*.*")))))
        self.menu_parse.file.add_separator()
        self.menu_parse.file.add_checkbutton(label="Refresh", variable=self.settings["follow"], onvalue=True, offvalue=False)
        self.menu_parse.file.add_command(label="Refresh rate...", command=lambda :self.settings["refresh"].set(simpledialog.askinteger("Refresh rate", "Input refresh rate between 1 and 60 seconds (standard is 30)", minvalue=1, maxvalue=60)))

        self.menu_parse.show = tk.Menu(self.menu_parse)
        self.menu_parse.show.add_checkbutton(label="Dmgs", variable=self.settings["dmgs"], onvalue=True, offvalue=False)
        self.menu_parse.show.add_checkbutton(label="Dmgs crits", variable=self.settings["dmgs_crits"], onvalue=True, offvalue=False)
        self.menu_parse.show.add_checkbutton(label="Dmgs recieved", variable=self.settings["dmgs_recieved"], onvalue=True, offvalue=False)
        self.menu_parse.show.add_checkbutton(label="Heals", variable=self.settings["heals"], onvalue=True, offvalue=False)
        self.menu_parse.show.add_checkbutton(label="Heals crits", variable=self.settings["heals_crits"], onvalue=True, offvalue=False)
        self.menu_parse.show.add_checkbutton(label="Heals recieved", variable=self.settings["heals_recieved"], onvalue=True, offvalue=False)
        self.menu_parse.show.add_checkbutton(label="Misc info", variable=self.settings["misc_info"], onvalue=True, offvalue=False)
        self.menu_parse.show.add_checkbutton(label="Loot", variable=self.settings["loot"], onvalue=True, offvalue=False)

        self.menu_parse.add_cascade(label="Code activation", menu=self.menu_parse.combat)
        self.menu_parse.add_cascade(label="File", menu=self.menu_parse.file)
        self.menu_parse.add_cascade(label="Show", menu=self.menu_parse.show)
        master.config(menu=self.menu_parse)

        # Work space
        self.mainframe = tk.Frame(master, bg="green")
        self.mainframe.pack(expand=True, fill=tk.BOTH)

            # Fight_select Frame
        self.mainframe.fight_select = tk.Frame(self.mainframe, bg="blue")
        self.mainframe.fight_select.pack(side=tk.LEFT, fill=tk.Y)

        self.mainframe.fight_select.dungeon_menu = tk.Menubutton(self.mainframe.fight_select, text="Select dungeon run", relief=tk.RAISED, bd=2)
        self.mainframe.fight_select.dungeon_menu.pack(side=tk.TOP, fill=tk.X)

        self.mainframe.fight_select.monster_list = tk.Listbox(self.mainframe.fight_select)
        self.mainframe.fight_select.monster_list.pack(expand=True, fill=tk.BOTH)

            # Player_select Frame
        self.mainframe.player_select = tk.Frame(self.mainframe, bg="red", height=25)
        self.mainframe.player_select.pack(side=tk.TOP, fill=tk.X)

            # Stats_view Frame
        self.mainframe.stats_view = tk.Frame(self.mainframe, bg = "purple")
        self.mainframe.stats_view.pack(expand=True, fill=tk.BOTH)

        # Status bar
        self.statusbar = tk.Label(master, text="File: "+self.settings["logfile"].get(), relief=tk.SUNKEN, anchor=tk.W, bd=1)
        self.statusbar.pack(fill=tk.X)


    def code_test(self, type):
        self.parse(self.settings["logfile"].get())

    def settings_logfile(self, response):
        '''self.settings["logfile"].set(response), if response[-4:] == ".log" exists as a file'''
        if response != None and path.exists(response) and response[-4:] == ".log":
            self.settings["logfile"].set(response)
            self.statusbar["text"] = "File: "+self.settings["logfile"].get()

    def convert_dictToObj(self, args):
        '''args["key"] = tkVar to args.key = var'''
        args_named = {}
        for key in args:
            args_named[key] = args[key].get()

        args_named = namedtuple("args", args_named.keys())(*args_named.values())
        return(args_named)

class Parser:
    def __init__(self):
        self.pattern = {
            "combat_pattern" : re.compile('(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Combat] (?P<dude_hurt>[\S\s]+) took (?P<damages>\S+) damage from (?P<damage_dealer>[\S ]+)\s+'),
            "xp_pattern" : re.compile('(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Gained (?P<pts>\S+) XP?'),
            "dram_pattern" : re.compile('(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Gained (?P<pts>\S+) Dram?'),
            "rep_pattern" : re.compile('(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Earned (?P<pts>\S+) Reputation?'),
            "loot_pattern" : re.compile('(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Item Acquired: (?P<loot>.*)'),
            "enter_combat_pattern" : re.compile('(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}):(?P<milsec>\d{3}) \[Combat] You are now in combat.'),
            "exit_combat_pattern" : re.compile('(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}):(?P<milsec>\d{3}) \[Combat] You are no longer in combat')
        }
        self.pattern_master = re.compile("(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[(?P<type>Loot|Combat|System)]( Gained (?P<xp>\S+) XP?| Item Acquired: (?P<loot>.*)| Gained (?P<dram>\S+) Dram?| Earned (?P<reputation>\S+) Reputation?| (?P<dude_hurt>.+) took (?P<damages>\S+) damage from (?P<damage_dealer>[\S]+)(?:(?=.) (?P<crit>\(Critical\))|))")
    def __call__(self, logfile):
        for line in self.readlines_reverse(logfile):
            re_line = re.match(self.pattern_master, line)
            if re_line:
                if re_line.group("type") == "Loot":
                    self.loot(re_line)
                elif re_line.group("type") == "Combat":
                    self.combat(re_line)
                elif re_line.group("type") == "System":
                    self.system(re_line)
                else:
                    print("Error group does not exist: " + re_line.group("type"))
                    system("pause")

    def loot(self, line):
        '''Does something if [Loot]'''
        print(line.group("time") + " - Looting")

    def combat(self, line):
        '''Does something if [Combat]'''
        print(line.group("time") + " - Fighting")

    def system(self, line):
        '''Does something if [System]'''
        print(line.group("time") + " - System Notice")


    def readlines_reverse(self, filename):
        '''Reverse read file (note; not self written)'''
        with open(filename) as qfile:
            qfile.seek(0, SEEK_END)
            position = qfile.tell()
            line = ''
            while position >= 0:
                qfile.seek(position)
                next_char = qfile.read(1)
                if next_char == "\n":
                    yield line[::-1]
                    line = ''
                else:
                    line += next_char
                position -= 1
            yield line[::-1]


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
    if (nme == 'nt'):
        user_path = getenv("USERPROFILE")
    else:
        user_path = ""

    root = tk.Tk()
    gui = Gui(root)
    root.mainloop()
    # main()
