import random
import string

def code_gen(length=6):
    characters = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(characters, k=length))
    return code