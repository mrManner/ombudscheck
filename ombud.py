#! python3

import csv
import argparse
import requests
from bs4 import BeautifulSoup as bs

def getgroup(p):
    if p['Huvudkar'] == 'Ja':
        # Get group from Scoutnet
        p['Representerar'] = scrape(p['Medlemsnummer'])
        p['Bra gissning'] = True
        return p
    elif p['Annankar'] != '':
        p['Representerar'] = p['Annankar']
        p['Bra gissning'] = True
        return p
    else:
        # This p has not indicated any group, so we guess 
        # they represent their main group but mark them for reference
        p['Representerar'] = scrape(p['Medlemsnummer'])
        p['Bra gissning'] = False
        return p
    pass

def scrape(num):
    pass

parser = argparse.ArgumentParser()
parser.add_argument("file", help="The csv export file from Scoutnet")
parser.add_argument("-u", "--username", required=True,
        help="Membership number or email address of Scoutnet user")
parser.add_argument("-p", "--password", required=True,
        help="Password of Scoutnet user")
args = parser.parse_args()

file = open(args.file, 'r')
reader = csv.DictReader(file, delimiter=';')

print([getgroup(p) for p in reader if 'Ombud' in p['Deltagaralternativ']])
