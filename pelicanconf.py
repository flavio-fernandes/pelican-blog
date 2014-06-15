#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Flavio'
SITENAME = u'FlavioBlog'
SITEURL = ''
ARTICLE_URL = '{category}/{slug}.html'
ARTICLE_SAVE_AS = '{category}/{slug}.html'
YEAR_ARCHIVE_SAVE_AS = 'archives/{date:%Y}/index.html'
MONTH_ARCHIVE_SAVE_AS = 'archives/{date:%Y}/{date:%b}/index.html'
TIMEZONE = 'America/New_York'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Links
LINKS =  (('Delicious Links', 'http://delicious.com/gute'),
          ('Red Hat', 'http://redhat.com/'),
          ('Open Day Light', 'http://www.opendaylight.org/'))

# Social widget
SOCIAL = (('Twitter', 'http://twitter.com/guteusa'),
          ('LinkedIn', 'https://www.linkedin.com/pub/flavio-fernandes/3/110/a26'),
          ('GitHub', 'http://github.com/flavio-fernandes'))

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# Theme
THEME = 'themes/pelican-bootstrap3'

# Dark Nav
## BOOTSTRAP_NAVBAR_INVERSE = True

# Display Preferences
DISPLAY_CATEGORIES_ON_MENU = True
DISPLAY_CATEGORIES_ON_SIDEBAR = False
DISPLAY_TAGS_ON_SIDEBAR = True
TAG_CLOUD = True
TAG_CLOUD_MAX_ITEMS = 20

# Load the Summary Plugin
PLUGIN_PATH = 'plugins'
PLUGINS = ['summary',
           'pelican_gist']

# Set the End Marker to
SUMMARY_END_MARKER = '<!--more-->'

## # Monokai lovin'
## PYGMENTS_STYLE = 'monokai'
PYGMENTS_STYLE = 'emacs'

# License
CC_LICENSE = 'CC-BY-NC'

# BootStrap
BOOTSTRAP_THEME = 'simplex'

#Github
## GITHUB_URL = 'https://github.com/flavio-fernandes'
