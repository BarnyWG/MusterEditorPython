# '''
# funktionen für MusterEditor
# ausgelagert Fremdcode
# '''


def bytes2int(b):
    res = 0
    for x in b[::-1]:
        res = (res << 8) + x
    return res
