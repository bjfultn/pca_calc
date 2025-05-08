"""
Helper functions to calculate columns for the stars table.
All helper functions must return a query set with an added column that has
the same name as the function name.
"""

import logging
import pandas as pd

from django.db.models import Case, When, Q, F, Avg, Count, Min, Sum, FloatField, IntegerField, Func, Aggregate, Prefetch, Value, CharField
from django.db.models.functions import TruncDate, Now, ExtractDay, Replace, Coalesce, Concat
from django.db import models
from django.core.exceptions import FieldError

from django.apps import apps

EXOFOP_URL = 'https://exofop.ipac.caltech.edu/tess/target.php'

def safe_division(n, d):
    return n / d if d else 0

def get_model_columns(model):
    """Get list of columns that already exist in a model ignoring ForeinKey and similar connections

    Args:
        model (Django table model): Django table object

    Returns:
        list

    """

    model_columns = [f.name for f in model._meta.fields if not isinstance(f, (models.fields.AutoField,
                                                                              models.OneToOneField,
                                                                              models.ManyToManyField))]
    print(model_columns)

    return model_columns


class DiffDays(Func):
    function = 'DATE_PART'
    template = "%(function)s('day', %(expressions)s)"


class CastDate(Func):
    function = 'date_trunc'
    template = "%(function)s('day', %(expressions)s)"


class Median(Aggregate):
    function = 'PERCENTILE_CONT'
    name = 'median'
    output_field = FloatField()
    template = '%(function)s(0.5) WITHIN GROUP (ORDER BY %(expressions)s)'


class RoundInt(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s::numeric, 0)"


class ListConcat(Aggregate):
    function = 'string_agg'
    template = "%(function)s(%(distinct)s%(expressions)s, '%(separator)s')"

    def __init__(self, expression, distinct=False, separator=None, **extra):
        super(ListConcat, self).__init__(
            expression,
            distinct='DISTINCT ' if distinct else '',
            separator=separator or ' ',
            output_field=CharField(),
            **extra)


class NullIfnan(Func):
    template = "NULLIF(%(expressions)s, 'nan')"


class AbsoluteSum(Sum):
    name = 'AbsoluteSum'
    template = '%(function)s(%(absolute)s(%(expressions)s))'

    def __init__(self, expression, **extra):
        super(AbsoluteSum, self).__init__(
            expression, absolute='ABS ', output_field=IntegerField(), **extra)

    def __repr__(self):
        return "SUM(ABS(%s))".format(
            self.arg_joiner.join(str(arg) for arg in self.source_expressions)
        )


def num_nights(stars):
    query = stars.annotate(date=TruncDate('observations__utctime')) \
                 .values('date', 'name') \
                 .annotate(c=Count('date', distinct=True)) \
                 .values('name') \
                 .annotate(num_nights=Count('date', distinct=True, output_field=FloatField()))

    return query


def num_nights_hires_j(stars):
    query = stars.filter(observations__instrument='hires_j') \
                 .annotate(date=TruncDate('observations__utctime')) \
                 .values('date', 'name') \
                 .annotate(c=Count('date', distinct=True)) \
                 .values('name') \
                 .annotate(num_nights_hires_j=Count('date', distinct=True, output_field=FloatField()))

    return query


def num_nights_apf(stars):
    query = stars.filter(observations__instrument='apf') \
                 .annotate(date=TruncDate('observations__utctime')) \
                 .values('date', 'name') \
                 .annotate(c=Count('date', distinct=True)) \
                 .values('name') \
                 .annotate(num_nights_apf=Count('date', distinct=True, output_field=FloatField()))

    return query


def last_observed(stars):
    query = stars.annotate(now=Now()) \
                 .annotate(dt=DiffDays(CastDate(F('now')) - CastDate(F('observations__utctime')))) \
                 .values('name') \
                 .annotate(last_observed=Min('dt'))

    return query


def last_observed_hires_j(stars):
    query = stars.filter(observations__instrument='hires_j') \
                 .annotate(now=Now()) \
                 .annotate(dt=DiffDays(CastDate(F('now')) - CastDate(F('observations__utctime')))) \
                 .values('name') \
                 .annotate(last_observed_hires_j=Min('dt'))

    return query


def last_observed_apf(stars):
    query = stars.filter(observations__instrument='apf') \
                 .annotate(now=Now()) \
                 .annotate(dt=DiffDays(CastDate(F('now')) - CastDate(F('observations__utctime')))) \
                 .values('name') \
                 .annotate(last_observed_apf=Min('dt'))

    return query


def last_comment(stars):
    query = stars.annotate(now=Now()) \
                 .annotate(dc=DiffDays(CastDate(F('now')) - CastDate(F('comments__submit_date')))) \
                 .values('name') \
                 .annotate(last_comment=Min('dc'))

    return query


def have_template_hires_j(stars):
    query = stars.filter(observations__instrument='hires_j') \
                 .annotate(num_templates=Count('observations__rvs_hires_j__dsst_obs')) \
                 .annotate(have_template_hires_j=Case(When(num_templates__gt=0,
                                                           then=Value(1)),
                                                      default=Value(0),
                                                      output_field=IntegerField())) \
                 .values('name', have_template_hires_j=F('have_template_hires_j'))

    return query


def have_template_apf(stars):
    query = stars.filter(observations__instrument='apf') \
                 .annotate(num_templates=Count('observations__rvs_apf__dsst_obs')) \
                 .annotate(have_template_apf=Case(When(num_templates__gt=0,
                                                       then=Value(1)),
                                                  default=Value(0),
                                                  output_field=IntegerField())) \
                 .values('name', have_template_apf=F('have_template_apf'))

    return query


def total_exptime_hires_j(stars):

    query = stars.values('name') \
                 .annotate(total_exptime_hires_j=Sum('observations__metadata_hires_j__exposure_time')/3600.) \


    return query


def total_exptime_apf(stars):

    query = stars.values('name') \
                 .annotate(total_exptime_apf=Sum('observations__metadata_apf__exposure_time')/3600.)

    return query


def num_comments(stars):
    query = stars.values('name') \
                 .annotate(num_comments=Count('comments__comment'))

    return query


def program_list(stars):
    star_names = stars.values_list('name')
    model = apps.get_model(app_label='db', model_name='Star')
    istars = model.objects.filter(name__in=star_names)
    query = istars.values('name') \
                  .annotate(program_list=Case(When(programs__name__isnull=False, then=ListConcat('programs__name', separator=', ')),
                                                   default=Value(''))
                            )

    return query


def comment_list(stars):
    query = stars.values('name') \
                 .annotate(comment_list=ListConcat('comments__comment', separator=', '))

    return query


def othernames(stars):
    query = stars.values('name') \
                 .annotate(othernames=Replace(Replace('simbad__simbad_othernames',
                                                      Value('|'), Value(',')),
                                              Value(' '), Value('')))

    return query


def distance(stars):
    query = stars.values('name') \
                 .annotate(distance=Case(When(prlax__lte=0, then=0),
                                         default=1/F('prlax')))

    return query


def teff(stars):
    backup_order = [Median('observations__smemp_hires_j__teff'),
                    Median('observations__smsyn_hires_j__teff'),
                    Median('observations__smsyn_apf__teff')]

    query = stars.values('name') \
                 .annotate(teff=Coalesce(*backup_order))

    return query


def logg(stars):
    backup_order = [Median('observations__smsyn_hires_j__logg'),
                    Median('observations__smsyn_apf__logg')]

    query = stars.values('name') \
                 .annotate(logg=Coalesce(*backup_order))

    return query


def feh(stars):
    backup_order = [Median('observations__smemp_hires_j__fe'),
                    Median('observations__smsyn_hires_j__fe'),
                    Median('observations__smsyn_apf__fe')]

    query = stars.values('name') \
                 .annotate(feh=Coalesce(*backup_order))

    return query


def vsini(stars):
    backup_order = [Median('observations__smsyn_hires_j__vsini'),
                    Median('observations__smsyn_apf__vsini')]

    query = stars.values('name') \
                 .annotate(vsini=Coalesce(*backup_order))

    return query


def mass(stars):
    backup_order = [Median('observations__smsyn_hires_j__mass'),
                    Median('observations__smsyn_apf__mass')]

    query = stars.values('name') \
                 .annotate(mass=Coalesce(*backup_order))

    return query


def radius(stars):
    backup_order = [Median('observations__smemp_hires_j__radius'),
                    Median('observations__smsyn_hires_j__radius'),
                    Median('observations__smsyn_apf__radius')]

    query = stars.values('name') \
                 .annotate(radius=Coalesce(*backup_order))

    return query


def logrhk(stars):
    backup_order = [Median('observations__svals_hires_j__logrhk'),
                    Median('observations__svals_apf__logrhk')]

    query = stars.values('name') \
                 .annotate(logrhk=Coalesce(*backup_order))

    return query


def svalue(stars):
    backup_order = [Median('observations__svals_hires_j__svalue'),
                    Median('observations__svals_apf__svalue')]

    query = stars.values('name') \
                 .annotate(svalue=Coalesce(*backup_order))

    return query


def toi(stars):
    query = stars.values('name', toi=F('tic__toi'))

    return query


def ticnum(stars):
    query = stars.values('name', ticnum=F('tic__tic'))

    return query


def n_toi(stars):
    query = stars.values('star__name') \
                 .annotate(n_toi=Count('toi_cand')) \
                 .values(star_id=F('star_id'), n_toi=F('n_toi'))

    return query


def in_tks(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks=Case(When(Q(program_list__contains='TKS') & ~Q(program_list__contains='TKS - Drop'),
                                            then=Value(1)),
                                       default=Value(0),
                                       output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks=F('in_tks'))

    return query


def in_tks_drop(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_drop=Case(When(program_list__contains='TKS - Drop',
                                                 then=Value(1)),
                                            default=Value(0),
                                            output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_drop=F('in_tks_drop'))

    return query


def num_tks(stars):
    star_names = stars.values_list('name')
    model = apps.get_model(app_label='db', model_name='Star')
    search_programs = ['TKS - SC1A - Radius Gap',
                       'TKS - SC1B - Flux/Envelopes',
                       'TKS - SC1C - USPs',
                       'TKS - SC1D - HZ',
                       'TKS - SC1E - Comp/Stellar',
                       'TKS - SC2A - Distant Giants',
                       'TKS - SC2Bi - Eccentricity',
                       'TKS - SC2Bii - Obliquity',
                       'TKS - SC2C - Multis',
                       'TKS - SC3 - Atmospheres',
                       'TKS - TOA - Stellar Catalog',
                       'TKS - TOB - Doppler Noise',
                       'TKS - Evolved Stars']

    istars = model.objects.filter(name__in=star_names)
    query = istars.filter(programs__name__in=search_programs) \
                  .annotate(num_tks=Count('programs__name')) \
                  .values('name', star_id=F('name'), num_tks=F('num_tks'))

    return query


def in_tks_sc1a(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_sc1a=Case(When(program_list__contains='TKS - SC1A ',
                                                 then=Value(1)),
                                            default=Value(0),
                                            output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_sc1a=F('in_tks_sc1a'))

    return query


def in_tks_sc1b(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_sc1b=Case(When(program_list__contains='TKS - SC1B ',
                                                 then=Value(1)),
                                            default=Value(0),
                                            output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_sc1b=F('in_tks_sc1b'))

    return query


def in_tks_sc1c(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_sc1c=Case(When(program_list__contains='TKS - SC1C ',
                                                 then=Value(1)),
                                            default=Value(0),
                                            output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_sc1c=F('in_tks_sc1c'))

    return query


def in_tks_sc1d(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_sc1d=Case(When(program_list__contains='TKS - SC1D ',
                                                 then=Value(1)),
                                            default=Value(0),
                                            output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_sc1d=F('in_tks_sc1d'))

    return query


def in_tks_sc1e(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_sc1e=Case(When(program_list__contains='TKS - SC1E ',
                                                 then=Value(1)),
                                            default=Value(0),
                                            output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_sc1e=F('in_tks_sc1e'))

    return query


def in_tks_sc2a(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_sc2a=Case(When(program_list__contains='TKS - SC2A ',
                                                 then=Value(1)),
                                            default=Value(0),
                                            output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_sc2a=F('in_tks_sc2a'))

    return query


def in_tks_sc2bi(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_sc2bi=Case(When(program_list__contains='TKS - SC2Bi ',
                                                 then=Value(1)),
                                              default=Value(0),
                                              output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_sc2bi=F('in_tks_sc2bi'))

    return query


def in_tks_sc2bii(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_sc2bii=Case(When(program_list__contains='TKS - SC2Bii ',
                                                 then=Value(1)),
                                              default=Value(0),
                                              output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_sc2bii=F('in_tks_sc2bii'))

    return query


def in_tks_sc2c(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_sc2c=Case(When(program_list__contains='TKS - SC2C ',
                                                 then=Value(1)),
                                            default=Value(0),
                                            output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_sc2c=F('in_tks_sc2c'))

    return query


def in_tks_sc3(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_sc3=Case(When(program_list__contains='TKS - SC3 ',
                                                 then=Value(1)),
                                           default=Value(0),
                                           output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_sc3=F('in_tks_sc3'))

    return query


def in_tks_toa(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_toa=Case(When(program_list__contains='TKS - TOA ',
                                                 then=Value(1)),
                                           default=Value(0),
                                           output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_toa=F('in_tks_toa'))

    return query


def in_tks_tob(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_tob=Case(When(program_list__contains='TKS - TOB ',
                                                 then=Value(1)),
                                           default=Value(0),
                                           output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_tob=F('in_tks_tob'))

    return query


def in_tks_evol(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_evol=Case(When(program_list__contains='TKS - Evolved ',
                                                 then=Value(1)),
                                            default=Value(0),
                                            output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_evol=F('in_tks_evol'))

    return query


def in_tks_ash(stars):
    stars = program_list(stars)
    query = stars.annotate(in_tks_ash=Case(When(program_list__contains='Ashley Thesis',
                                                 then=Value(1)),
                                           default=Value(0),
                                           output_field=IntegerField())) \
                 .values('name', star_id=F('name'), in_tks_ash=F('in_tks_ash'))

    return query


def texp_keck(stars, table='Star'):
    backup_order = ['vmag',
                    'simbad__simbad_v_mag',
                    'tic__tic_vmag',
                    'tic__tic_tmag',
                    'simbad__simbad_g_mag']

    # need to make these importable from cpsutils
    exp1 = 110
    v1 = 8.0
    c1 = 250
    iod_slow = 1.4

    if table == 'TIC':
        prefix = 'star__'
        exp_field = 'exp_keck'
        name_field = 'star_id'
    else:
        prefix = ''
        exp_field = 'tic__exp_keck'
        name_field = 'name'

    new_backups = []
    for col in backup_order:
        with_nulls = col+'_null'
        new_backups.append(F(with_nulls))
        ano = {with_nulls: NullIfnan(prefix+col)}
        stars = stars.annotate(**ano)

    query = stars.values(name_field) \
                 .annotate(vmag_backup=Coalesce(*new_backups), counts=F(exp_field)) \
                 .annotate(texp_keck=iod_slow*(F('counts')*exp1)/(c1*10**(-0.4*(F('vmag_backup')-v1))))

    return query


def texp_apf(stars, table='Star'):
    backup_order = ['vmag',
                    'simbad__simbad_v_mag',
                    'tic__tic_vmag',
                    'tic__tic_tmag',
                    'simbad__simbad_g_mag']

    # need to make these importable from cpsutils
    m1 = 22.9
    iod_slow = 1.4

    if table == 'TIC':
        prefix = 'star__'
        exp_field = 'exp_apf'
        name_field = 'star_id'
    else:
        prefix = ''
        exp_field = 'tic__exp_apf'
        name_field = 'name'

    new_backups = []
    for col in backup_order:
        with_nulls = col+'_null'
        new_backups.append(F(with_nulls))
        ano = {with_nulls: NullIfnan(prefix+col)}
        stars = stars.annotate(**ano)

    query = stars.values(name_field) \
                 .annotate(vmag_backup=Coalesce(*new_backups), counts=F(exp_field)*1e9) \
                 .annotate(texp_apf=iod_slow*F('counts')/(10**((m1 - F('vmag_backup'))/2.5)))

    return query


def remaining_nobs_keck(stars):
    stars = stars.filter(star__observations__instrument='hires_j') \
                 .annotate(date=TruncDate('star__observations__utctime')) \
                 .values('date', 'star_id') \
                 .annotate(c=Count('date', distinct=True)) \
                 .values('star_id') \
                 .annotate(num_nights_hires_j=Count('date', distinct=True, output_field=FloatField()))

    query = stars.annotate(remaining_nobs_keck=F('nobs_goal_keck')-F('num_nights_hires_j'))

    return query


def remaining_nobs_apf(stars):
    stars = stars.filter(star__observations__instrument='apf') \
                 .annotate(date=TruncDate('star__observations__utctime')) \
                 .values('date', 'star_id') \
                 .annotate(c=Count('date', distinct=True)) \
                 .values('star_id') \
                 .annotate(num_nights_apf=Count('date', distinct=True, output_field=FloatField()))

    query = stars.annotate(remaining_nobs_apf=F('nobs_goal_apf')-F('num_nights_apf'))

    return query


def remaining_texp_keck(stars):
    stars = texp_keck(stars, table='TIC')
    stars = remaining_nobs_keck(stars)

    query = stars.annotate(overhead=180*F('n_visits_night_keck') + 120+(F('n_shots_keck')-1)*45) \
                 .annotate(remaining_texp_keck=(F('overhead') + F('remaining_nobs_keck')*F('texp_keck'))/3600.)

    return query


def remaining_texp_apf(stars):
    stars = texp_apf(stars, table='TIC')
    stars = remaining_nobs_apf(stars)

    query = stars.annotate(overhead=180*F('n_visits_night_apf') + 120+(F('n_shots_apf')-1)*45) \
                 .annotate(remaining_texp_apf=(F('overhead') + F('remaining_nobs_apf')*F('texp_apf'))/3600.)

    return query
