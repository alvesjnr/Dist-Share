
def apply_minimun_version(project):
    project._version = 'v0.1'


def compare_versions(a,b):
    """return -1 if a<b, 0 if a==b and 1 if a>b"""
    a = a.replace('V','v')
    b = b.replace('V','v')
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
    
    """
        Update file to v0.3.1
    """
    if compare_versions(old_version._version,'v0.3.1') == -1:
        for copy in old_version.copies_manager.copies:
            if not hasattr(copy,'linked_file_license'):
                copy.linked_file_license = False
            if not hasattr(copy,'linked_file_license_path'):
                copy.linked_file_license_path = ''
        old_version._version = 'v0.3.1'

    return old_version
