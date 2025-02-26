import os
import csv
import hashlib


path = os.path.dirname(__file__)

name_main = "Meca'stuff"

bg_color = "#062332"
ctrl_color = "#BD3014"
label_color = "#BD3014"

def create_account(username, password, name, firstname, mail, tel, admin):
    f = open(path+"/users.csv", "a")
    hash = hashlib.sha256(password.encode()).hexdigest()
    f.write(f"{username};{hash};{name};{firstname};{mail};{tel};{admin};\n")
    f.close()
