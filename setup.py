try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup
	
config = {
	'description': 'transforms a raspberry pi in a music player',
	'author': 'Antoine Orozco',
	'url': 'URL to get it at.',
	'download_url': 'Where to download it.',
	'author_email': 'orozco_antoine@yahoo.fr'
	'version': '0.1',
	'install_requires': ['nose'],
	'packages': ['NAME'],
	'scripts': [],
	'name': 'pimusic'
}

setup(**config)
