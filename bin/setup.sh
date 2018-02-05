#!/bin/bash

# Essentials
echo "Getting essentials"
echo
echo
sudo apt-get -y update
sudo apt-get -y install python-dev build-essential

# Pip and Virtualenv
echo "Getting pip, virtualenv, and pip libraries"
echo
echo
sudo apt-get -y install python-pip
sudo pip install virtualenv
sudo apt-get -y install libcurl4-openssl-dev
sudo apt-get -y install libpq-dev
. activate
pip install https://github.com/djangonauts/django-rest-framework-gis/tarball/master

# Install Postgre and PostGIS
echo "Getting PostgreSQL and PostGIS"
echo
echo
sudo apt-get -y install postgresql-9.5 postgresql-9.5-postgis-2.2 pgadmin3 postgresql-contrib
sudo apt-get -y install libxml2-dev
sudo apt-get -y install libgdal1-dev
sudo apt-get -y install postgis*
wget http://download.osgeo.org/postgis/source/postgis-2.4.3.tar.gz
tar xvzf postgis-2.4.3.tar.gz
cd postgis-2.4.3
./configure
make
make install
sudo su - postgres -c createdb django_test exit

# Install GEOS
echo "Installing GEOS"
echo
echo
sudo apt-get -y install build-essential
sudo apt-get -y install gcc build-essential
sudo apt-get -y install g++ build-essential
wget http://download.osgeo.org/geos/geos-3.6.2.tar.bz2
tar xjf geos-3.6.2.tar.bz2
cd geos-3.6.2
./configure
make
sudo make install
cd ..

# Install PROJ.4
echo "Installing PROJ.4"
echo
echo
wget http://download.osgeo.org/proj/proj-4.9.3.tar.gz
wget http://download.osgeo.org/proj/proj-datumgrid-1.5.tar.gz
tar xzf proj-4.9.3.tar.gz
cd proj-4.9.3/nad
tar xzf ../../proj-datumgrid-1.5.tar.gz
cd ..
./configure
make
sudo make install
cd ..

# Set up PostGIS
echo "Setting up PostGIS"
echo
echo
cd ~/
echo "CREATE USER django_user WITH PASSWORD 'dj4ng0_t3st';CREATE EXTENSION adminpack;CREATE EXTENSION postgis;CREATE EXTENSION postgis_topology;\q" >> psqlCommands.sql
sudo su - postgres -c psql django_test < psqlCommands.sql
echo "All done"
