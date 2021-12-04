from setuptools import setup, find_packages

dev_deps = [
    'pytest==6.2.5',
    'pytest-asyncio=0.16.0',
]


def read_requirements():
    f = open('./requirements.txt')
    deps = f.readlines()
    deps = set(deps) - {*dev_deps}
    deps = list(deps)
    f.close()
    return deps


setup(name='doter',
      version='0.0.1',
      author='Chi Zhang',
      description='A dotfile manager',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Topic : Utilities',
      ],
      packages=find_packages(include=['doter*'], exclude=['test', 'venv']),
      install_requires=read_requirements(),
      entry_points={'console_scripts': ['doter = doter.__main__:main']},
      extra_require={
          'dev': dev_deps,
      })
