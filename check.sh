#!/bin/sh

if [ ! -f .venv/bin/activate ] && [ ! -f .venv/Scripts/activate ]; then
    echo "Cannot found .venv: please do python3 -m venv .venv"
    echo "Make sure your python version is python3.11 or later"
    exit 1
fi


if [ ! "$WINDIR" = "" ]; then
    . .venv/Scripts/activate
else
    . .venv/bin/activate
fi

pylint --rcfile pylint.toml chatapp
if [ ! "$?" = 0 ]; then
    echo "Pylint error"
    exit 1
fi
pytest
