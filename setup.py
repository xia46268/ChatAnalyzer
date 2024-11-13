from setuptools import setup, find_packages

setup(
    name='chatanalyzer',
    version='0.1.6',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'seaborn',
        'requests',
        'tqdm',
        'jieba',
        'wordcloud',
    ],
    entry_points={
        'console_scripts': [
            'chatanalyzer=chatanalyzer.main:main',
        ],
    },
    author='Rong Xia',
    author_email='xia46268@gmail.com',
    description='A tool for analyzing Chinese chat data',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/xia46268/ChatAnalyzer',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)