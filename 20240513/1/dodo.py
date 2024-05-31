"""Automatization of building project."""
import glob
import shutil

from doit.task import clean_targets


DOIT_CONFIG = {'default_tasks': ['test', 'sdist', 'wheel', 'rm_db']}


def task_gen_pot():
    """Generate .pot template."""
    return {
            'actions': ['pybabel extract --keywords=ngettext:2,3 --keywords=_:2 mood/server -o i18n/server.pot'],
            'file_dep': glob.glob('mood/server/*.py'),
            'targets': ['i18n/server.pot'],
            'doc': 'Create/re-create ".pot" patterns.',
            'clean': [clean_targets],
    }


def task_upd_po():
    """Generate .po file."""
    return {
            'actions': ['pybabel update --ignore-pot-creation-date -l ru_RU.UTF-8\
                        -i i18n/server.pot -D mood -d i18n/po'],
            'file_dep': ['i18n/server.pot'],
            'targets': ['i18n/po/ru_RU.UTF-8/LC_MESSAGES/mood.po'],
            'doc': 'Update translation',
    }


def task_gen_mo():
    """Generate .mo file."""
    return {
            'actions': ['mkdir -p mood/po/ru_RU.UTF-8/LC_MESSAGES/',
                        'pybabel compile -l ru_RU.UTF-8 -i i18n/po/ru_RU.UTF-8/LC_MESSAGES/mood.po -D mood -d mood/po'],
            'file_dep': ['i18n/po/ru_RU.UTF-8/LC_MESSAGES/mood.po'],
            'targets': ['mood/po/ru_RU.UTF-8/LC_MESSAGES/mood.mo'],
            'doc': 'compile translations',
            'clean': [clean_targets],
    }


def task_rm_db():
    """Remove generated files."""
    return {
            'actions': ['rm .*.db'],
            'doc': 'Remove "doit" db.',
    }


def task_i18n():
    """Update translation of project."""
    return {
            'actions': None,
            'task_dep': ['gen_pot', 'upd_po', 'gen_mo'],
            'doc': 'Generate translation.',
    }


def task_gen_html():
    """Generate html documentation."""
    return {
            'actions': ['sphinx-build -M html ./docs/source ./mood/docs/build'],
            'file_dep': glob.glob('docs/source/*.rst') + glob.glob('mood/*/*.py'),
            'targets': ['mood/docs/build'],
            'clean': [(shutil.rmtree, ["mood/docs/build"])],
    }


def task_test():
    """Run tests."""
    return {
            'actions': ['python3 -m unittest server_test.py', 'python3 -m unittest client_test.py'],
            'task_dep': ['i18n'],
            'doc': 'Test client and server.',
    }


def task_del_uncommited():
    """Delete uncommited files."""
    return {
            'actions': ['git clean -xdf'],
            'doc': 'Clean uncommited files',
            }


def task_sdist():
    """Build project."""
    return {
            'actions': ['python3 -m build -s -n'],
            'task_dep': ['del_uncommited'],
            'doc': 'Generate source distribution',
            }


def task_wheel():
    """Create wheel."""
    return {
            'actions': ['python3 -m build -w'],
            'task_dep': ['i18n', 'gen_html'],
            'doc': 'Generate wheel',
            }
