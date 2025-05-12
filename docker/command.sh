#!/usr/bin/env bash

jupyter lab \
    --ip=0.0.0.0 \
    --port=9000 \
    --ServerApp.token=abcd \
    --ServerApp.allow_remote_access=True \
    --no-browser
