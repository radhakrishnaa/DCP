from setuptools import setup

setup(
    name='gdicfg',
    version=open('dcp/VERSION.txt').read().strip(),
    author='Device Configuration Portal',
    author_email='branta@motorola.com',
    url='https://sites.google.com/a/motorola.com/',
    packages=['dcp', 'api', 'api.migrations', 'django_cas', 'util',
              'gcalendarv3pyapi'],
    package_dir={'dcp': 'dcp'},
    description='Motorola Portal',
    install_requires=[
        "Django==1.5.1",
        "MySQL_python==1.2.5",
        "South==0.7.6",
        "distribute>=0.6.49",
        "django_filter==0.6",
        "django_reversion==1.7",
        "djangorestframework==2.2.6",
    ],
    include_package_data=True,
    zip_safe=False,
)
