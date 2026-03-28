from bcrypt import checkpw, hashpw, gensalt

def generate_hash(password):
    password = password.encode('utf-8')
    return hashpw(password, gensalt(10)).decode('utf-8')

def verify_hash(password, hash):
    password = password.encode('utf-8')
    hash = hash.encode('utf-8')
    return checkpw(password, hash)
