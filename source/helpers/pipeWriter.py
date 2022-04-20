
def addRegister(register:str):
    try:
        with open('../pipe1', 'a') as f:
            f.write(register)
    except IOError:
        print('error'*10)
    