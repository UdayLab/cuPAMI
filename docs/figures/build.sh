#!/bin/sh
# Rebuild the README figures. Requires tectonic and pdftocairo (poppler).
# Usage, from anywhere: sh docs/figures/build.sh
set -e
cd "$(dirname "$0")"
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
for name in algorithm-io gpu-setup gpu-pipeline; do
    tectonic --outdir "$out" "$name.tex"
    pdftocairo -svg "$out/$name.pdf" "$name.svg"
done
