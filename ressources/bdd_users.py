import sqlite3

conn = sqlite3.connect('ressources/bdd_all.db')
cursor = conn.cursor()
conn.close()