import os
from setuptools import setup, find_packages

def recursive_include(relative_dir):
    all_paths = []
    root_prefix = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'chalicelib'
    )

    full_path = os.path.join(root_prefix, relative_dir)
    for rootdir, _, filenames in os.walk(full_path):
        for filename in filenames:
            abs_filename = os.path.join(rootdir, filename)
            all_paths.append(abs_filename[len(root_prefix) + 1:])
    return all_paths


setup(
    name='judicilib',
    version='0.1.0',
    description='Judicilib',
    author='izaias.junior@grancursosonline.com.br',
    packages=find_packages(where='chalicelib'),
    package_dir={'': 'chalicelib'},
    include_package_data=True,
    package_data={
        'judici': ['py.typed']
    },
    zip_safe=False,
    keywords='judici',
    classifiers=[
        'Programming Language :: Python :: 3.10',
    ],
    install_requires=[
        "pydantic-settings",
        "pydantic",
        "chalice",
        "chalice-local",
        "boto3",
        "python-dotenv",
        "PyPDF2",
    ],
)