from db.models import Star, Program
import helpers.star
import helpers.stars_table
import helpers.toi_table
import helpers.tic_table
import helpers.program_table


def data(request):
    data = []
    stars = Star.objects.none()
    for program in programs():
        stars = stars | program.stars.all()

    requested_columns = user_columns(request.user)

    # Calculate requested columns using a DICT
    if stars.count() > 0:
        data = helpers.star.add_columns(stars, requested_columns)
        data = data.to_dict('records')

    return data


def default_programs():
    return ["TKS", "TESS"]

def user_columns(user):
    sorted_columns = {}
    user_columns = user.data.get('candidates_table_columns', default_columns())
    for table_name in display_fields().keys():
        sorted_columns[table_name] = user_columns[table_name]
    return sorted_columns

def programs():
    temp_programs = default_programs()
    programs = Program.objects.filter(name__in=temp_programs)
    # programs = Program.objects.filter(name__icontains='TKS') | \
    #            Program.objects.filter(name__icontains='TESS')

    return programs

def default_columns():
    """ The default columns that should be shown
    """
    columns = {}
    columns.update(helpers.stars_table.default_columns())
    columns.update(helpers.tic_table.default_columns())
    columns.update(helpers.toi_table.default_columns())
    columns.update(helpers.program_table.default_columns())
    return columns


def display_fields():
    """ Candidates table columns/fields that we want to allow the user to select
        This list must merge all the different table display_fields together
    """
    columns = {}
    columns['Star'] = helpers.stars_table.display_fields()
    columns['TIC'] = helpers.tic_table.display_fields()
    columns['TOI'] = helpers.toi_table.display_fields()
    columns['Program'] = helpers.program_table.display_fields()
    return columns


def table_columns():
    """ The complete list of columns and display text
        This list must merge all the different table columns together
    """
    columns = {}
    columns.update(helpers.stars_table.table_columns())
    columns.update(helpers.tic_table.table_columns())
    columns.update(helpers.toi_table.table_columns())
    return columns
