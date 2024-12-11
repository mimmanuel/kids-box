help:
    just --list

install:
    uv sync

run-dev:
    uv run fastapi dev spotify.py
