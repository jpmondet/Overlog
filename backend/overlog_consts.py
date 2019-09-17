"""
    Module containing all constants heavily tied to Orbus.
"""
#! /usr/bin/env python3

import re

# pylint: disable=line-too-long

COMBAT_PATTERN = re.compile(
    r"(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Combat] (?P<dude_hurt>[\S\s]+) took (?P<damages>\S+) damage from (?P<damage_dealer>[\S ]+)\s+"
)
XP_PATTERN = re.compile(
    r"(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Gained (?P<pts>\S+) XP?"
)
DRAM_PATTERN = re.compile(
    r"(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Gained (?P<pts>\S+) Dram?"
)
REP_PATTERN = re.compile(
    r"(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Earned (?P<pts>\S+) Reputation?"
)
LOOT_PATTERN = re.compile(
    r"(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Item Acquired: (?P<loot>.*)"
)
ENTER_COMBAT_PATTERN_TIME = re.compile(
    r"(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Combat] You are now in combat."
)
EXIT_COMBAT_PATTERN_TIME = re.compile(
    r"(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Combat] You are no longer in combat."
)

DUNGEON1 = "Crypt"
DUNGEON2 = "Sewers"
DUNGEON3 = "Airship"
DUNGEON4 = "Broken Hall"

RAIDBOSS1 = "Clockwork Hunter"
RAIDBOSS2 = "Pot Tank"
RAIDBOSS3 = "Broken Knight"
RAIDBOSS4 = "Seamstress"
RAIDBOSS5 = "Empowered  Valusia Warrior"
