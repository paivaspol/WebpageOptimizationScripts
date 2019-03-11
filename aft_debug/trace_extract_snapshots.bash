#!/usr/bin/env bash

set -e

trace=$1
outdir=$2

if [[ ! -f $trace || -z $outdir ]]; then
	echo usage: trace_extract_snaps.bash trace outdir >&2
	exit 12
fi

mkdir -p "$outdir"
if [[ $? -ne 0 ]]; then
	echo "could not create $outdir, does it already exist?" >&2
	exit 3
fi

# jq -r -r '.traceEvents | .[] | select(.name == "Screenshot") | (.ts | tostring) + " " + .args.snapshot' "$trace" \
jq -r -r '.[] | select(.name == "Screenshot") | (.ts | tostring) + " " + .args.snapshot' "$trace" \
	| (
		start=NA
		while read line; do
			ts=$(( $(cut -d' ' -f1 <<<"$line") / 1000)) # μs to ms
			if [[ $start == "NA" ]]; then
				start=$ts
			fi
			t=$((ts-start)) 
			echo "$(cut -d' ' -f2 <<<"$line")" | base64 -d > "$outdir/$(printf "ms_%06d" $t).jpg"
		done
	)
