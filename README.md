# Stein's Feed

Content aggregator.
Icon taken from [Santa Fe College](https://www.sfcollege.edu/about/index).

## Instructions

1.  Set up `python` environment.

        pyenv local python-3.8.6

2.  Set up virtual environment.

        python3 -m venv .venv
        source .venv/bin/activate

3.  Install packages.

        make requirements

4.  Download `feedparser`.

        git clone git@github.com:hy144328/feedparser
        git checkout copy2summary

5.  Link `feedparser`.

        ln -s ../feedparser/feedparser
