
def compare_versions(a,b):
    """return -1 if a<b, 0 if a==b and 1 if a>b"""
    while a.count('.') < 2:
        a += '.0'
    while b.count('.') < 2:
        b += '.0'
    to_compare = zip(a.replace('v','').split('.'),b.replace('v','').split('.'))

    for i,j in to_compare:
        if i<j:
            return -1
        elif i>j:
            return 1
        else:
            continue
    else:
        return 0

def update_version(old_version):
    #TODO
    return old_version
