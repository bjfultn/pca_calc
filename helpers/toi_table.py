
def default_columns():
    """ The default columns that should be shown
    """
    return {
        'TOI': [
            "toi_cand",
        ]
    }


def display_fields():
    """ Columns that we want to allow the user to select as a persistent option in thier settings
    """
    columns = table_columns()
    for col in fields_not_selectable():
        del columns[col]
    return columns


def fields_not_selectable():
    """ Columns that are hidden from user settings or
        columns as hidden search fields on the tabulator
    """
    return []


def table_columns():
    """ The complete list of columns for the stars_table.
        Also includes simple display text for settings selection only.
    """
    return {
        'toi_cand': 'TOI <span>Number</span>',
        'n_toi': 'N <span>TOIs</span>',
        'per': "Orbital Period",
        'per_err': "Orbital Period Error",
        'epoch': "Transit Epoch",
        'rp': "Planet Radius",
        'mp': "Expected Mass",
        "sinc": "Incident Flux",
        "kexp": "Expected K",
        "pipeline": "Detection Pipeline",
        "disp": "Disposition",
        "tks_comments": "TKS Notes",
        "public_comments": "TFOP Notes"
    }
