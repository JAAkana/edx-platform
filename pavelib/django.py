from paver.easy import *
from paver.setuputils import setup

from pavelib import prereqs, proc_utils
from proc_utils import write_stderr

default_port = {"lms": '8000', "cms": '8001'}

setup(
    name="OpenEdX",
    packages=['OpenEdX'],
    version="1.0",
    url="",
    author="OpenEdX",
    author_email=""
)


@task
def pre_django():
    """
    Installs requirements and cleans previous python compiled files
    """
    prereqs.install_python_prereqs()
    sh("find . -type f -name *.pyc -delete")
    sh('pip install -q --no-index -r requirements/edx/local.txt')


@task
@cmdopts([
    ("env=", "e", "Environment settings"),
    ("port=", "p", "Port")
])
def cms(options):

    setattr(options, 'system', 'cms')
    run_server(options)


@task
@cmdopts([
    ("env=", "e", "Environment settings"),
    ("port=", "p", "Port")
])
def lms(options):

    setattr(options, 'system', 'lms')
    run_server(options)


@task
@cmdopts([
    ("system=", "s", "System to act on"),
    ("env=", "e", "Environment settings"),
    ("port=", "p", "Port")
])
def run_server(options):
    """
      runs server specified by system using a supplied environment
    """
    system = getattr(options, 'system', 'lms')
    env = getattr(options, 'env', 'dev')
    port = getattr(options, 'port', '')

    if port == '':
        port = default_port[system]

    try:
        sh('python manage.py %s runserver --traceback --settings=%s' % (system, env) + ' --pythonpath=. ' + port)
    except:
        write_stderr("Failed to runserver")
        return


@task
@cmdopts([
    ("env=", "e", "Environment settings"),
])
def resetdb():
    """
      runs syncdb and then migrate
    """
    env = getattr(options, 'env', 'dev')

    sh('python manage.py lms syncdb --traceback --settings=%s' % (env) + ' --pythonpath=. ')
    sh('python manage.py lms migrate --traceback --settings=%s' % (env) + ' --pythonpath=. ')


@task
@cmdopts([
    ("system=", "s", "System to act on"),
    ("env=", "e", "Environment settings"),
])
def check_settings():
    """
       checks settings files
    """
    system = getattr(options, 'system', 'lms')
    env = getattr(options, 'env', 'dev')

    try:
        sh(("echo 'import %s.envs.%s'" % (system, env)) + ' | python manage.py %s shell --plain --settings=%s' % (system, env) + ' --pythonpath=. ')
    except:
        write_stderr("Failed to import settings")
        return


@task
@cmdopts([
    ("system=", "s", "System to act on"),
    ("env=", "e", "Environment settings"),
])
def run_celery():
    """
      runs celery for the specified system
    """
    system = getattr(options, 'system', 'lms')
    env = getattr(options, 'env', 'dev_with_worker')

    proc_utils.run_process(['python manage.py %s celery worker --loglevel=INFO --settings=%s --pythonpath=. ' % (system, env)], True)


@task
@cmdopts([
    ("env=", "e", "Environment settings"),
    ("worker_env=", "w", "Celery Worker Environment settings"),
])
def run_all_servers():
    """
      runs cms, lms and celery workers
    """
    env = getattr(options, 'env', 'dev')
    worker_env = getattr(options, 'env', 'dev_with_worker')

    proc_utils.run_process(['python manage.py lms runserver --traceback --settings=%s' % (env) + ' --pythonpath=. ' + default_options['lms'],
                            'python manage.py cms runserver --traceback --settings=%s' % (env) + ' --pythonpath=. ' + default_options['cms'],
                            'python manage.py lms celery worker --loglevel=INFO --settings=%s --pythonpath=. ' % (worker_env),
                            'python manage.py cms celery worker --loglevel=INFO --settings=%s --pythonpath=. ' % (worker_env)
                            ], True)


@task
@cmdopts([
    ("env=", "e", "Environment settings"),
    ("src=", "s", "Source location"),
    ("dest=", "d", "Destination location"),
])
def clone_course():
    """
      Clone existing MongoDB based course
    """
    env = getattr(options, 'env', 'dev')
    src = getattr(options, 'src', '')
    dest = getattr(options, 'dest', '')

    if src == '' or dest == '':
        print("You must provide a source and destination")
        exit()

    sh('python manage.py cms clone --traceback --settings=%s' % (env) + ' --pythonpath=. %s %s' % (src, dest))


@task
@cmdopts([
    ("env=", "e", "Environment settings"),
    ("location=", "l", "Location to delete"),
    ("commit=", "c", "Commit"),
])
def delete_course():
    """
      Delete existing MongoDB based course
    """
    env = getattr(options, 'env', 'dev')
    location = getattr(options, 'location', '')
    commit = getattr(options, 'commit', 'True')

    if location == '':
        print("You must provide a location")
        exit()

    sh('python manage.py cms delete_course --traceback --settings=%s' % (env) + ' --pythonpath=. %s %s' % (location, commit))


@task
@cmdopts([
    ("env=", "e", "Environment settings"),
    ("data_dir=", "d", "Data directory"),
    ("course_dir=", "c", "Course directory"),
])
def import_course():
    """
      Import course data from a directory
    """
    env = getattr(options, 'env', 'dev')
    data_dir = getattr(options, 'data_dir', '')
    course_dir = getattr(options, 'course_dir', '')

    if data_dir == '':
        print("You must provide a directory")
        exit()

    sh('python manage.py cms import --traceback --settings=%s' % (env) + ' --pythonpath=. %s %s' % (data_dir, course_dir))


@task
@cmdopts([
    ("env=", "e", "Environment settings"),
    ("data_dir=", "d", "Data directory"),
    ("course_dir=", "c", "Course directory"),
])
def xlint_course():
    """
      xlint course data in a directory
    """
    env = getattr(options, 'env', 'dev')
    data_dir = getattr(options, 'data_dir', '')
    course_dir = getattr(options, 'course_dir', '')

    if data_dir == '':
        print("You must provide a directory")
        exit()

    sh('python manage.py cms xlint --traceback --settings=%s' % (env) + ' --pythonpath=. %s %s' % (data_dir, course_dir))


@task
@cmdopts([
    ("env=", "e", "Environment settings"),
    ("course_id=", "c", "Course to export"),
    ("output=", "o", "Output path"),
])
def export_course():
    """
      Export course data to a tar.gz file
    """
    env = getattr(options, 'env', 'dev')
    course_id = getattr(options, 'course_id', '')
    output = getattr(options, 'output', '')

    if course_id == '' or output == '':
        print("You must provide a course id and output path")
        exit()

    sh('python manage.py cms export --traceback --settings=%s' % (env) + ' --pythonpath=. %s %s' % (course_id, output))


@task
@cmdopts([
    ("system=", "s", "System to act on"),
    ("env=", "e", "Environment settings"),
    ("user=", "u", "User to set staff bit"),
])
def set_staff():
    """
      Export course data to a tar.gz file
    """
    system = getattr(options, 'system', 'lms')
    env = getattr(options, 'env', 'dev')
    user = getattr(options, 'user', '')

    if user == '':
        print("You must provide a user id")
        exit()

    sh('python manage.py cms set_staff --traceback --settings=%s' % (env) + ' --pythonpath=. %s ' % (user))


@task
@cmdopts([
    ("action=", "a", "Action"),
    ("system=", "s", "System to act on"),
    ("env=", "e", "Environment settings"),
    ("options=", "o", "Options"),
])
def django_admin():
    """
      Execute a manage.py command
    """
    action = getattr(options, 'action', '')
    system = getattr(options, 'system', '')
    env = getattr(options, 'env', 'dev')
    arg_options = getattr(options, 'options', '')

    if action == '':
        print("You must provide an action")
        exit()

    if system == '' and (arg_options == 'migrate' or arg_options == 'syncdb'):
        sh('python manage.py cms %s --traceback --settings=%s' % (action, env) + ' --pythonpath=. %s ' % (arg_options))
        sh('python manage.py lms %s --traceback --settings=%s' % (action, env) + ' --pythonpath=. %s ' % (arg_options))
    else:
        if system == '':
            system = 'lms'

        sh('python manage.py %s %s --traceback --settings=%s' % (system, action, env) + ' --pythonpath=. %s ' % (arg_options))
