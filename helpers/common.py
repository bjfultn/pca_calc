import os, time, sys, re, unicodedata
import misaka as m
import helpers
from pca_calc import settings
from django.template.defaultfilters import stringfilter
from django import template
from pygments import highlight
from pygments.formatters import HtmlFormatter, ClassNotFound
from pygments.lexers import get_lexer_by_name
register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def parameterize(string, sep = '-'):
    parameterized_string = unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore').decode()
    parameterized_string = re.sub("[^a-zA-Z0-9\-_]+", sep, parameterized_string)
    if sep is not None and sep is not '':
        parameterized_string = re.sub('/#{re_sep}{2,}', sep, parameterized_string)
        parameterized_string = re.sub('^#{re_sep}|#{re_sep}$', sep, parameterized_string, re.I)
    return parameterized_string.lower()


@register.filter(is_safe=True)
@stringfilter
def markdown(text):
    if not text:
        text = ""
    renderer = HighlighterRenderer(flags=m.HTML_HARD_WRAP)
    md = m.Markdown(
        renderer,
        extensions=m.EXT_TABLES |
                   m.EXT_FENCED_CODE |
                   m.EXT_FOOTNOTES |
                   m.EXT_AUTOLINK |
                   m.EXT_STRIKETHROUGH |
                   m.EXT_UNDERLINE |
                   m.EXT_HIGHLIGHT |
                   m.EXT_QUOTE |
                   m.EXT_SUPERSCRIPT |
                   m.EXT_MATH |
                   m.EXT_NO_INTRA_EMPHASIS |
                   m.EXT_SPACE_HEADERS |
                   m.EXT_MATH_EXPLICIT |
                   m.EXT_DISABLE_INDENTED_CODE
    )
    rendered_text = md(text)
    smarty_text = m.smartypants(rendered_text)
    return smarty_text


class HighlighterRenderer(m.HtmlRenderer):
    def blockcode(self, text, lang):
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ClassNotFound:
            lexer = None

        if lexer:
            formatter = HtmlFormatter()
            return highlight(text, lexer, formatter)
        # default
        return '\n<pre><code>{}</code></pre>\n'.format(text.strip)


@register.simple_tag
def server_env():
    if 'runserver' in sys.argv:
        return "development"
    else:
        return "production"


@register.filter
def spell_it_out(string):
    new_string = ""
    for c in string:
        if c == " ":
          new_string += c
        else:
          new_string += c + "-"
    return new_string


@register.filter(name='zip')
def zip_lists(a, b):
  return zip(a, b)


@register.filter(name='order_by')
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)


@register.filter
def comment_format(string):
    return string.replace("\n", "<br />")

@register.filter
def getattr(field, names):
    return names[field]

@register.filter
def static_plot_created_at(string):
    try:
        data_dir = settings.DATA_DIR
        file = string.split("=")[1]
        path = os.path.join(data_dir, file)
        date = time.strftime("%a %b %d %H:%M:%S %Z %Y", time.gmtime(os.path.getmtime(path)))
    except (FileNotFoundError, IOError):
        return ""

    return date

@register.filter
def retain_whitespace(string):
    try:
        return string.replace(' ', '&nbsp;').rstrip()
    except AttributeError:
        return string


@register.filter
def dec_backup(dec, star):
    source = 'simbad__simbad_dec'

    if -90 <= dec <= 90:
        return dec
    else:
        dec = np.nan

    if np.isnan(dec):
        try:
            dec_split = star[source].split()
            dec = float(dec_split[0]) + float(dec_split[1])/60.
            # logging.debug('Loaded V mag from {}: {}:{}'.format(source, star['name'], vmag))
            if not np.isnan(dec):
                return dec
        except AttributeError:
            pass

    return 99


@register.filter
def since_crop(value):

    return value.split(',')[0]


@register.filter
def get_fits_name(obs, type):
    spectra = obs.spectra.filter(spectrum_type=type)
    if spectra.count() >= 1:
        return spectra.first().filename
    else:
        return ''


@register.filter
def get_item(dict, key):
    result = dict.get(key)
    if result is None:
        result = ''

    return result


@register.filter
def download(path, starname):
    if path is None:
        return None
    else:
        return download_url(starname, path, os.path.basename(path))


@register.filter
def pd_to_datatable(df, classes=None):
    cols = df.columns
    for col in cols:
        df[col] = df[col].replace(np.nan, '')
    html = df.to_html(classes=classes,
                      header=False,
                      index=False,
                      border=False,
                      columns=cols,
                      na_rep='',
                      formatters={'time': lambda x: x.strftime("%Y-%m-%d %H:%M") if isinstance(x, datetime) else x[:-7]},
                      float_format=lambda x: "{:.3f}".format(x))

    # strip out data only
    html = '\n'.join(html.split('\n')[1:-1])

    return html

@register.filter
def user_settings_filter(settings, key):
    default_value = None

    if key == 'stars_table_columns':
      default_value = helpers.stars_table.default_columns()

    if key == 'candidates_table_columns':
      default_value = helpers.candidates.default_columns()

    return settings.get(key, default_value)

@register.filter
def inspect(object, error = False):
    if error == True:
      raise ValueError(object)
    else:
      return dir(object)

@register.filter
def to_spaces(string):
    return string.replace("_", " ").replace("-", " ")

@register.filter
def params_to_obj(string):
    params = {}
    for pair in string.split("|"):
        params[pair.split(":")[0]] = pair.split(":")[1]
    return params

@register.filter
def list_length_gt(obj, length):
    return len(list(obj)) > length
