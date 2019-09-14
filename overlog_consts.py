"""
    Module containing all constants heavily tied to Orbus.
"""
#! /usr/bin/env python3

import re

# pylint: disable=line-too-long

COMBAT_PATTERN = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Combat] (?P<dude_hurt>[\S\s]+) took (?P<damages>\S+) damage from (?P<damage_dealer>[\S ]+)\s+"
)
XP_PATTERN = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Gained (?P<pts>\S+) XP?"
)
DRAM_PATTERN = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Gained (?P<pts>\S+) Dram?"
)
REP_PATTERN = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Earned (?P<pts>\S+) Reputation?"
)
LOOT_PATTERN = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Item Acquired: (?P<loot>.*)"
)
ENTER_COMBAT_PATTERN = re.compile(
    "(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}):(?P<milsec>\d{3}) \[Combat] You are now in combat."
)
EXIT_COMBAT_PATTERN = re.compile(
    "(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}):(?P<milsec>\d{3}) \[Combat] You are no longer in combat."
)
ENTER_COMBAT_PATTERN_TIME = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Combat] You are now in combat."
)
EXIT_COMBAT_PATTERN_TIME = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Combat] You are no longer in combat."
)
