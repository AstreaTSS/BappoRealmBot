import threading, realm, advert

t1 = threading.Thread(target=realm.run) 
t2 = threading.Thread(target=advert.run) 

t1.start()
t2.start()