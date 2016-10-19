#! python3

import csv
import argparse
import requests
from bs4 import BeautifulSoup as bs

parser = argparse.ArgumentParser()
parser.add_argument("file", help="The csv export file from Scoutnet")
parser.add_argument("-u", "--username", required=True,
        help="Membership number or email address of Scoutnet user")
parser.add_argument("-p", "--password", required=True,
        help="Password of Scoutnet user")
args = parser.parse_args()

file = open(args.file, 'r')
reader = csv.DictReader(file, delimiter=';')
