from setuptools import setup, find_packages

setup(
    name='devilzero',
    version='2.0.0',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'devilzero = devilzero.main:main',
        ],
    },
    install_requires=[line.strip() for line in open('requirements.txt').readlines() if line.strip()],
    python_requires='>=3.8',
    author='Voktha',
    author_email='voktha@proton.me',
    description='DDoS testing toolkit (educational use only)',
    license='MIT',
    url='https://github.com/Vokthos/devilZERO',
)