def find_first(l, predicate):
    return next((item for item in l if predicate(item)), None)
