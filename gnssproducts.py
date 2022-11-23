# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 10:17:56 2018

@author: aslak
"""

import pandas as pd
import datetime
import gpstime
import os
import pathlib
import re
from urllib.parse import urlparse
import ftplib
import subprocess

import settings


def loaddatacenterurls():
    """
    ==================================================================================
    The urls of all the Data centers are in url_list. That file is from RTKLIB

    Here I load it and modify it to suit gps_sprintf() and figure out the download interval
    ==================================================================================
    """
    datacenterurls = pd.read_table(r"URL_LIST.txt", header=None, comment=r"#", names=["key", "url", "interval"], delim_whitespace=True, index_col=0)

    for i, row in datacenterurls.iterrows():
        url = row["url"]

        upperurl = url.upper()
        interval = datetime.timedelta(days=100000)
        if "%Y" in upperurl:
            interval = datetime.timedelta(days=365)
        if "%M" in upperurl:
            interval = datetime.timedelta(days=28)
        if "%W" in upperurl:
            interval = datetime.timedelta(days=7)
        if "%D" in upperurl:
            interval = datetime.timedelta(days=1)
        if "%N" in upperurl:
            interval = datetime.timedelta(days=1)
        if "%H" in upperurl:
            interval = datetime.timedelta(hours=1)
        row["interval"] = interval

        # convert sprintf style url to something pythons .format function likes:
        url = url.replace("%Y", "{date:%Y}")  # .        %Y -> yyyy    : year (4 digits) (2000-2099)
        url = url.replace("%y", "{date:%y}")  # .        %y -> yy      : year (2 digits) (00-99)
        url = url.replace("%m", "{date:%m}")  # .        %m -> mm      : month           (01-12)
        url = url.replace("%d", "{date:%d}")  # .        %d -> dd      : day of month    (01-31)
        url = url.replace("%D", "{dayofgpsweek}")  # .       %D -> d       : day of gps week (0-6)
        url = url.replace("%h", "{date:%h}")  # .        %h -> hh      : hours           (00-23)
        url = url.replace("%H", "{hourcode}")  # .        %H -> a       : hour code       (a-x)
        url = url.replace("%M", "{date:%M}")  # .        %M -> mm      : minutes         (00-59)
        url = url.replace("%n", "{doy:03d}")  # .        %n -> ddd     : day of year     (001-366)
        url = url.replace("%W", "{gpsweek:04d}")  # .        %W -> wwww    : gps week        (0001-9999)
        # url = url.replace('%s','{upperstationame:04d}') # .        %s -> ssss    : station name    (lower-case)
        # .        %S -> SSSS    : station name    (upper-case)
        # .        %r -> rrrr    : station name
        row["url"] = url
    return datacenterurls


datacenterurls = loaddatacenterurls()


def gps_sprintf(url, date):
    hourcode = chr(ord("a") + date.hour - 1)
    gpsweek = gpstime.gpsWeek(date.year, date.month, date.day)
    dayofgpsweek = gpstime.dayOfWeek(date.year, date.month, date.day)
    doy = gpstime.julianDay(date.year, date.month, date.day)
    return url.format(date=date, hourcode=hourcode, dayofgpsweek=dayofgpsweek, doy=doy, gpsweek=gpsweek)


def extract(compressedfile, targetfolder):
    if compressedfile.endswith(".tar.gz"):
        subprocess.call([settings.tar, "-xzf", compressedfile, "-C", targetfolder])
    elif compressedfile.endswith(".Z") or compressedfile.endswith(".gz"):
        subprocess.call([settings.gunzip, compressedfile])
    # TODO:otherwise move file to that folder


def productfiles(product_key, start_date, end_date):
    """
    Returns a list of files with a given product key and covering the date range specified.

    Will auto downloads and extract missing files.

    @author: aslak
    """
    product = datacenterurls.loc[product_key]
    date = start_date
    files = []
    while date < end_date + product["interval"]:
        if date > end_date:
            date = end_date
        url = gps_sprintf(product["url"], date)
        urlfilename = os.path.basename(url)
        localfile = re.sub("(.tar.gz|.Z)$", "", urlfilename)
        localfolder = os.path.join(settings.folders["GNSSproducts"], product_key, str(date.year))

        if not os.path.isfile(os.path.join(localfolder, localfile)):
            print("    - Downloading {}".format(url))
            url = urlparse(url)
            # DOWNLOAD IT!
            if url.scheme == "ftp":
                ftpfun = ftplib.FTP
            else:
                ftpfun = ftplib.FTP_TLS
            with ftpfun(url.netloc) as ftp:
                ftp.login(user="anonymous", passwd="anslak@nbi.ku.dk")
                if url.scheme == "ftps":
                    ftp.prot_p()
                localpath = os.path.join(localfolder, urlfilename)
                pathlib.Path(localfolder).mkdir(parents=True, exist_ok=True)
                with open(localpath, "wb") as f:
                    ftp.cwd(os.path.dirname(url.path))
                    ftp.retrbinary("RETR " + urlfilename, f.write)
            # EXTRACT IT!
            extract(localpath, localfolder)

        files.append(os.path.join(localfolder, localfile))

        date = date + product["interval"]

    return set(files)


if __name__ == "__main__":
    # this is for testing only

    startdate = datetime.datetime(2018, 7, 31, 16, 51, 17)
    enddate = datetime.datetime(2018, 8, 3, 0, 0, 0)
    url = datacenterurls.loc["IGS_EPH"]["url"]
    print(gps_sprintf(url, startdate))
    assert gps_sprintf(url, startdate) == "ftp://cddis.gsfc.nasa.gov/gps/products/2012/igs20122.sp3.Z"

    print(productfiles("IGS_EPH", startdate, enddate))
