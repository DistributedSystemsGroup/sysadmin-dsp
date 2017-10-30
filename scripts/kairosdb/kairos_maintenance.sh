#!/bin/sh

curl -d @trim_history_query.json http://bf5:8090/api/v1/datapoints/delete

