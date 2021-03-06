#!/bin/sh

problempath=${1:-'/tmp/problems/'}
buildconf=${2:-'multigrid'}

[ "$buildconf" = "multigrid" ] || [ "$buildconf" = "gsrb" ] || exit 1

generate_problem() {
	../Python/problemgenerator/generate.py "$problempath" 2 "$1" -t "wave"
}

generate_problems() {
	[ -e "$problempath" ] || mkdir -p "$problempath"
	# delete existing problems
	rm -f "$problempath/"*.npy
	STEP=$([ "$buildconf" = "multigrid" ] && echo "64" || echo "16")
	# generate new problems
	for i in $(seq 1 20); do
		generate_problem $((i * STEP))
	done

	if [ "$buildconf" = "gsrb" ]; then
		for i in $(seq 1 15); do
			generate_problem $((320 + (i * 64)))
		done
	fi

	if [ "$buildconf" = "multigrid" ]; then
		generate_problem 16
		generate_problem 32
		generate_problem 48
		N=1280
		for i in $(seq 1 10); do
			generate_problem $((N + i * 128))
		done
		N=2560
		for i in $(seq 1 6); do
			generate_problem $((N + i * 256))
		done
	fi
}

# source of virtual Python environment
run_virtual() {
	cd ../Python/ || exit 1
	. ./venv/bin/activate || exit 1
	./run.sh "openblas" "$problempath" "${buildconf}"
	deactivate
}

# source of intel Python environment
run_intel() {
	cd ../Python/ || exit 1
	. ./intelpython3/bin/activate || exit 1
	./run.sh "intel" "$problempath" "${buildconf}"
	# conda deactivate
}

run_d() {
	./benchmark.sh "$problempath" "$1"
}

generate_problems

oldpwd=$(pwd)

cd ../D || exit 1
dub build --force --compiler=ldc2 --build=release-nobounds --config="$buildconf"
for x in "field" "naive" "slice" "ndslice"; do
	run_d "./$buildconf -s $x"
done
cd "$oldpwd" || exit 1

run_intel
cd "$oldpwd" || exit 1

run_virtual
cd "$oldpwd" || exit 1
