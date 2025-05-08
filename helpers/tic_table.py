import helpers.star
from db.models import Star


def default_columns():
    """ The default columns that should be shown
    """
    return {
        'TIC': [
            "tic",
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
        'tic': 'TIC <span>Number</span>',
        'tic_tmag': 'T <span>mag</span>',
        'tic_vmag': 'V <span>mag</span>',
        'tic_smass': 'M <span>star</span>',
        'tic_sradius': 'R <span>star</span>',
        'tic_teff': 'Teff <span>K</span>',
        'rot_per': 'Rotation Period <span>days</span>',
        'ruwe': 'RUWE <span>days</span>',
        'ast_det': 'Astro. det. <span>prop.</span>',
        'evol': 'Evolution <span>state</span>',
        'priority': 'Priority',
        'vetting': 'Vetting <span>status</span>',
        'ao_vet': 'AO Vetting <span>status</span>',
        'hires_prv': 'Active on <span>HIRES</span>',
        'apf_prv': 'Active on <span>APF</span>',
        'hires_next_run_notes': 'HIRES <span>notes</span>',
        'prv_plan': 'PRV <span>plan</span>',
        'nobs_goal_keck': 'N obs goal <span>HIRES</span>',
        'min_cadence_keck': 'Min. cadence <span>HIRES</span>',
        'exp_keck': 'Exp. meter <span>HIRES</span>',
        'n_shots_keck': 'N shots per visit <span>HIRES</span>',
        'n_visits_night_keck': 'N visits per night <span>HIRES</span>',
        'remaining_nobs_keck': 'Remaining N obs. HIRES',
        'remaining_texp_keck': 'Remaining HIRES hours',
        'nobs_goal_apf': 'N obs. goal <span>APF</span>',
        'min_cadence_apf': 'Min. cadence <span>APF</span>',
        'exp_apf': 'Exp. meter <span>APF</span>',
        'n_shots_apf': 'N shots per visit <span>APF</span>',
        'n_visits_night_apf': 'N visits per night <span>HIRES</span>',
        'remaining_nobs_apf': 'Remaining N obs. APF',
        'remaining_texp_apf': 'Remaining APF hours',
    }
