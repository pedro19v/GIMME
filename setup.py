from setuptools import setup

setup(
    name="GIMMECore",
    version="1.1.0",
    license = "CC BY 4.0",
    author="Samuel Gomes",
    author_email = "samuel.gomes@tecnico.ulisboa.pt",
    packages=['GIMMECore', 'GIMMECore.ModelBridge', 'GIMMECore.AlgDefStructs'],
    classifiers = [
    'Development Status :: Development',
    'Intended Audience :: Science/Research',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Scientific/Engineering :: Adaptation'
    ]

)

