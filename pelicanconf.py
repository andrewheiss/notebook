#!/usr/bin/env python3
import jinja2
from bs4 import BeautifulSoup

# Site development flag
DEVELOPING_SITE = True

DELETE_OUTPUT_DIRECTORY = True


# ------------------
# Site information
# ------------------
AUTHOR = 'Andrew Heiss'
SITENAME = 'Heiss Research Notebook'
DESCRIPTION = ''

SITEURL = ''
GITHUB_URL = 'https://github.com/andrewheiss/notebook'

PATH = 'content'

TIMEZONE = 'America/New_York'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_LANG = 'en'

TYPOGRIFY = True  # Nice typographic things
TYPOGRIFY_IGNORE_TAGS = ['h1']


# ---------------
# Site building
# ---------------
# Theme
THEME = 'theme'

# Folder where everything lives
PATH = 'content'

# Templates that are actually full pages
DIRECT_TEMPLATES = (('index', 'tags', 'categories', 'archives',
                     'all_notes', 'search'))

# The notebook is structured around projects (categories), which contain notes
# (articles). It should follow this URL structure:
#   /project/ = list of all projects
#   /project/project-name/ = description of project + list of notes
#   /project/project-name/note-title/ = actual note

# Category stuff
USE_FOLDER_AS_CATEGORY = True

CATEGORIES_URL = 'project/'
CATEGORIES_SAVE_AS = 'project/index.html'

REVERSE_CATEGORY_ORDER = False
CATEGORY_URL = 'project/{slug}/'
CATEGORY_SAVE_AS = 'project/{slug}/index.html'

ARTICLE_URL = 'project/{category}/{slug}/'
ARTICLE_SAVE_AS = 'project/{category}/{slug}/index.html'

# Note stuff
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

# Tag stuff
TAG_SAVE_AS = ''
TAGS_SAVE_AS = 'tags/index.html'

# Remove author pages
AUTHOR_SAVE_AS = ''
AUTHORS_SAVE_AS = ''

ARCHIVES_SAVE_AS = 'archive/index.html'

# Include source files, just for fun
OUTPUT_SOURCES = True
OUTPUT_SOURCES_EXTENSION = '.txt'

# Ordering
PAGE_ORDER_BY = 'date'
ARTICLE_ORDER_BY = 'reversed-date'

STATIC_PATHS = ['files', 'robots.txt']
READERS = {'html': None}  # Don't parse HTML files

# Search
SEARCH_SAVE_AS = 'search/index.html'
ALL_NOTES_SAVE_AS = 'all_notes/index.html'


# ---------
# Plugins
# ---------
PLUGIN_PATHS = ['/Users/andrew/Development/•Pelican/pelican-plugins']
PLUGINS = ['category_meta', 'always_modified', 'pandoc_reader', 'tipue_search']

MD_EXTENSIONS = ['smarty', 'extra', 'footnotes', 'meta',
                 'codehilite(css_class=highlight)', 'headerid(level=2)']


# Pandoc settings
bibliography_path = '/Users/andrew/Dropbox/Readings/Papers.bib'
csl_path = '/Users/andrew/.pandoc/csl/american-political-science-association.csl'

PANDOC_ARGS = [
    '-t', 'html5',
    '--no-highlight',  # Use highlight.js instead
    '--base-header-level=2',  # Make all H1s H2s, etc.
    '--section-divs',  # wWap heading blocks with <section>
    '--filter', 'pandoc-citeproc',  # Bibliographies!
    '--csl=' + csl_path,
    '--bibliography=' + bibliography_path
]

# Feed generation
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None


LINKS = (('<i class="fa fa-home"></i> Notebook home', '/'),
         ('<i class="fa fa-question-circle"></i> About this notebook', '/about/'),
         ('<i class="fa fa-sort-alpha-asc"></i> All notes alphabetically', '/all_notes/'),
         ('<i class="fa fa-calendar"></i> All notes by date', '/archive/'),
         ('<i class="fa fa-tags"></i> All notes by tag', '/tags/'))

MENUITEMS = [('My homepage', 'https://www.andrewheiss.com'),
             ('ingorestrictions.org', 'https://ingorestrictions.org'),
             ('ingodata.org', 'https://ingodata.org')]

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True


# ---------------
# Jinja filters
# ---------------
def pure_table(html):
    soup = BeautifulSoup(html, 'html.parser')

    for table_tag in soup.find_all('table'):
        table_tag['class'] = table_tag.get('class', []) + ['pure-table']

    return jinja2.Markup(soup)

def fmt_date(value, fmt):
    return value.strftime(fmt)

def current_year(value):
    import time
    return(time.strftime("%Y"))


JINJA_FILTERS = {'pure_table': pure_table,
                 'fmt_date': fmt_date,
                 'current_year': current_year}
