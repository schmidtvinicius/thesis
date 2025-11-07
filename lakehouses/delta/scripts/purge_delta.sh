#!/bin/bash

cd unitycatalog-main
bin/uc table delete --full_name unity.default.$1
cd ..
rm -rf spark-warehouse/$1