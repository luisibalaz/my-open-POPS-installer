
# my-open-POPS-installer

A Command Line Tool used to create and install PS1 VCD from BIN files, into OPL POPS folder.

Currently only works on Linux, but it shouln't be too hard to add the extra code to run on Windows (and maybe Mac too).

Also, the printed informaton in console is in Spanish (but the docstrings inside the popsinstaller.py are in English, sorry for that). My plans are to have multiple language translations in multiple simple text files.

---

## How to "compile"?

 * Make sure to have Python >= 3.8 and a (not so old) gcc compiler installed.

 * **Recommended**: Create a virtualenv, where you can install all requirments inside `requirements.txt`, running `pip3 install -r requirements.txt`.

 * Just do

   ```
   make
   ```
   and it should compile into a `popsinstaller` executable (can be modified inside Makefile).

 * Also, if running different Python version, make sure to edit that on the Makefile.

### Compilation is not necessary!

You can run the `popsinstaller.py` directly, if you have Python and al dependencies satisfied. (Again, recommended to use a virtualenv).

The compiled version should, however, run without Python dependencies (in theory at least, have not tested, sorry for that).

 ---

## How to use?

To run the progam, you have multiple options
```
popsinstaller game.bin
popsinstaller game.cue
popsinstaller game.VCD
```
 * If a `bin` file is specified, it will create the corresponding `cue` and `VCD` files (if not already created and/or in POPS folder specified on the config file).
 * If a `cue` file is specified, it will search for the `bin` (and quit if not found), and create the `VCD` (if not already created and/or in POPS folder specified on the config file).
 * If a `VCD` file is specified, it will only renamte and copy it to the POPS folder (if not already created and/or in POPS folder specified on the config file).

### Optional arguments:

```
  -h, --help            Show help message and exit
  -f, --force           Force creation of Cue/VCD files
  -c /path/to/cfg, --config /path/to/cfg
                        Config file. Default is .env on root of this program
```

### Note!

It is mandatory for the executable, .env (if not using custom config) and resources folder to be on the same level, as in

```
/path/to/executable/popsinstaller
/path/to/executable/.env
/path/to/executable/resources/cue2pops
/path/to/executable/resources/cuemake.sh
/path/to/executable/resources/POPSTARTER.ELF
```

---

## The `resources` folder

It is necessary for you to provide these files and put them inside the `resources` folder:

 * `cue2pops`: Source code, needs compilation: https://github.com/makefu/cue2pops-linux
 * `cuemake.sh`: Source code, can copy and paste it: https://github.com/xadrianzetx/cuemake
 * `POPSTARTER.ELF`: Download from https://bitbucket.org/ShaolinAssassin/popstarter-documentation-stuff/wiki/Home, unZIP and paste the file inside `resources` folder.

If a link goes down, let me know.

---

## The `.env` file

### Structure

```
OPLDIR=/path/to/OPLfolder
POPSDIR=${OPLDIR}/POPS
MEDIA=SMB
SMBSHARE=PS2SMB
```

### Description

 * `OPLDIR`: Path to where the OPL folder is located (mounted to local PC).
 * `POPSDIR`: POPS subfolder of `OPLDIR`. Do not change.
 * `MEDIA`: Type of media you are using/configuring at the moment. Possible values:
  * `SMB` (tested and working)
  * `USB` (not tested)
  * `HDD` (not tested)
 * `SMBSHARE`: The name of the public SAMBA share (not currently in use).

### Multiple config/`.env` files.

You may chose a second config file with the `-c /path/to/cfg` optional parameter when calling `popsinstaller`. This is useful is you use multiple media, such as both USB and SMB. It is recommended to have your main config file in `.env` at the same folder as the executable, for convenience.

## Future plans

 * I'm planning to make it run on Windows, and to make a simple GUI interface to make it more user friendly. I may have to port it to another language.

 * Translations. It is coming to English very soon.

 * Merging BINS. Only a single BIN is supported right now.

 * Creation of more comple CUE files.
