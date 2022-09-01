#!/bin/bash
set -e
export PGPASSWORD=$POSTGRES_PASSWORD;
psql -Upostgres -c 'CREATE DATABASE web;'