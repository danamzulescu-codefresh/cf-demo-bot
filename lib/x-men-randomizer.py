import random
import sys
import subprocess


def run_command(full_command):
    proc = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = proc.communicate()
    print(output)
    if proc.returncode != 0:
        sys.exit(1)
    return b''.join(output).strip().decode()  # only save stdout into output, ignore stderr


def main():

    heroes = [
        'Wolverine',
        'Storm',
        'Beast',
        'Rogue',
        'Cyclops',
        'Gambit',
        'Jubilee'
    ]
    hero = random.choice(heroes)
    run_command('cf_export HERO={}'.format(hero))

    villains = [
        'Magneto',
        'Mystique',
        'Juggernaut',
        'Sabretooth',
        'Toad',
        'Mojo',
        'Pyro'
    ]
    villain = random.choice(villains)
    run_command('cf_export VILLAIN="{}"'.format(villain))

if __name__ == "__main__":
    main()