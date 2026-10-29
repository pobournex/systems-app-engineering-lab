# Runbook: Elasticsearch cluster yellow or red

Written from the lab scenario (single node). Production clusters need more care.

## Symptom / alert
- Grafana alert on cluster health firing.
- `_cluster/health` status is `yellow` or `red`.

## Meaning
- **Green:** all shards assigned.
- **Yellow:** all primaries assigned, some replicas not. Data is available but redundancy is reduced.
- **Red:** at least one primary shard is unassigned. Some data is unavailable.

## Diagnose
1. Health:
   ```bash
   curl -s localhost:9200/_cluster/health?pretty
   ```
2. Which shards:
   ```bash
   curl -s "localhost:9200/_cat/shards?v" | grep -i unassigned
   ```
3. Why:
   ```bash
   curl -s "localhost:9200/_cluster/allocation/explain?pretty" | grep -A3 '"decider"'
   ```
   In the lab the decider was `same_shard`: a replica cannot live on the same node as its primary, and there was only one node.
4. Also check disk space, node count and recent node restarts.

## Fix
- **Single-node lab yellow:** set replicas to 0 for the lab index:
  ```bash
  curl -s -X PUT localhost:9200/orders-lab/_settings -H 'Content-Type: application/json' \
    -d '{"index":{"number_of_replicas":0}}'
  ```
  This removes redundancy. It is a lab shortcut, not a production fix.
- **Production yellow:** bring the missing node back or add capacity so replicas can be assigned.
- **Red:** find why the primary is unassigned (node down, disk, corruption) using the explain API. Do not delete indices or force allocation without the data owner's approval and a restore path.

## Verify
- Health returns to `green` and unassigned shards = 0.
- Alert returns to Normal.

## Security note
The lab runs with Elasticsearch security disabled. Production must have security enabled.

## Escalate
Red status, no recoverable node, disk alarms, or any step that could lose data: escalate to the on-call owner for the search platform.
