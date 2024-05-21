from zipfile import ZipFile
from pathlib import Path
from glob import iglob

ZIPARCH = 'docs.zip'
HTMLINDEX = '_build/html/index.html'


def task_html():
    """Generate HTML docs."""
    return {
        'actions': ['sphinx-build -M html "." "_build"'],
        'file_dep': ["Moo.py", "API.rst", "index.rst"],
        'targets': [HTMLINDEX]
    }


def zipp(path, outfile):
    with ZipFile(outfile, 'w') as myzip:
        for p in iglob(path + '/**', recursive=True, include_hidden=True):
            P = Path(p)
            if P.is_file():
                myzip.write(p)


def task_zip():
    """Generate ZIP doc"""
    return {
        'actions': [(zipp, ['_build', ZIPARCH]),],
        'task_dep': ['html'],
        'targets': [ZIPARCH]
    }


def task_erase():
    """Erase all trash and generates"""
    return {
        'actions': ['git clean -xdf'],
    }

def task_pot():
    """Re-create .pot ."""
    return {
            'actions': ['pybabel extract -o DateTime.pot AppBase'],
            'file_dep': glob.glob('AppBase/*.py'),
            'targets': ['DateTime.pot'],
           }


def task_po():
    """Update translations."""
    return {
            'actions': ['pybabel update --ignore-pot-creation-date -D DateTime -d po -i DateTime.pot'],
            'file_dep': ['DateTime.pot'],
            'targets': ['po/ru/LC_MESSAGES/DateTime.po'],
           }


def task_mo():
    """Compile translations."""
    return {
            'actions': [
                (create_folder, [f'{PODEST}/ru/LC_MESSAGES']),
                f'pybabel compile -D DateTime -l ru -i po/ru/LC_MESSAGES/DateTime.po -d {PODEST}'
                       ],
            'file_dep': ['po/ru/LC_MESSAGES/DateTime.po'],
            'targets': [f'{PODEST}/ru/LC_MESSAGES/DateTime.mo'],
           }