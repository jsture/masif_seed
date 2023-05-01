import os
import sys
from subprocess import Popen, PIPE, run, CalledProcessError

from input_output.read_msms import read_msms
from triangulation.xyzrn import output_pdb_as_xyzrn
from default_config.global_vars import msms_bin
from default_config.masif_opts import masif_opts
import random

# Pablo Gainza LPDI EPFL 2017-2019
# Calls MSMS and returns the vertices.
# Special atoms are atoms with a reduced radius.
def computeMSMS(pdb_file, protonate=True):
    print(f"Computing MSMS for {pdb_file}")
    randnum = random.randint(1, 10000000)
    file_base = masif_opts["tmp_dir"] + "/msms_" + str(randnum)
    out_xyzrn = file_base + ".xyzrn"

    if protonate:
        output_pdb_as_xyzrn(pdb_file, out_xyzrn)
    else:
        print("Error - pdb2xyzrn is deprecated.")
        sys.exit(1)
    # Now run MSMS on xyzrn file
    probe_start = 1.505
    vert_exists = False
    fudge = 0
    while not vert_exists:
        probe_radius = probe_start + fudge
        try:
            print("Running MSMS with probe radius: " + str(probe_radius))
            args = [
                msms_bin,
                "-density",
                "3.0",
                "-hdensity",
                "3.0",
                "-probe",
                str(probe_radius),
                "-if",
                out_xyzrn,
                "-of",
                file_base,
                "-af",
                file_base,
            ]
            run(args, stdout=PIPE, stderr=PIPE, check=True)
            vert_exists = os.path.exists(file_base + ".vert")
        except Exception as e:
            print(e)
            fudge += 0.01
            if probe_radius > 2.0:
                print("Error: MSMS failed to run.")
                sys.exit(1)
            continue

    vertices, faces, normals, names = read_msms(file_base)
    areas = {}
    ses_file = open(file_base + ".area")
    next(ses_file)  # ignore header line
    for line in ses_file:
        fields = line.split()
        areas[fields[3]] = fields[1]

    # Remove temporary files.
    os.remove(file_base + ".area")
    os.remove(file_base + ".xyzrn")
    os.remove(file_base + ".vert")
    os.remove(file_base + ".face")
    return vertices, faces, normals, names, areas
