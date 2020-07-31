#!/bin/bash

let prim_key=900000000
while [[ $prim_key -ge 0 ]]; do
    echo "DELETE FROM video_copyright_protection_metrics WHERE prim_key > $prim_key"
    eval "db -w -u xdb.rm_insights -e 'DELETE FROM video_copyright_protection_metrics WHERE prim_key > $prim_key;'"
    prim_key=$(($prim_key-1000000))
done
