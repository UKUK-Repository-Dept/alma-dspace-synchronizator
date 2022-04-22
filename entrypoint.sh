#!/bin/bash
echo "Starting sysno-alma-dspace-sychronizator"

echo "Processing params: MODE=$MODE LIMIT=$LIMIT"

if [[ -z "$LIMIT" ]]  # no limit
  then
    echo "LIMIT is empty string, there is no limit."
    echo "Starting processing in MODE $MODE without a limit."
    python alma-dspace-synchronizer.py -m $MODE
  else
    echo "Starting processing in MODE=$MODE with LIMIT = $LIMIT"
    python alma-dspace-synchronizer.py -m $MODE -l $LIMIT
fi