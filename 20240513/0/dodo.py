import glob
import shutil

from doit.task import clean_targets


DOIT_CONFIG = {'default_tasks': ['html']}


def task_gen_pot():
    return {
            'actions': ['pybabel extract --keywords=ngettext:2,3 --keywords=_:2 mood -o server.pot'],
            'file_dep': glob.glob('mood/server/*.py'),
            'targets': ['server.pot'],
            'doc': 'Create/re-create ".pot" patterns.',
            'clean': [clean_targets],
    }


def task_upd_po():
    return {
            'actions': ['pybabel update --ignore-pot-creation-date -l ru_RU.UTF-8 -i server.pot -D mood -d po1'],
            'file_dep': ['server.pot'],
            'targets': ['po/ru_RU.UTF-8/LC_MESSAGES/mood.po'],
            'doc': 'Update translation',
    }


def task_gen_mo():
    return {
            'actions': ['pybabel compile -l ru_RU.UTF-8 -i po1/ru_RU.UTF-8/LC_MESSAGES/mood.po -D mood -d po1'],
            'file_dep': ['po1/ru_RU.UTF-8/LC_MESSAGES/mood.po'],
            'targets': ['po1/ru_RU.UTF-8/LC_MESSAGES/mood.mo'],
            'doc': 'compile translations',
            'clean': [clean_targets],
    }


def task_rm_db():
    return {
            'actions': ['rm .*.db'],
            'doc': 'Remove "doit" db.',
    }


def task_i18n():
    return {
            'actions': None,
            'task_dep': ['gen_pot', 'upd_po', 'gen_mo'],
            'doc': 'Generate translation.',
    }


def task_gen_html():
    return {
            'actions': ['sphinx-build -M html ./source ./build'],
            'file_dep': glob.glob('source/*.rst') + glob.glob('mood/*/*.py'),
            'targets': ['docs/build'],
            'clean': [(shutil.rmtree, ["build"])],
    }


def task_test():
    return {
            'actions': ['python3 -m unittest server_test.py'],
            'task_dep': ['i18n'],
            'doc': 'Test client and server.',
    }