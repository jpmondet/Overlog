# Overlog

OrbusVR combat log parser

## Usage: 

### Windows users (without `python`)

Download `overlog.exe` and put it where you want.

For those examples, let's assume you put it on your Desktop.


#### Quick view of the stats collected from the CURRENT combat.log

By default, overlog will go and parse the `combat.log` located in the official Orbus directory.

Thus, just **double-click** on `overlog.exe`.


#### Slighly advanced usage

##### Preliminaries

`overlog` comes with some options that you can choose to use, or not.

For that, you will need to use the command-line by launching `cmd.exe` (Start menu -> Run... -> write cmd.exe -> Enter).

`cmd.exe` will launch a black window where you can use commands.

At this point, you can drag-and-drop `overlog.exe` in the window which will automatically write the path to overlog.exe no matter where you chose to put it.

After that path written automatically, you can add `-h` to have a look to the options : 

`C:\Whatever-path-you-have\overlog.exe -h`

```
usage: overlog.exe [-h] [-l LOGFILE] [-f] [-r REFRESH] [-d] [-dc] [-dr] [-hr]
                   [-hl] [-hlc] [-m] [-lo] [--version]

Parse combat logs from OrbusVR and, by default, displays all the stats
(overall dmgs,dmgs_received, heals and criticals). You can filter the stats
with options.

optional arguments:
  -h, --help            show this help message and exit
  -l LOGFILE, --logfile LOGFILE
                        The log file to parse
  -f, --follow          Keep watching the file
  -r REFRESH, --refresh REFRESH
                        When watching the file, set the refresh time (by
                        default, it refreshes every 30 sec)
  -d, --dmgs            Display the overall dmgs
  -dc, --dmgs_crits     Display the overall critical dmgs
  -dr, --dmgs_received  Display the overall dmgs received
  -hr, --heals_received
                        Display the overall heals received
  -hl, --heals          Display the overall heals provided
  -hlc, --heals_crits   Display the overall critical heals provided
  -m, --misc_infos      Display some other infos we can find in the log file
                        (like xp/gold/rep, nbr of dungeons, time in combat,
                        maybe more?)
  -lo, --loots          Display all the loots acquired
  --version             show program's version number and exit
```

##### Display the stats of another combat.log file

**/!\ Preliminaries must have been done**

If you have some other logfiles that you would like to parse, you can use the flag `-l`.

For example : 

`C:\Whatever-path-you-have\overlog.exe -l "the\path\to\my\other\file\crypt_10_with_20_min_left.log"`

##### Display the stats continuously

**/!\ Preliminaries must have been done**

If you want to have a near "real time" view of the stats while doing some combats/dungeons/whatever, you can leverage the `-f` flag.

`C:\Whatever-path-you-have\overlog.exe -f`


By default, the stats will be refreshed every 30 sec.

However, you can use the `-r` flag to speed (or slow) this up.

`C:\Whatever-path-you-have\overlog.exe -f -r 3` will refresh every 3 secondes.

/i\ Note that those options make sense only if the logfile have new things written into (so most certainly the default combat.log except you are doing cool things ;-) ).  
If you peer those options with `-l` to a static logfile in a custom emplacement, the stats will be refreshed but there will be nothing new ;-)  

##### Display only specific stats

**/!\ Preliminaries must have been done**

By default, `overlog` will show all the stats it parsed.

However, you can filter this a lil' bit with the remaining flags : 
```
  -d, --dmgs            Display the overall dmgs
  -dc, --dmgs_crits     Display the overall critical dmgs
  -dr, --dmgs_received  Display the overall dmgs received
  -hr, --heals_received
                        Display the overall heals received
  -hl, --heals          Display the overall heals provided
  -hlc, --heals_crits   Display the overall critical heals provided
```

For example, let's say you are a healer and you don't want to see the damages done by other players, you can use the flags to show only heals : 

`C:\Whatever-path-you-have\overlog.exe -hr -hl -hlc`

##### Display more infos about the session

**/!\ Preliminaries must have been done**

Using the `-m` flag, you will have some miscellaneous informations that could be of some use, for example : 

`C:\Whatever-path-you-have\overlog.exe -m`

```
You won 16404 XP, 3046 Dram and 10 Reputation on this session! :-)
You even completed 1 dungeons ! Amazing !
And btw, you were in combat for 1:36:50.602000 hour(s)
```
(Note that the combat time is the time you were ACTUALLY fighting in combat mode, not the time in a dungeon or something like that)


##### Display the loots you acquired during the session

**/!\ Preliminaries must have been done**

By using the `-lo` flag, you can quickly display all the loots you acquired in the whole `combat.log`.

It could be of some use for farmers (or to validate `luck` calculations maybe ;-) )

##### Any combination of options

All the options shown above can be mixed up, for example the following will work : 

`C:\Whatever-path-you-have\overlog.exe -f -r 10 -d -hlc -m`

### Python3 users (linux/windows/...)

The usage is pretty straightforward since there is no dependency and there is no need of compiled binary :-)

A good old `python3 overlog.py -h` will get you on track !
