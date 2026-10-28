#!/usr/bin/env bash
# Create an index with 1 replica on a single node (goes yellow) and load 3 docs.
set -euo pipefail
ES=${ES:-localhost:9200}

curl -s -X PUT "$ES/orders-lab" -H 'Content-Type: application/json' \
  -d '{"settings":{"number_of_shards":1,"number_of_replicas":1}}'
echo
curl -s -X POST "$ES/orders-lab/_bulk?refresh=true" -H 'Content-Type: application/x-ndjson' \
  --data-binary $'{"index":{}}\n{"order":"order-1","status":"ok","amount":10}\n{"index":{}}\n{"order":"order-2","status":"failed","amount":25}\n{"index":{}}\n{"order":"order-3","status":"ok","amount":40}\n'
echo
curl -s "$ES/_cluster/health?pretty" | grep -E 'status|unassigned_shards'
