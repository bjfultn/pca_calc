

import time
import logging
import pandas as pd
import numpy as np
import copy
from django.db.models import F, Avg, Count, Min, Sum, FloatField, Func, Aggregate, Prefetch, Value
from django.db.models.functions import TruncDate, Now, ExtractDay, Replace, Coalesce
from django.core.exceptions import FieldError
import db.models
from helpers import columns as cols
from helpers.columns import DiffDays, CastDate, Median, Concat
from django import template
from django.apps import apps
from django.db import models

register = template.Library()

@register.filter
def vmag_backup(vmag, star):
    try:
        if -10 < vmag < 30 and vmag != 0.0:
            return vmag
        for source in ['simbad_v_mag', 'simbad_g_mag']:
            if np.isnan(vmag) or vmag == -99.0 or vmag == 0.0:
                try:
                    vmag = star['simbad__' + source]
                except TypeError:
                    sbad = star.simbad.first()
                    if sbad is not None:
                        vmag = getattr(sbad, source)
                # logging.debug('Loaded V mag from {}: {}:{}'.format(source, star['name'], vmag))
                if np.isfinite(vmag):
                    return vmag
        return 99
    except TypeError:
        return 99


@register.filter
def ra_backup(ra, star):
    source = 'simbad__simbad_ra'

    if 0 <= ra <= 24:
        return ra
    else:
        ra = np.nan

    if np.isnan(ra):
        try:
            ra_split = star[source].split()
            ra = float(ra_split[0]) + float(ra_split[1])/60.
            # logging.debug('Loaded V mag from {}: {}:{}'.format(source, star['name'], vmag))
            if not np.isnan(ra):
                return ra
        except:
            pass

    return 99


def fill_vmag(stars, sdf):
    """Fill in missing vmag values with values from Simbad

    Args:
        stars (QuerySet): Stars from stars table
        sdf (DataFrame): DataFrame of stars table with columns added
    """

    cols = sdf.columns
    sb = stars.values('name', 'simbad__simbad_v_mag',
                              'simbad__simbad_g_mag',
                              'simbad__simbad_ra',
                              'simbad__simbad_dec',
                              'simbad__simbad_othernames',
                              'tic__tic_vmag',
                              'tic__tic_tmag')

    merged = pd.merge(sdf, pd.DataFrame(sb), how='left', left_on='Star_name', right_on='name', suffixes=['', '_sbad'])

    merged['Star_vmag'].replace(0, np.nan, inplace=True)

    for col in ['simbad__simbad_v_mag', 'tic__tic_vmag', 'simbad__simbad_g_mag', 'tic__tic_tmag']:
        try:
            merged['Star_vmag'].fillna(np.round(merged[col], 2), inplace=True)
        except TypeError:
            pass

    merged['Star_vmag'].replace(0, np.nan, inplace=True)

    merged = merged[cols]

    return merged


def add_columns(stars, column_dict):
    """
    Calculate aggregate statistics on stars queryset and add as a column.
    Only available for specifically implemented column names.

    Args:
        stars (QuerySet): QuerySet of Star objects
        column_dict (dictionary): dict of column table names (keys) and column names (values) to calculate.
    """

    colmapper = cols.__dict__


    if isinstance(stars, list):
        qlist = [star.name for star in stars]
        stars = qlist

    merged = pd.DataFrame(stars.values())
    star_names = merged['name'].values

    # start with Star table to make sure we have the star name in there
    table = 'Star'
    input_query = stars
    column_list = column_dict[table]
    hidden_columns = ['program_list', 'comment_list', 'othernames', 'url_slug']
    column_list.extend(hidden_columns)
    available_columns = merged.columns
    for column in column_list:
        t1 = time.time()

        if column in available_columns:
            continue
        if column not in colmapper.keys():
            logging.debug("Column calculation function for {} not defined".format(column))
            return merged

        query = colmapper[column](input_query)

        t2 = time.time()
        logging.debug("Calculated {} for {} stars in {:.4f} s".format(column, stars.count(), t2 - t1))

        if query.count() > 0:
            qf = pd.DataFrame(query)
        else:
            qf = pd.DataFrame(query, columns=merged.columns)
            qf[column] = np.nan

        merged = pd.merge(merged, qf, how='outer', on='name', suffixes=['', '_b'])

    merged = merged[column_list]
    renamed_columns = {col: table + '_' + col for col in column_list if col not in hidden_columns}
    merged.rename(columns=renamed_columns, inplace=True)

    tables = column_dict.keys()
    for table in tables:
        if table == 'Star' or len(column_dict[table]) == 0:
            # we already dealt with the Star table
            continue

        model = apps.get_model(app_label='db', model_name=table)
        column_list = column_dict[table]
        model_columns = cols.get_model_columns(model)

        try:
            input_query = model.objects.filter(star_id__in=star_names)
            input_df = pd.DataFrame(input_query.values())
            merge_on = 'id'
        except FieldError:
            input_query = stars
            input_df = pd.DataFrame(input_query.values())
            input_df['id'] = input_df['name']
            merge_on = 'name'

        table_df = input_df.copy()

        available_columns = model_columns
        for column in column_list:
            t1 = time.time()

            if column in available_columns:
                qf = input_df[['id', 'star_id', column]]
                logging.debug("Column {} available in the model".format(column))
            else:
                if column not in colmapper.keys():
                    logging.debug("Column calculation function for {} not defined".format(column))
                    return merged
                query = colmapper[column](input_query)

                if query.count() > 0:
                    qf = pd.DataFrame(query)
                else:
                    qf = pd.DataFrame(query, columns=input_df.columns)
                    qf[column] = np.nan

                t2 = time.time()
                logging.debug("Calculated {} for {} stars in {:.4f} s".format(column, stars.count(), t2-t1))

            outcols = qf.columns
            if merge_on not in outcols and 'star_id' in outcols:
                merge_on = 'star_id'
            elif merge_on not in outcols and 'id' in outcols:
                merge_on = 'id'

            logging.debug("Merging column {} for table {} ({}x{}) on key {}".format(column, table, len(table_df), len(qf), merge_on))

            table_df = pd.merge(table_df, qf, how='left', on=merge_on, suffixes=['', '_b'])

            unused = list(table_df.filter(regex='_b$'))
            logging.debug('Dropping {} unused columns'.format(len(unused)))
            table_df.drop(unused, axis=1, inplace=True)
            table_df.drop_duplicates(inplace=True)

        merged = merged.loc[:, ~merged.columns.duplicated()]
        merged.drop_duplicates(inplace=True)
        logging.debug('Final merge of table {} ({}x{}) unused columns'.format(table, len(merged), len(table_df)))
        if 'name' in table_df.columns and not 'star_id' in table_df.columns:
            table_df['star_id'] = table_df['name']
        merged = pd.merge(merged, table_df, how='left', right_on='star_id', left_on='Star_name', suffixes=['', '_b'])
        merged.drop(list(merged.filter(regex='_b$')), axis=1, inplace=True)

        renamed_columns = {col: table + '_' + col for col in column_list}
        merged.rename(columns=renamed_columns, inplace=True)

    if 'Star_vmag' in merged.columns:
        merged = fill_vmag(stars, merged)
    merged = merged.query('Star_name != "" and Star_name != "null"')

    merged = merged.replace({'nan': None})
    merged = merged.replace({pd.np.nan: None})
    merged.sort_values(by='Star_name', inplace=True)
    merged = merged.drop_duplicates()
    final_columns = merged.columns

    if 'TOI' in tables and len(column_dict['TOI']) > 0:
        if 'TOI_toi_cand' in final_columns:
            check_cols = ['Star_name', 'TOI_toi_cand']
        elif 'TOI_per' in final_columns and 'TOI_rp' in final_columns:
            check_cols = ['Star_name', 'TOI_per', 'TOI_rp']
        else:
            check_cols = ['Star_name'] + ['TOI_'+c for c in column_dict['TOI']]
    else:
        check_cols = ['Star_name']

    logging.debug("Dropping rows with duplcate entries in the following columns: {}".format(check_cols))
    merged = merged.drop_duplicates(subset=check_cols, keep='first')

    return merged


def add_observing_stats(stars):
    """Add some aggregate statistics to the stars table"""

    t1 = time.time()

    if isinstance(stars, list):
        qlist = [star.name for star in stars]
        stars = db.models.Star.objects.filter(name__in=qlist)

    logging.debug("Calculating num_nights")
    queries = dict()
    queries['num_nights'] = stars \
        .annotate(date=TruncDate('observations__utctime'))\
        .values('date', 'name')\
        .annotate(c=Count('date', distinct=True))\
        .values('name')\
        .annotate(num_nights=Count('date', distinct=True, output_field=FloatField()))\
        .values()

    # logging.debug("Calculating num_nights_hires_j")
    # queries['num_nights_hires_j'] = stars \
    #     .filter(observations__instrument__contains='hires_j') \
    #     .annotate(date=TruncDate('observations__utctime')) \
    #     .values('date', 'name')\
    #     .annotate(c=Count('date')) \
    #     .values('name') \
    #     .annotate(num_nights_hires_j=Count('date', distinct=True, output_field=FloatField())) \
    #     .values()
    #
    # logging.debug("Calculating num_nights_apf")
    # queries['num_nights_apf'] = stars \
    #     .filter(observations__instrument__contains='apf') \
    #     .annotate(date=TruncDate('observations__utctime')) \
    #     .values('date', 'name')\
    #     .annotate(c=Count('date')) \
    #     .values('name') \
    #     .annotate(num_nights_apf=Count('date', distinct=True, output_field=FloatField())) \
    #     .values()
    #
    #
    logging.debug("Calculating last_observed and last comment")
    queries['last_observed'] = stars \
        .annotate(now=Now()) \
        .annotate(dt=DiffDays(CastDate(F('now')) - CastDate(F('observations__utctime'))),
                  dc=DiffDays(CastDate(F('now')) - CastDate(F('comments__submit_date')))) \
        .values('name')\
        .annotate(last_observed=Min('dt'), last_comment=Min('dc')) \
        .values()
    #
    # logging.debug("Calculating last_observed_hires_j")
    # queries['last_observed_hires_j'] = stars \
    #     .filter(observations__instrument__contains='hires_j') \
    #     .annotate(now=Now()) \
    #     .annotate(dt=DiffDays(CastDate(F('now')) - CastDate(F('observations__utctime'))) + 1) \
    #     .values('name')\
    #     .annotate(last_observed_hires_j=Min('dt')) \
    #     .values()
    #
    # logging.debug("Calculating last_observed_apf")
    # queries['last_observed_apf'] = stars \
    #     .filter(observations__instrument__contains='apf') \
    #     .annotate(now=Now()) \
    #     .annotate(dt=DiffDays(CastDate(F('now')) - CastDate(F('observations__utctime'))) + 1) \
    #     .values('name')\
    #     .annotate(last_observed_apf=Min('dt')) \
    #     .values()

    queries['simbad'] = stars.values('name',
                                     'simbad__simbad_v_mag',
                                     'simbad__simbad_g_mag',
                                     'simbad__simbad_ra',
                                     'simbad__simbad_dec',
                                     'simbad__simbad_othernames')

    queries['programs'] = stars.annotate(program_list=Concat('programs__name', separator=', '))\
                               .values('name', 'program_list')

    merged = pd.DataFrame([], columns=['name'])
    for key, val in queries.items():
        merged = pd.merge(merged, pd.DataFrame(val), how='outer', on='name', suffixes=['', '_{}'.format(key)])
        if 'last_observed' in key:
            pass
            # merged[key].fillna(9999, inplace=True)
            # merged['last_comment'].fillna(9999, inplace=True)
        elif 'num_nights' in key:
            merged[key].fillna(0, inplace=True)

    merged['vmag'].replace(0, np.nan, inplace=True)
    merged['vmag'].fillna(np.round(merged['simbad__simbad_v_mag'], 2), inplace=True)

    merged = merged.query('name != ""')
    merged['othernames'] = merged['simbad__simbad_othernames'].str.replace('|', ',')

    stars = merged.replace({pd.np.nan: None}).to_dict('records')

    t2 = time.time()

    logging.debug("Calculated aggregate Star statistics in {:.4f} s".format(t2-t1))

    return stars


def filter_rvs(df):
    df = df[df['errvel'] <= 3*np.nanmedian(df['errvel'])]

    if 'mdchi' in df.columns and 'cts' in df.columns:
        df = df.query('mdchi < 2 and cts > 3000')
    if 'snr' in df.columns:
        df = df.query('snr > 10')
    if 'dewar' in df.columns:
        df = df.query('dewar > 1')

    return df


def binvels(vst, hours=2.0):
    """
    Bin velocities in a DataFrame

    Args:
        vst (DataFrame): DataFrame with times, velocities, and errors as bjd, mnvel, and errvel respectively
    Returns:
        DataFrame : binned vst

    """

    newvst = pd.DataFrame()

    t, v, e = timebin(vst['bjd'].values, vst['mnvel'].values, vst['errvel'].values, hours/24.)
    newvst['bjd'] = t
    newvst['mnvel'] = v
    newvst['errvel'] = e

    newvst['tel'] = vst['tel'].iloc[0]

    return newvst


def timebin(time, meas, meas_err, binsize):
    """Bin in equal sized time bins

    This routine bins a set of times, measurements, and measurement errors
    into time bins.  All inputs and outputs should be floats or double.
    binsize should have the same units as the time array.
    (from Andrew Howard, ported to Python by BJ Fulton)

    Args:
        time (array): array of times
        meas (array): array of measurements to be comined
        meas_err (array): array of measurement uncertainties
        binsize (float): width of bins in same units as time array

    Returns:
        tuple: (bin centers, binned measurements, binned uncertainties)
    """

    ind_order = np.argsort(time)
    time = time[ind_order]
    meas = meas[ind_order]
    meas_err = meas_err[ind_order]
    ct = 0
    while ct < len(time):
        ind = np.where((time >= time[ct]) & (time < time[ct]+binsize))[0]
        num = len(ind)
        wt = (1./meas_err[ind])**2.     # weights based in errors
        wt = wt/np.sum(wt)              # normalized weights
        if ct == 0:
            time_out = [np.sum(wt*time[ind])]
            meas_out = [np.sum(wt*meas[ind])]
            meas_err_out = [1./np.sqrt(np.sum(1./(meas_err[ind])**2))]
        else:
            time_out.append(np.sum(wt*time[ind]))
            meas_out.append(np.sum(wt*meas[ind]))
            meas_err_out.append(1./np.sqrt(np.sum(1./(meas_err[ind])**2)))
        ct += num

    return time_out, meas_out, meas_err_out


def calc_rv_offset(t1, t2, v1, v2, npoints=10):
    """Find RV offset between two datasets by calculating the median
    difference between closest npoints points in time.

    Args:
        t1 (array): array of timestamps for dataset 1
        t2 (array): array of timestamps for dataset 2
        v1 (array): array of velocities for dataset 1
        v2 (array): array of velocities for dataset 2
        npoints (int): calculate median offset between closest npoints measurements

    Returns:
        float: offset to add to dataset 2
    """
    it1 = range(len(t1))
    it2 = range(len(t2))

    comb = np.array(np.meshgrid(t1, t2)).T.reshape(-1, 2)
    ci = np.array(np.meshgrid(it1, it2)).T.reshape(-1, 2)
    diff = np.abs(comb[:, 0] - comb[:, 1])
    npoints = int(np.clip(npoints, 0, len(diff)))

    sort = np.argsort(diff)[:npoints]

    vels1 = v1[ci[sort][:, 0]]
    vels2 = v2[ci[sort][:, 1]]

    offset = np.median(vels1 - vels2)

    return offset


def download_url(starname, path, filename=None):
    if filename is None:
        return "/download/" + starname + "?file=" + path
    else:
        return "/download/" + starname + "?file=" + path + \
               "&filename=" + filename


def display_url(starname, path):
    return "/file/" + starname + "?file=" + path
