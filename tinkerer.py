#!/usr/bin/env python3
import os, sys, zipfile
from constructs.pack import Pack, Version, ForgeVersion, ATTRS
from constructs.mod import Mod
from shutil import *
from ftf_utilities import log, Mode, load_json, dump_json

def usage(msg):
    log(Mode.ERROR, msg + '\n\nusage: packer.py <target manifest> <destination manifest>')
    sys.exit(-1)

def load_mc_home():
    env_name = 'MC_HOME'
    mc_home = os.getenv(env_name)
    if(mc_home is None):
        valid = False
        log(Mode.WARN, 'Environment variable: ' + env_name + ' was not found! \
            \n\tDue to the changing nature of Curseforge\'s API and the rules surrounding it, this tool depends on any third party laucher to download the mods needed in order to build the server.')

        while(not valid):
            mc_home = input('Please enter the path to the top-level instances folder of your minecraft laucher: ')
            mc_home = os.path.expanduser(mc_home)

            if(os.path.exists(mc_home)):
                os.putenv(env_name, mc_home)
                break
            else: log(Mode.ERROR, 'Path does not exist: ' + str(mc_home))

    log(Mode.WARN, 'To prevent this warning in the future, decalre the environment variable \'MC_HOME\' with the path th the top-level instances folder of your minecraft launcher.')
    return os.path.expanduser(mc_home)

def menu():
    log(Mode.INFO, 'Stuff to do: \
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
        \n\t\t\tauthor')

def parse_version(version_string, forge = False):
    pieces = list(map(lambda x: int(x), version_string.split('.')))
    if(forge): res = ForgeVersion(pieces[0], pieces[1], pieces[2], pieces[3])
    else: res = Version(pieces[0], pieces[1], pieces[2])
    return res

def translate_attr(attr):
    for field in ATTRS:
        if attr in field: return field
    return attr

def set_attr(pack, attr, val):
    attr = translate_attr(attr)
    if(attr not in ATTRS): raise AttributeError()

    if(attr == 'pack_version' or attr == 'mc_version'):
        setattr(pack, attr, parse_version(val))
    elif(attr == 'forge_version'):
        setattr(pack, attr, parse_version(val, forge = True))
    else: setattr(pack, attr, val)

def get_attr(pack, attr):
    attr = translate_attr(attr)
    return attr, str(getattr(pack, attr))

def add_mod(pack):
    log(Mode.INFO, "Adding a new mod to the registry...")

    name = input("Mod Name: ")

    valid = False
    while not valid:
        try:
            project_id = int(input("Curseforge Project ID: "))
            valid = True
        except: valid = False

    valid = False
    while not valid:
        try:
            file_id = int(input("Curseforge File ID: "))
            valid = True
        except: valid = False

    valid = False
    while not valid:
        required = input("Required [Y/n]: ").lower()
        if(required == 'y' or required == ''): required = True
        elif(required == 'n'): required = False
        else: continue

        break

    mod = Mod(project_id, file_id, name, required)
    pack.add(mod)

def del_mod(pack, name):
    for mod in pack.mods:
        if name.lower() in mod.name.lower():
            pack.mods.remove(mod)
            return True, mod.name
    return False, None

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
        if(name is None): name = 'N/A'
        mod = Mod(raw_mod['projectID'], raw_mod['fileID'], name, required = raw_mod['required'])
        pack.add(mod)
    return pack

def dump_manifest(pack, filename = None):
    if(filename is None): filename = 'staging/manifest.json'
    dump_json(filename, pack.to_dict())
    log(Mode.INFO, 'Generated manifest at: ' + filename)

def destroy_staging():
    rmtree('build', ignore_errors = True)
    rmtree('staging', ignore_errors = True)

def regenerate_staging():
    os.makedirs('build', exist_ok = True)
    os.makedirs('staging', exist_ok = True)

def zip_directory(path, zipper):
    for root, dirs, files in os.walk(path):
        for file in files:
            filename = os.path.join(root, file)
            arcname = '/'.join(filename.split('/')[1:])
            log(Mode.DEBUG, 'Packaging: ' + arcname)
            zipper.write(filename, arcname = arcname)

def build_client(pack_name, manifest_path):
    pack_zip = pack_name + '.zip'
    copyfile(manifest_path, 'staging/manifest.json')
    copytree('res/overrides', 'staging/overrides')
    zipper = zipfile.ZipFile(pack_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel = 9)
    zip_directory('staging', zipper)
    zipper.close()
    move(pack_zip, 'build')

def build_server(pack, pack_name, manifest_path, client_build_path):
    path = 'res/resources.properties'
    file = open(path, 'r')
    properties = file.read()
    file.close()

    lines = properties.split('\n')
    # lines[0] = lines[0] # Currently no need to regenerate this part
    lines[1] = 'export MC_VERSION=' + str(pack.mc_version)
    lines[2] = 'export FORGE_VERSION=' + pack.forge_version.bannerless_str()
    properties = '\n'.join(lines)

    file = open(path, 'w+')
    log(Mode.DEBUG, 'Properties:\n' + str(properties))
    file.write(str(properties))
    file.close()

def main(args):
    save_on_exit = False
    if(len(args) == 0): usage('Missing arguments!')
    manifest_in = args[0]

    # Figure out manifest output
    if(len(args) == 2): manifest_out = args[1]
    else: manifest_out = args[0]

    pack = load_manifest(manifest_in) # Load the manifest
    mc_home = load_mc_home() # Check for mc home
    destroy_staging() # Get rid of any old temp files

    # Runtime loop
    menu()
    for input in sys.stdin:
        input = input.lower().strip()

        # Command processing
        if(input == 'q'): break
        elif(input == 'x'):
            save_on_exit = True
            break
        elif(input == 'w'):
            save_on_exit = True
            break
        elif(input.startswith('menu') or input.startswith('help')):
            menu()
        elif(input.startswith('set') or input.startswith('get')):
            try: cmd, attr, *args = input.split(' ')
            except ValueError as e:
                log(Mode.ERROR, 'Not enough arguments!')
                continue

            try:
                if(cmd == 'get'):
                    if(attr == 'all'):
                        msg = 'Pack Info:'
                        for a in ATTRS:
                            key, val = get_attr(pack, a)
                            msg += '\n' + key + ': ' + val
                        msg += '\nmods (' + str(len(pack)) + '):'
                        for mod in pack.alphabetical_mod_list(): msg += '\n\t' + str(mod)
                        log(Mode.INFO, msg)
                    else:
                        key, val = get_attr(pack, attr)
                        log(Mode.INFO, key + ': ' + val)
                elif(cmd == 'set'):
                    val = ' '.join(args)
                    set_attr(pack, attr, val)
            except AttributeError as e: log(Mode.ERROR, 'No such attribute: ' + str(attr))
        elif(input.startswith('add') or input.startswith('del')):
            try: cmd, *attr = input.split(' ')
            except ValueError as e:
                log(Mode.ERROR, 'Not enough arguments!')
                continue

            if(cmd == 'add'): add_mod(pack)
            else:
                search_terms = ' '.join(attr)
                deleted, mod_name = del_mod(pack, search_terms)
                if(deleted): msg = "Deleted mod: " + mod_name
                else: msg = "Could not find mod: " + search_terms
                log(Mode.INFO, msg)

        elif(input.startswith('build')):
            destroy_staging()
            regenerate_staging()

            dump_manifest(pack, filename = manifest_out)
            server_name = pack.name.replace(' ', '-').lower() + '-' + str(pack.pack_version) + '-' + str(pack.forge_version.forge)

            try: cmd, attr, *args = input.split(' ')
            except ValueError as e:
                log(Mode.ERROR, 'Not enough arguments!')
                continue

            if(attr == 'client'): build_client(server_name, manifest_in)
            elif(attr == 'server'):
                client_build_path = mc_home + os.sep + server_name

                if(not os.path.exists(client_build_path)):
                    log(Mode.ERROR, 'Client instance expected but not found at: ' + client_build_path)
                    continue
                build_server(pack, server_name, manifest_in, client_build_path)
            else:
                log(Mode.ERROR, 'Unrecognized build command: ' + attr)
                continue
        elif(input.startswith('clear')): destroy_staging()

    # Save the manifest
    if(save_on_exit): dump_manifest(pack, filename = manifest_out)
    destroy_staging()

if __name__ == '__main__': main(sys.argv[1:])