import sqlite3

conn = sqlite3.connect("bdd_all.db")
cursor = conn.cursor()

# Vérifier si la table existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
table_exists = cursor.fetchone()

if table_exists:
    print("✅ La table 'users' existe bien.")
else:
    print("❌ La table 'users' n'existe pas !")

conn.close()
