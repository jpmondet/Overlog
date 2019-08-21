#! /usr/bin/env python3



def main():

    fighters = dict()
    damages_taken = dict()
    with open("combat.log") as clog:
        for line in clog:
            if line.startswith("[Combat]"):
                words = line.split()
                dude_hurt = words[1]
                damage_dealer = words[-1]
                damages = (int)(words[-4])
                if fighters.get(damage_dealer):
                    fighters[damage_dealer] = (int)(fighters[damage_dealer]) + damages
                else:
                    fighters[damage_dealer] = damages

                if damages_taken.get(dude_hurt):
                    damages_taken[dude_hurt] = (int)(damages_taken[dude_hurt]) + damages
                else:
                    damages_taken[dude_hurt] = damages



    print(fighters)
    print(damages_taken)

if __name__ == "__main__":
    main()
