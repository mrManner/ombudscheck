#! python3

import csv
import time
import sys
import argparse
import requests
from bs4 import BeautifulSoup as bs


def getgroup(p, s):
    if p['maingroup'] == 'Ja':
        # Get group from Scoutnet
        p['Representerar'] = scrape(p['Medlemsnummer'], s)
        p['Representerar: Bra gissning'] = 'Ja'
        p['Anmält ombud för huvudkår'] = p['maingroup']
        p['Anmält ombud för annan kår'] = p['othergroup']
        p['Deltagaralternativ'] = p['participation']
        return p
    elif p['othergroup'] != '':
        p['Representerar'] = p['othergroup']
        p['Representerar: Bra gissning'] = 'Ja'
        p['Anmält ombud för huvudkår'] = p['maingroup']
        p['Anmält ombud för annan kår'] = p['othergroup']
        p['Deltagaralternativ'] = p['participation']
        return p
    else:
        # This p has not indicated any group, so we guess
        # they represent their main group but mark them for reference
        p['Representerar'] = scrape(p['Medlemsnummer'], s)
        p['Representerar: Bra gissning'] = 'Nej'
        p['Anmält ombud för huvudkår'] = p['maingroup']
        p['Anmält ombud för annan kår'] = p['othergroup']
        p['Deltagaralternativ'] = p['participation']
        return p
    pass


def scrape(num, session):
    r = session.get('https://www.scoutnet.se/organisation/user/' + str(num))
    if r.status_code != 200:
        raise UserNotFoundError
    else:
        time.sleep(.01)
        soup = bs(r.content, 'html.parser')
        # Get all groups for counting
        grouplist = soup.find(class_="membership_list").ul.find_all(groupmember)
        if len(grouplist) > 1:
            # The only way the primary group is marked is using this image
            ret = soup.find("img", class_="primary").previous_element
            soup.decompose()
            return ret
        else:
            # If there's only one group it doesn't count as primary...
            ret = soup.find(class_="membership_info").find('img').next_element
            soup.decompose()
            return ret

def groupmember(tag):
    if tag.has_attr('id'):
        return 'user_membership_group' in tag['id']
    else:
        return False

class UserNotFoundError(Exception):
    pass


def scoutnet_login(user, password):
    # returns a Requests session with a Scoutnet login
    s = requests.Session()
    credentials = {'signin[username]': user, 'signin[password]': password}
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


# Fix the fieldnames for writing
fieldnames = []
fieldnames.append('Medlemsnummer')
fieldnames.append('Medlemsstatus')
fieldnames.append('Namn')
fieldnames.append('Kön')
fieldnames.append('Födelsedatum')
fieldnames.append('Personnummer')
fieldnames.append('Organisation')
fieldnames.append('Distrikt')
fieldnames.append('Samverksansorganisation')
fieldnames.append('Kår')
fieldnames.append('E-post')
fieldnames.append('Adress')
fieldnames.append('Telefonnummer')
fieldnames.append('Registrerad')
fieldnames.append('Deltagaralternativ')
fieldnames.append('Anmält ombud för huvudkår')
fieldnames.append('Anmält ombud för annan kår')
fieldnames.append('Ombudsgrupp')
fieldnames.append('Stämmopatrull')
fieldnames.append('Representerar')
fieldnames.append('Representerar: Bra gissning')

writer = csv.DictWriter(sys.stdout, fieldnames = fieldnames,
        extrasaction = 'ignore', dialect='excel', delimiter=';', quotechar='"')


writer.writeheader()
for row in [getgroup(p, session) for p in reader if 'Ombud' in p['participation']]:
    writer.writerow(row)

