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

BOSS1_DUNGEON1 = "Dungeon Troll"
BOSS2_DUNGEON1 = "Lich King"
BOSS1_DUNGEON2 = "Mutated Rat"
BOSS2_DUNGEON2 = "Sewer Slime"
BOSS1_DUNGEON3 = "Chaos Purity"
BOSS2_DUNGEON3 = "Chaos Hunter"
BOSS1_DUNGEON4 = "Minotaur"
BOSS2_DUNGEON4 = "Gorgon"

DUNGEON_BOSSES_DICT = {
    DUNGEON1: [BOSS1_DUNGEON1, BOSS2_DUNGEON1],
    DUNGEON2: [BOSS1_DUNGEON2, BOSS2_DUNGEON2],
    DUNGEON3: [BOSS1_DUNGEON3, BOSS2_DUNGEON3],
    DUNGEON4: [BOSS1_DUNGEON4, BOSS2_DUNGEON4],
}

BOSSES_DUNGEON_DICT = {
    BOSS1_DUNGEON1: DUNGEON1,
    BOSS1_DUNGEON2: DUNGEON2,
    BOSS1_DUNGEON3: DUNGEON3,
    BOSS1_DUNGEON4: DUNGEON4,
    BOSS2_DUNGEON1: DUNGEON1,
    BOSS2_DUNGEON2: DUNGEON2,
    BOSS2_DUNGEON3: DUNGEON3,
    BOSS2_DUNGEON4: DUNGEON4,
}

DUNGEON_BOSSES_TUPLE = (
    BOSS1_DUNGEON1,
    BOSS2_DUNGEON1,
    BOSS1_DUNGEON2,
    BOSS2_DUNGEON2,
    BOSS1_DUNGEON3,
    BOSS2_DUNGEON3,
    BOSS1_DUNGEON4,
    BOSS2_DUNGEON4,
)

RAIDBOSS1 = "Clockwork Hunter"
RAIDBOSS2 = "Pot Tank"
RAIDBOSS3 = "Broken Knight"
RAIDBOSS4 = "Seamstress"
RAIDBOSS5 = "Empowered  Valusia Warrior"
