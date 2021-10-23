import sys
import os
import dotenv
import subprocess
import re
import argparse
import hashlib
import shutil
def game_id(bin_file):
    with open(bin_file,"rb") as f:
        f.seek(37696)
        N = 37696
        r0 = f.read(64).decode('utf-8',"replace")
        f.seek(37696)
        S = ""
        while "BOOT = cdrom:" not in S and "BOOT=cdrom:" not in S:
            r1 = f.read(64).decode('utf-8',"replace")
            N += 64
            S = r0+r1
            r0 = r1
        r2 = f.read(64).decode('utf-8',"replace")
    S = S + r2
    pattern = r'\w\w\w\w\w\d\d\d.\d\d'
    found = re.findall(pattern,S)
    return found[0].upper()

print(game_id(sys.argv[-1]))
