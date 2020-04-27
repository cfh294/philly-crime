#!/bin/bash
set -e
wd=$(dirname "$0")

if [[ -z "$1" ]]; then
    echo "You must supply a database engine."
    exit 1
fi

for c in "DecisionTreeClassifier" "MultinomialNB" "RandomForestClassifier"; do
    echo "${c} - Using Neighborhoods"
    python3 ${wd}/crime-model.py --engine-string "${1}" --date "04/26/2020" --hour 12 --area-id 8 --classifier-name ${c}
    echo "${c} - Using Districts"
    python3 ${wd}/crime-model.py --engine-string "${1}" --date "04/26/2020" --hour 12 --area-id 8 --classifier-name ${c} --use-districts
done