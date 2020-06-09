
def add_value_to_dict(dico,key,val):
    if key in dico.keys():
        dico[key] = dico[key] + val
    else:
        dico[key] = val

def next_year(timestamp):
    return timestamp + 365*24*3600

def next_month(timestamp):
    return timestamp + 30*24*3600

def step_months_if_needed(before, now, old_alters, by_month):

def new_alters_by_month(ego, csvobj):
    """
    je fais pas l'ouverture du fichier etc.,
    faudra ajouter tout le début ou changer le nom de la fonction
    """
    header = next(csvobj)
    first_row = next(csvobj)
    before = int(first_row[2])
    nb_new = 0
    by_month = {}
    for row in csvobj:
        idr,timestamp = row[0],int(row[2])
        if idr not in alters:
            alters[idr] = timestamp
            nb_new += 1
            dt = datetime.fromtimestamp(timestamp)
            month_year = ( dt.month, dt.year)
            month_next_year = ( dt.month, dt.year + 1)
            add_value_to_dict(old_alters, month_next_year, 1)

            # step months if needed
            while before < timestamp:
                dt = datetime.fromtimestamp(before)
                month_year = (dt.month, dt.year)
                if month_year in old_alters:
                    nb_new -= old_alters[month_year]
                by_month[month_year] = nb_new
                before = next_month(before)

#
