import hashlib
import string

def hashit(stri):
    for i in range(0, 500000):
        stri = hashlib.sha224(stri).hexdigest()
    return stri