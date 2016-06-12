def wandoujiaFilter(url):
    fields = url.split('/')
    return not isWandoujiaPackage(fields[-1])

def isWandoujiaPackage(name):
    fields = name.split('.')
    return len(fields) > 1 and name.find('?') < 0 and name.find('=') < 0

def filter360(url):
    fields = url.split('/')
    try:
        int(fields[-1])
        return False
    except:
        return True


def getPersistFilter(task):
    if task == 'wandoujia':
        return wandoujiaFilter
    elif task == '360':
        return filter360
