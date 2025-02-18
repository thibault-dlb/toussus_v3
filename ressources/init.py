import os
import hashlib
path = os.path.dirname(os.path.realpath(__file__))

def init (username, mdp, nom, prénom, mail, tel, admin):
    f = open(path+"/users.csv", "a")
    password = hashlib.sha256(mdp.encode()).hexdigest()
    print (password)
    f.write(f"{username};{password};{nom};{prénom};{mail};{tel};{admin}")
    f.close()
    
init("thibault.dlb", "Epicier", "de Laubrière", "Thibault", "thibdelaub@outlook.fr", "0769145620", "True")


