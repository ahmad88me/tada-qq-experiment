"""
This is based on https://github.com/oeg-upm/ttla/blob/master/data/preprocessing.py
and was adjusted for Python 3

To install the reqs:

pip install requests unicodecsv chardet
"""
import sys
import os
import json
import unicodecsv as csv
import logging
import chardet
import requests
import tarfile
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# DATA_DIR = "data"
# DEST_DIR = os.path.join(DATA_DIR, "T2Dv2")
ARC_FNAME = "extended_instance_goldstandard.tar.gz"


def json_to_csv(fname, overwrite=False):
    """
    :param fname: of the json file
    :return:
    """

    #csv_fname = fname[:-4] + "csv"
    csv_fname = fname[:-4] + "tar.gz.csv"

    csv_dest = os.path.join(DEST_DIR, csv_fname)
    if os.path.exists(csv_dest) and not overwrite:
        logger.info("%s already exists" % csv_dest)
        return
    json_fdir = os.path.join(DATA_DIR, "tables", fname)
    f = open(json_fdir, "rb")
    s = f.read()
    detected_encoding = chardet.detect(s)['encoding']
    logger.debug("detected encoding %s for %s" % (detected_encoding, fname))
    decoded_s = s.decode(detected_encoding)
    j = json.loads(decoded_s)
    f.close()
    table = zip(*j["relation"])

    with open(csv_dest, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for row in table:
            writer.writerow(row)

    logger.debug("generate csv %s" % csv_dest)


def export_files_to_csv():

    if not os.path.exists(DEST_DIR):
        os.mkdir(DEST_DIR)

    if not os.path.exists(os.path.join(DATA_DIR, ARC_FNAME[:-7])):
        if not os.path.exists(os.path.join(DATA_DIR, ARC_FNAME)):
            logger.info("Downloading the data")
            download_archive()
        logger.info("Extracting the data")
        extract_archive()

    classes_dir = os.path.join(DATA_DIR, "classes_GS.csv")
    with open(classes_dir, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            json_fname = row[0].strip()[:-6]+"json"
            json_to_csv(json_fname, overwrite=False)
            logger.info("export: "+json_fname)

    logger.info("Cleaning up the data")
    cleanup_archive()


def cleanup_archive():
    files = ["instance", "tables", "property", "classes_GS.csv", ARC_FNAME]
    for f in files:
        d = os.path.join(DATA_DIR, f)
        if os.path.exists(d):
            if os.path.isdir(d):
                shutil.rmtree(d)
            else:
                os.remove(d)


def download_archive():
    url = "http://webdatacommons.org/webtables/extended_instance_goldstandard.tar.gz"
    r = requests.get(url)
    arc_dir = os.path.join(DATA_DIR, ARC_FNAME)
    with open(arc_dir, 'wb') as f:
        f.write(r.content)


def extract_archive():
    arc_dir = os.path.join(DATA_DIR, ARC_FNAME)
    tar = tarfile.open(arc_dir, "r:gz")
    tar.extractall(path=DATA_DIR)
    tar.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        DATA_DIR = sys.argv[1]
        DEST_DIR = os.path.join(DATA_DIR, "T2Dv2")
        export_files_to_csv()
    else:
        print("Specify the destination directory")
