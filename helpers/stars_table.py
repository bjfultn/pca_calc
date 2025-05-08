import helpers.star
from db.models import Star


def data(request, program_slug = None):
    # Start with an empty queryset
    stars = Star.objects.none()

    # Update session var with a program selected from the menu by the user
    if program_slug:
        request.session['program_filter'] = program_slug
    elif request.GET.get("program"):
        request.session['program_filter'] = request.GET.get("program")

    # Default to "All" if the session is new or the user is not subscribed to the program
    if 'program_filter' in request.session and request.user.is_subscribed(request.session['program_filter']):
        program_filter = request.session['program_filter']
    else:
        program_filter = "All"
        program_name = "All Stars"

    # Populate the stars queryset from programs
    for program in request.user.programs.all():
        if program_filter == "All":
            stars = stars | program.stars.all()
            program_name = "All Stars"
        elif program_filter == program.url_slug():
            stars = program.stars.all()
            program_name = program.name

    # If the user is admin show all the stars
    if program_filter == "All" and request.user.is_staff:
        stars = Star.objects.all()
        program_name = "All Stars"

    requested_columns = request.user.settings().get('stars_table_columns', default_columns())

    # Calculate requested columns
    if stars.count() > 0:
        stars = helpers.star.add_columns(stars, requested_columns).to_dict('records')

    return {
        'program_filter': program_filter,
        'program_name': program_name,
        'stars': stars,
    }


def default_columns():
    """ The default columns that should be shown
    """
    return {
        'Star': [
            "name",
            "ra",
            "dec",
            "vmag",
            "num_nights",
            "last_observed",
            "last_comment",
            "num_nights_hires_j",
            "num_nights_apf",
            "last_observed_hires_j",
            "last_observed_apf"
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
    return ["name", "othernames", "program_list", "comment_list"]


def table_columns():
    """ The complete list of columns for the stars_table.
        Also includes simple display text for settings selection only.
    """
    return {
                         "name": "Name",
                          "toi": "TOI <span>link</span>",
                       "ticnum": "TIC <span>link</span>",
                         "vmag": "V <span>mag</span>",
                           "ra": "RA <span>hr</span>",
                          "dec": "Dec <span>deg</span>",
                      "bvcolor": "B-V <span>mag</span>",
                        "prlax": "Parallax <span>arcsec</span>",
                     "distance": "Distance <span>pc</span>",
                         "teff": "Teff <span>K</span>",
                         "logg": "Logg",
                          "feh": "Fe/H",
                        "vsini": "Vsini",
                       "svalue": "S HK",
                       "logrhk": "LogR'HK",
                         "mass": "Mass <span>Msun</span>",
                       "radius": "Radius <span>Rsun</span>",
        "num_nights": "N <span>obs</span>",
           "num_nights_hires_j": "N Keck <span>obs</span>",
               "num_nights_apf": "N APF <span>obs</span>",
                "last_observed": "Last Obs <span>days</span>",
        "last_observed_hires_j": "Last Keck Obs <span>days</span>",
            "last_observed_apf": "Last APF Obs <span>days</span>",
                 "last_comment": "Last Cmnt <span>days</span>",
                   "othernames": "Alt Names",
                 "program_list": "Programs",
                 "comment_list": "Comments",
                 "num_comments": "N Comments",
                    'texp_keck': 'HIRES exposure time',
                     'texp_apf': 'APF exposure time',
        'total_exptime_hires_j': 'Total HIRES exposure time',
            'total_exptime_apf': 'Total APF exposure time',
        'have_template_hires_j': 'Have HIRES template?',
            'have_template_apf': 'Have APF template?'
    }
