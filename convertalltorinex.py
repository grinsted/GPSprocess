# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 10:30:01 2018

@author: aslak
"""

import teqctool
import settings
import glob
import os
import re
import pathlib
import numpy as np
import datetime


def quoteifneeded(s):
    s = s.replace('"', '""')
    s = s.replace("\n", "")
    s = re.sub(r"(\S*\s\S.*)", r'"\1"', s)
    return s


def make_convert_script(input_file, min_time_delta=datetime.timedelta(minutes=5), join_small_gaps=datetime.timedelta(minutes=5)):
    """
    This function generates a batch file with teqc commands to split and convert the leica files.

    The batch script should be manually edited afterwards, to add stake ids etc.
    """
    try:
        meta = teqctool.get_meta(input_file)
    except:
        print("ERROR: teqc +meta failed on {}".format(input_file))
        return
    starts = meta["survey starts"]
    unit = settings.units[meta["receiver ID number"]]

    # combine starts if they are less than xx min appart.
    dt = np.diff(starts)
    eliminate = (dt[0:-1] < join_small_gaps).nonzero()
    starts = np.delete(starts, np.add(eliminate, 1))

    dbxfolder = os.path.dirname(input_file)
    batchfolder = os.path.dirname(dbxfolder)

    batchpath = [batchfolder, "teqc-{}.bat".format(os.path.basename(os.path.splitext(input_file)[0]))]
    batchpath = os.path.join(*batchpath)

    # TODO
    # Do not overwrite batch

    outputfolder = os.path.join(batchfolder, "Rinex")
    pathlib.Path(outputfolder).mkdir(parents=True, exist_ok=True)
    relrinexfolder = os.path.relpath(outputfolder, batchfolder)
    rel_input_file = os.path.relpath(input_file, batchfolder)

    if os.path.exists(batchpath):
        print("SKIPPING (already exists): {}".format(batchpath))
        return

    with open(batchpath, "w") as batchfile:

        batchfile.write("setlocal\n")

        teqcpath = os.path.relpath(os.path.dirname(settings.teqc), batchfolder)
        batchfile.write("set PATH={};%PATH%\n".format(teqcpath))

        batchfile.write("\n" * 3)

        nbincalls = 0
        for (ix, start) in enumerate(starts[:-1]):
            end = starts[ix + 1] - datetime.timedelta(seconds=10)
            if end - start < min_time_delta:
                print("skipping short survey...")
                continue

            if end - start.replace(second=0, hour=0, minute=0) < datetime.timedelta(days=1):
                # if it does not span midnight:
                outputname = "{}_{:%y%m%d_%H%M}".format(unit, start)
                outputname = os.path.join(relrinexfolder, outputname)
                obsfile = outputname + ".{:%y}o".format(start)
                navfile = outputname + ".{:%y}n".format(start)
                command = [
                    "teqc",
                    "-leica",
                    "mdb",
                    "-O.mo",
                    "StakeID",
                    "-st",
                    "{:%Y_%m_%d:%H:%M:%S}".format(start),
                    "-e",
                    "{:%Y_%m_%d:%H:%M:%S}".format(end),
                    "+obs",
                    obsfile,
                    "+nav",
                    navfile,
                    rel_input_file,
                ]
            else:
                outputname = "{}_daily_{}_".format(unit, chr(ord("A") + nbincalls))
                outputname = os.path.join(relrinexfolder, outputname)
                command = [
                    "teqc",
                    "-leica",
                    "mdb",
                    "-O.mo",
                    "StakeID",
                    "-st",
                    "{:%Y_%m_%d:%H:%M:%S}".format(start),
                    "-e",
                    "{:%Y_%m_%d:%H:%M:%S}".format(end),
                    "+obs",
                    "+",
                    "+nav",
                    "+",
                    "-tbin",
                    "1d",
                    outputname,
                    rel_input_file,
                ]
                nbincalls = nbincalls + 1
            commandasstring = " ".join([quoteifneeded(elem) for elem in command])
            batchfile.write(commandasstring)
            batchfile.write("\n" * 2)

        batchfile.write("pause\n")


rootdir = settings.folders["originaldata"] + r"\2022"
pattern = "*.m00"


for filename in glob.iglob(os.path.join(rootdir, "**", pattern), recursive=True):
    print("Input file: {}".format(filename))
    make_convert_script(input_file=filename)
