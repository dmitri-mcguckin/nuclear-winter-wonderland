#!/usr/bin/env python3
import os, sys
from pack_constructor.pack import Pack, Version, ForgeVersion, ATTRS
from pack_constructor.mod import Mod
from ftf_utilities import log, Mode, load_json, dump_json

def usage(msg):
    log(Mode.ERROR, msg + "\n\nusage: packer.py <target manifest> <destination manifest>")
    sys.exit(-1)

def load_mc_home():
    env_name = "MC_HOME"
    mc_home = os.getenv(env_name)
    if(mc_home is None):
        valid = False
        log(Mode.WARN, "Environment variable: " + env_name + " was not found! \
            \n\tDue to the changing nature of Curseforge's API and the rules surrounding it, this tool depends on any third party laucher to download the mods needed in order to build the server.")

        while(not valid):
            mc_home = input("Please enter the path to the top-level instances folder of your minecraft laucher: ")
            mc_home = os.path.expanduser(mc_home)

            if(os.path.exists(mc_home)):
                os.putenv(env_name, mc_home)
                break
            else: log(Mode.ERROR, "Path does not exist: " + str(mc_home))

    log(Mode.WARN, "To prevent this warning in the future, decalre the environment variable 'MC_HOME' with the path th the top-level instances folder of your minecraft launcher.")
    return os.path.expanduser(mc_home)

def menu():
    log(Mode.INFO, "Stuff to do: \
        \n\t*.) set [attribute] \
        \n\t*.) get [attribute/all] \
        \n\t*.) add \
        \n\t*.) del [mod name] \
        \n\t*.) build [client/server] \
        \n\n\tAttributes: \
        \n\t\t\tname \
        \n\t\t\tpack version \
        \n\t\t\tmc version \
        \n\t\t\tforge version \
        \n\t\t\tauthor")

def parse_version(version_string, forge = False):
    pieces = list(map(lambda x: int(x), version_string.split('.')))
    if(forge): res = ForgeVersion(pieces[0], pieces[1], pieces[2], pieces[3])
    else: res = Version(pieces[0], pieces[1], pieces[2])
    return res

def set_attr(pack, attr, val):
    if(attr not in ATTRS): raise AttributeError()

    if(attr == 'pack_version' or attr == 'mc_version'):
        setattr(pack, attr, parse_version(val))
    elif(attr == 'forge_version'):
        setattr(pack, attr, parse_version(val, forge = True))
    else: setattr(pack, attr, val)

def get_attr(pack, attr): return str(getattr(pack, attr))

def add_mod(): pass
def del_mod(name): pass


def load_manifest(filename):
    manifest = load_json(filename)
    minecraft = manifest['minecraft']

    name = manifest['name']
    pack_version = parse_version(manifest['version'])
    mc_version = parse_version(minecraft['version'])
    forge_version = parse_version(minecraft['modLoaders'][0]['id'][6:], forge= True)
    author = manifest['author']
    mods = manifest['files']

    pack = Pack(name, pack_version, mc_version, forge_version, author)

    for raw_mod in mods:
        name = raw_mod.get('name')
        if(name is None): name = "N/A"
        mod = Mod(raw_mod['projectID'], raw_mod['fileID'], name, required = raw_mod['required'])
        pack.add(mod)
    return pack

def dump_manifest(pack, filename = None):
    if(filename is None): filename = "build/manifest.json"
    dump_json(filename, pack.to_dict())
    log(Mode.INFO, "Generated manifest at: " + filename)

def main(args):
    if(len(args) == 0): usage("Missing arguments!")
    manifest_in = args[0]

    # Figure out manifest output
    if(len(args) == 2): manifest_out = args[1]
    else: manifest_out = None

    # Load the manifest
    pack = load_manifest(manifest_in)

    # Check for mc home
    mc_home = load_mc_home()

    # Create the build/staging directories
    os.makedirs("build", exist_ok = True)
    os.makedirs("staging", exist_ok = True)

    # Runtime loop
    menu()
    for input in sys.stdin:
        input = input.lower().strip()

        if(input == 'q'): sys.exit(0)
        elif(input == 'x'): break
        elif(input == 'w'): dump_manifest(pack, filename = manifest_out)
        elif(input.startswith("menu") or input.startswith("help")):
            menu()
        elif(input.startswith('set') or input.startswith('get')):
            try: cmd, attr, *args = input.split(' ')
            except ValueError as e:
                log(Mode.ERROR, "Not enough arguments!")
                continue

            try:
                if(cmd == 'get'):
                    if(attr == 'all'):
                        msg = "Pack Info:"
                        for a  in ATTRS: msg += "\n" + a + ": " + get_attr(pack, a)
                        msg += "\nmods (" + str(len(pack)) + "):"
                        for mod in pack.alphabetical_mod_list(): msg += "\n\t" + str(mod)
                        log(Mode.INFO, msg)
                    else: log(Mode.INFO, attr + ": " + get_attr(pack, attr))
                elif(cmd == 'set'):
                    args = ' '.join(args)
                    set_attr(pack, attr, args)
            except AttributeError as e: log(Mode.ERROR, "No such attribute: " + str(attr))
        elif(input.startswith('add') or input.startswith('del')):
            try: cmd, attr, *args = input.split(' ')
            except ValueError as e:
                log(Mode.ERROR, "Not enough arguments!")
                continue
        elif(input.startswith('build')):
            try: cmd, attr, *args = input.split(' ')
            except ValueError as e:
                log(Mode.ERROR, "Not enough arguments!")
                continue

            if(attr == 'client'):
                # Do da copys
                pass
            elif(attr == 'server'):
                server_name = pack.name.replace(' ', '-').lower() + '-' + str(pack.pack_version) + '-' + str(pack.forge_version.forge)
                client_build_path = mc_home + os.sep + server_name

                if(not os.path.exists(client_build_path)):
                    log(Mode.ERROR, "Client instance expected but not found at: " + client_build_path)
                    continue

                # Do da copys
            else:
                log(Mode.ERROR, "Unrecognized build command: " + attr)
                continue

    # Save the manifest
    dump_manifest(pack, filename = manifest_out)

if __name__ == "__main__": main(sys.argv[1:])
