#!/bin/bash

set -e

PSTATS_FILE="profile.pstats"
SAMPLE_FILE="samples/ilgeo2010_excerpt.csv"
GRAPH_FILE="profile.svg"

python -m cProfile -o "$PSTATS_FILE" profiler.py samples/ilgeo2010_excerpt.csv
gprof2dot -f pstats "$PSTATS_FILE" | dot -Tsvg -o "$GRAPH_FILE"
