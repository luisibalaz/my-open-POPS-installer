#!/bin/python3
import sys
import os
import dotenv
import subprocess
import re
import argparse
import hashlib
import shutil

def md5(fname):
    """Expects a filename
    Returns md5sum of the file as string"""
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

class Game(object):
    """Class to represent a BIN file game and its appropiate properties and
    methods"""
    media_prefix = {
        "SMB":"SB.",
        "USB":"XX.",
        "HDD":""
    }

    def __init__(self,filename,force_creation,MEDIA):
        """Creates a Game instance, whose file name is determined by "filename",
        "force_creation" dictates if we overwrite previously create files,
        "MEDIA" determines if we are using to HDD, USB o SMB in OPL"""
        self.media = MEDIA
        self.check_files()
        self.base_name = os.path.splitext(filename)[0]
        status = self.bin_cue_vcd_check()
        self.bin_file = status[0][0]
        self.cue_file = status[0][1]
        self.vcd_file = status[0][2]
        self.bin_exists = status[1][0]
        self.cue_exists = status[1][1]
        self.vcd_exists = status[1][2]
        self.game_id = self.get_id()
        self.new_vcd = f"{self.game_id}.{self.vcd_file}"
        self.elf_name = self.elf_name()
        self.vcd_media_exists = os.path.isfile(os.path.join(POPSDIR,self.new_vcd))
        self.force_creation = force_creation
        self.ensure_bin()
        self.create_cue()
        self.create_vcd()
        self.move_files()

    def check_files(self):
        """Checks is necessary files in order to run VCD games exists and if md5sum is correct.
        If not, asks you to download them"""
        if self.media == "HDD":
            files_to_check = [x for x in os.listdir(POPSDIR) if x.lower() == "pops.elf" or x.lower() == "ioprp252.img"]
            md5check = {"pops.elf":"355a892a8ce4e4a105469d4ef6f39a42","ioprp252.img":"1db9c6020a2cd445a7bb176a1a3dd418"}
        elif self.media == "USB" or self.media == "SMB":
            files_to_check = [x for x in os.listdir(POPSDIR) if x.lower() == "pops_iox.pak"]
            md5check = {"pops_iox.pak":"a625d0b3036823cdbf04a3c0e1648901"}
        for f in files_to_check:
            if md5(os.path.join(POPSDIR,f)) == md5check[f.lower()]:
                print(f"{f} ... OK")
            else:
                print(f"md5sum de {f} no es correcta. Probablemente el archivo esté dañado. Descárgalo de nuevo.")
                while True:
                    user_input = input("¿Continuar de todas formas? [y/n]: ")
                    if user_input.lower() not in ["y","n"]:
                        print("Respuesta no válida")
                        continue
                    elif user_input.lower() == "n":
                        print("Abortando...")
                        quit()
                    elif user_input.lower() == "y":
                        print("Continuando...")
                        break
        return


    def elf_name(self):
        """Given itself as a parameter, it finds necessary strings to create the
        final name of the ELF that goes into POPS folder"""
        return f"{Game.media_prefix[self.media]}{self.game_id}.{self.base_name}.ELF"

    def bin_cue_vcd_check(self):
        """Checks if bin, cue and VCD files exist.
        Generates filenames appropriately
        Returns two tuples in the form of
        (bin file, cue file, vcd file),(bin exists,cue exists,vcd exists)"""
        print(self.base_name)
        try:
            bin_name = [x for x in os.listdir(os.getcwd()) if x.lower() == self.base_name.lower() + ".bin"][0]
        except IndexError:
            bin_name = self.base_name + "bin"
        try:
            cue_name = [x for x in os.listdir(os.getcwd()) if x.lower() == self.base_name.lower() + ".cue"][0]
        except IndexError:
            cue_name = self.base_name + ".cue"
        vcd_name = self.base_name + ".VCD"
        bin_exists = os.path.isfile(os.path.join(CWD,bin_name))
        cue_exists = os.path.isfile(os.path.join(CWD,cue_name))
        vcd_exists = os.path.isfile(os.path.join(CWD,vcd_name))
        return ((bin_name,cue_name,vcd_name),(bin_exists,cue_exists,vcd_exists))

    def ensure_bin(self):
        """Bin file HAS to exist. If it doesnt, quit"""
        if not self.bin_exists:
            print("Archivo Bin no existe.")
            if self.vcd_exists:
                print("Utilizando VCD en su lugar...")
            else:
                print("Abortando...")
                quit()
        return

    def create_cue(self):
        """If CUE file doesn't exists, or if we force its creation, creates CUE file"""
        if self.force_creation:
            print("Forzando creación de archivo CUE...")
            try:
                os.remove(os.path.join(CWD,self.cue_file))
                self.cue_exists = False
            except FileNotFoundError:
                pass
        if not self.cue_exists:
            if not self.bin_exists:
                return
            print("Creando archivo CUE...")
            generate_cue = ["bash",cuemake,"-b",self.bin_file]
            subprocess.run(generate_cue)
            print("Creado")
        else:
            print("Archivo Cue ya existe localmente")
        return

    def create_vcd(self):
        """If VCD file doesn't exists, or if we force its creation, creates VCD file"""
        if self.vcd_media_exists:
            self.vcd_exists = True
        if self.force_creation:
            print("Forzando creación de archivo VCD...")
            try:
                os.remove(os.path.join(CWD,self.vcd_file))
            except FileNotFoundError:
                pass
            finally:
                self.vcd_exists = False
                self.vcd_media_exists = False
        if not self.vcd_exists:
            print("Creando archivo VCD...")
            generate_vcd = [cue2pops,self.cue_file]
            subprocess.run(generate_vcd)
            print("Creado")
        else:
            if not self.cue_exists:
                return
            print("Archivo VCD ya existe en el dispositivo")
        return

    def get_id(self):
        """Function to scan BIN file and extract the GAME ID.
        MIGHT NOT BE 100% RELIABLE
        IF IT RUNS FOR TOO LONG, CANCEL OR IT WILL NEVER STOP"""
        try:
            return self.game_id
        except AttributeError:
            file_to_open = self.bin_file if self.bin_exists else self.vcd_file
            with open(file_to_open,"rb") as f:
                f.seek(37696)
                r0 = f.read(1024).decode('utf-8',"replace")
                f.seek(37696)
                S = ""
                while "BOOT" not in S:
                    r1 = f.read(1024).decode('utf-8',"replace")
                    S = r0+r1
                    r0 = r1
                r2 = f.read(1024).decode('utf-8',"replace")
            S = S + r2
            pattern = r'\w\w\w\w\w\d\d\d.\d\d'
            found = re.findall(pattern,S)
            return found[0].upper()

    def move_files(self):
        """Moves and renames necessary files to POPS folder"""
        try:
            if not self.vcd_media_exists:
                print("Copiando...")
                shutil.move(os.path.join(CWD,self.vcd_file), os.path.join(POPSDIR,self.new_vcd), copy_function = shutil.copyfile)
        except:
            print("No se pudo mover el archivo VCD a la carpeta de OPL.")
            print(f"Manualmente, cópialo y pégalo en {POPSDIR}, renombrado como")
            print(self.new_vcd)
        finally:
            try:
                shutil.copyfile(os.path.join(EXECDIR,"resources","POPSTARTER.ELF"), os.path.join(POPSDIR,self.elf_name))
            except:
                print("No se pudo copiar POPSTARTER.ELF a la carpeta de OPL.")
                print(f"Manualmente, cópialo y pégalo en {POPSDIR}, renombrado como")
                print(self.elf_name)
        return


try:
    EXECDIR=os.path.dirname(os.path.abspath(__file__))
except NameError:
    EXECDIR=os.path.dirname(sys.executable)

# To process arguments
parser = argparse.ArgumentParser()
parser.add_argument("game",help="bin/cue/vcd file")
parser.add_argument('-f',"--force", action='store_true', help='Force creation of Cue/VCD files')
parser.add_argument('-c',"--config",nargs="?",const=1,default=os.path.join(EXECDIR,".env"),type=str, help='Config file. Default is .env on root of this program')
args = parser.parse_args()
path = args.game
force_creation = args.force
config_path = os.path.abspath(args.config)
input_file = os.path.basename(os.path.abspath(path))

# Welcome screen

print("*****************************************")
print("       popsinstaller by luisibalaz       ")
print("Actualmente sólo se soporta 1 archivo bin")
print("*****************************************")

# Obtain necessary data from the system and configs from .env file

dotenv.load_dotenv(config_path)
CWD = os.path.dirname(os.path.abspath(path))
os.chdir(CWD)
try:
    OPLDIR = os.environ["OPLDIR"]
    POPSDIR = os.environ["POPSDIR"]
    MEDIA = os.environ["MEDIA"]
except KeyError:
    print("Archivo de configuración incorrecto. Abortando...")
    quit()
if not os.path.isdir(OPLDIR):
    print("La carpeta de OPL definida en .env no es válida. Abortando...")
    quit()
if MEDIA not in ["SMB","USB","HDD"]:
    print("El medio en .env no es SMB, USB o HDD. Abortando...")
    quit()
if MEDIA == "SMB":
    SMBSHARE = os.environ["SMBSHARE"]
else:
    SMBSHARE = ""
print("Carpeta actual" + ": " + CWD)
print("Carpeta OPL" + ": " + OPLDIR)
print("Carpeta POPS" + ": " + POPSDIR)

# cue2pops and cuemake files
# currently only for LINUX. Don't know how to use them for Windows for now

if os.name == "nt":
    pass
elif os.name == "posix":
    cue2pops_file = "cue2pops"
    cuemake_file = "cuemake.sh"

cue2pops = os.path.join(EXECDIR, "resources", cue2pops_file)
cuemake = os.path.join(EXECDIR, "resources", cuemake_file)

# Instance of Game class. This is where CUE, VCD files are created.
game = Game(input_file,force_creation,MEDIA)

cfg_prefix = { # Just a dictionary to store some prefixes
    "SMB":"smb:/POPS/",
    "USB":"mass:/POPS/",
    "HDD":"pfs0:/POPS/"
    }

newline = f"{game.base_name}={cfg_prefix[game.media]}{game.elf_name}\n" # Construction of newline in conf_apps.cfg
pattern = r'\w\w\w\w\w\d\d\d.\d\d' # A pattern in the form SLUS_999.99, for example
already_in_cfg = False

with open(os.path.join(OPLDIR,"conf_apps.cfg"),"r") as cfg: # Open cfg file and read it
    lines = cfg.readlines()
    if newline in lines:
        print("Juego ya se encuentra añadido en cfg")
        already_in_cfg = True
    pops_games = [(i,x.strip()) for i,x in enumerate(lines) if "POPS" in x.strip()]
is_badly_named = False
badly_named_files = []
for i in range(len(pops_games)):
    found = re.findall(pattern,pops_games[i][1])
    try:
        if found[0] == game.game_id:
            if not already_in_cfg:
                badly_named_files.append([0,newline,2])
    except IndexError:
        badly_named_files.append([*pops_games[i],0])
    finally:
        if not os.path.isfile(os.path.join(POPSDIR,pops_games[i][1].split("/POPS/")[1])):
            badly_named_files.append([*pops_games[i],1])

def print_badly_named(badly_named_files):
    """Given specific error codes asigned by the code above, process them and Given
    the user feedback about what is going on"""
    if len(badly_named_files) != 0:
        print("Tienes archivos nombrados incorrectamente:")
        for tup in badly_named_files:
            if tup[2] == 0:
                print(f"{tup[0]}:{tup[1]} : Se espera tener GAME ID")
        for tup in badly_named_files:
            if tup[2] == 1:
                print(f"{tup[0]}:{tup[1]} : Archivo no encontrado")
        for tup in badly_named_files:
            if tup[2] == 2:
                print(f"{tup[1]}: GAME ID ya en uso")

print_badly_named(badly_named_files)

if not already_in_cfg: # Add game to cfg if not already in it
    with open(os.path.join(OPLDIR,"conf_apps.cfg"),"a") as cfg:
        print("Actualizando configuración...")
        cfg.write(newline)

print("Finalizando...")
