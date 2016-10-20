#! python3

import csv
import sys
import argparse
import requests
from bs4 import BeautifulSoup as bs


def getgroup(p, s):
    if p['maingroup'] == 'Ja':
        # Get group from Scoutnet
        p['Representerar'] = scrape(p['Medlemsnummer'], s)
        p['Bra gissning'] = True
        return p
    elif p['othergroup'] != '':
        p['Representerar'] = p['othergroup']
        p['Bra gissning'] = True
        return p
    else:
        # This p has not indicated any group, so we guess
        # they represent their main group but mark them for reference
        p['Representerar'] = scrape(p['Medlemsnummer'], s)
        p['Bra gissning'] = False
        return p
    pass


def scrape(num, session):
    r = session.get('https://www.scoutnet.se/organisation/user/' + str(num))
    soup = bs(r.content, 'html.parser')
    # Get all groups for counting
    grouplist = soup.find(class_="membership_list").ul.find_all(
            class_="membershiplist_item")
    if len(grouplist) > 1:
        # The only way the primary group is marked is using this image
        return soup.find("img", class_="primary").previous_element
    else:
        # If there's only one group it doesn't count as primary...
        return soup.find(class_="membershiplist_item").h4.content


def scoutnet_login(user, password):
    # returns a Requests session with a Scoutnet login
    s = requests.Session()
    credentials = {'signin[username]': user, 'signin[password]': password}
    print(credentials)
    r = s.post('https://www.scoutnet.se/login', data=credentials)
    if r.status_code == 200:
        return s
    else:
        raise LoginError(r.status_code)


class LoginError(Exception):
    pass


parser = argparse.ArgumentParser()
parser.add_argument("file", help="The csv export file from Scoutnet")
parser.add_argument("-u", "--username", required=True,
                    help="Membership number or email address of Scoutnet user")
parser.add_argument("-p", "--password", required=True,
                    help="Password of Scoutnet user")
args = parser.parse_args()

session = scoutnet_login(args.username, args.password)
file = open(args.file, 'r')
reader = csv.DictReader(file)

# Fix up the reader a bit
reader.fieldnames[23] = 'participation' # Do they represent anyone? If so:
reader.fieldnames[24] = 'maingroup'     # Do they represent their main group...
reader.fieldnames[25] = 'othergroup'    # ...or another?

#print(reader.fieldnames)
result = ([getgroup(p, session) for p in reader if 'Ombud' in p['participation']])

reader.fieldnames.append('Bra gissning')
reader.fieldnames.append('Representerar')
writer = csv.DictWriter(sys.stdout, fieldnames = reader.fieldnames)
writer.writerows(result)
