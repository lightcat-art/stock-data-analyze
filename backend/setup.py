from setuptools import setup, find_packages


# version 파일에서 버전 가져옴

def get_version(path='version'):
    version = ""
    with open(path, 'r') as f:
        version = f.read().strip()

    return version


def get_option(path='build-option'):
    build_option = ""
    with open(path, 'r') as f:
        build_option = f.read().strip()

    return build_option


# requirements 파일에서 requirements 정보 가져옴
def get_requirements(path='requirements.txt'):
    reqs = []

    try:
        with open(path, 'r') as f:
            reqs = f.read().split()

        return reqs
    except Exception:
        return []


name = 'stock-data-analyze'
option = get_option(path='build-option')

if option == 'aio':
    setup(
        name=name,
        version=get_version(path='version'),
        description='',
        author='dhk',
        author_email='ehdgns322@gmail.com',
        urllib='',
        install_requires=get_requirements(path='requirements.txt'),
        packages=find_packages(exclude=['venv']),
        keywords=['stock', 'chart'],
        python_requires='>=3.7'
    )
elif option == 'source-only':
    setup(
        name=name,
        version=get_version(path='version'),
        description='',
        author='dhk',
        author_email='ehdgns322@gmail.com',
        urllib='',
        # install_requires=get_requirements(path='requirements.txt'),
        packages=find_packages(exclude=['venv']),
        keywords=['stock', 'chart'],
        python_requires='>=3.7'
    )
