#!/bin/bash
set -e
wd=$(dirname "$0")

if [[ -z "$1" ]]; then
    echo "You must supply a database engine."
    exit 1
fi

for c in "DecisionTreeClassifier" "MultinomialNB" "RandomForestClassifier"; do
    echo "${c} - Using Neighborhoods"
    python3 ${wd}/crime-model.py --engine-string "${1}" --classifier-name ${c} --force
    echo "${c} - Using Districts"
    python3 ${wd}/crime-model.py --engine-string "${1}" --classifier-name ${c} --use-districts --force
done