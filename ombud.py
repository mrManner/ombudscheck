import os
import csv

file = open('dj.csv', 'r')
reader = csv.DictReader(file, delimiter=';')
rows = []

for row in reader:
    rows.append(row)

people = [p for row in rows if 'Ombud' in x['Deltagaralternativ']]
