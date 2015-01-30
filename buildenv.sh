#!/bin/bash
#http://habrahabr.ru/post/114745/
mkdir -p reports

#REPO="http://127.0.0.1:8888"
#echo Checking for local repo at ${REPO}
#curl -f --head ${REPO} > /dev/null 2>&1 || REPO='http://pypi.python.org/simple'
#echo "... will use ${REPO}"

echo 'Creating "venv" environment...'
$1/jobs/python-2.7.9/bin/virtualenv --distribute --no-site-packages venv

echo 'Installing dependencies to "venv" environment...'

if [ x$1 == x"--ci" ]; then
echo "Testing mode."
PIP=reqs
else
echo "Dev/deploy mode."
PIP=stuff
fi

./venv/bin/pip install -q --upgrade pip
./venv/bin/pip install -q pep8
./venv/bin/pip install -q pylint
./venv/bin/pip install -q coverage
./venv/bin/pip install -q nose

$1/jobs/python-2.7.9/bin/virtualenv --relocatable venv


#==================================
venv/bin/pep8 --repeat --ignore=E501,W391 project > reports/pep8.report #| perl -ple 's/: ([WE]\d+)/: [$1]/' > reports/pep8.report
venv/bin/pylint --rcfile pylint.rc project/*.py > reports/pylint.report
echo "pylint complete"
#==================================
venv/bin/coverage run --include 'project/*.py' project/tests.py --with-xunit --xunit-file=reports/tests.xml --where=project
venv/bin/coverage xml -o reports/coverage.xml
#==================================
rm -rf venv
