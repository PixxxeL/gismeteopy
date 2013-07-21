# -*- coding: utf-8 -*-

from distutils.core import setup
#import markdown2
import gismeteo

#with open('README.md') as fh:
# long_description = fh.read()
#markdowner = markdown2.Markdown()

setup(
    name = "gismeteopy",
    version = gismeteo.__version__,
    packages = ["gismeteo"],
    url = 'https://github.com/PixxxeL/gismeteopy',
    author = 'pixel',
    author_email = 'ivan.n.sergeev@gmail.com',
    maintainer = 'pixel',
    maintainer_email = 'ivan.n.sergeev@gmail.com',
    license = 'GPL3',
    description = 'Load data from gismeteo.ru service and processing them',
    #long_description = markdowner.convert(long_description),
    download_url = 'https://github.com/PixxxeL/gismeteopy/archive/master.zip',
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
