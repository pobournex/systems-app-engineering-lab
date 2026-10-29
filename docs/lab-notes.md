# Lab notes

Each entry: what I did / what broke / how I fixed it.

## 1. VM and base setup
- **Did:** Created an Ubuntu Server 24.04 VM on a Proxmox VE 9.1 cluster, installed OpenSSH, Docker and Compose.
- **Broke:** Console paste didn't work; SSH timed out though ping worked; installer used only half the disk.
- **Fixed:** Moved to SSH; installed `openssh-server`; `lvextend -r -l +100%FREE`.

## 2. RabbitMQ
- **Did:** Ran RabbitMQ 4 with management UI via Compose. Wrote pika producer/consumer scripts. Published 1,000+ messages with no consumer (queue piled up, 0 consumers), then drained it with a consumer using prefetch 10 and acks.
- **Did:** Ran a consumer that never acks; saw 10 unacked; stopped it and saw them go back to ready.
- **Did:** Built a dead-letter exchange and queue; rejected "bad" messages with `requeue=false`; read the `x-death` header.
- **Learned:** Ready vs unacked vs consumers tells you which failure you have.

## 3. Elasticsearch and Kibana
- **Did:** Single-node ES 8.15.3 and Kibana via Compose (security off, lab only). Loaded 3 documents.
- **Broke (on purpose):** Index with 1 replica on one node went yellow.
- **Fixed:** Used the allocation explain API (`same_shard`), set replicas to 0, back to green.
- **Did:** Created a Kibana data view (no time field, since the documents have no timestamp) and searched in Discover with KQL.

## 4. Metrics
- **Did:** Found the existing kube-prometheus-stack. Added static Endpoints, Service and ServiceMonitor objects for RabbitMQ (15692) and the elasticsearch-exporter (9114). Confirmed targets `up` in Prometheus and queried both in Grafana Explore.
- **Broke:** Prometheus API query returned `bad_data` from shell quoting.
- **Fixed:** `curl -G --data-urlencode`.

## 5. Alerts
- **Did:** Two Grafana-managed rules in folder `lab`, group `lab-alerts`: queue depth, and ES cluster health.
- **Broke:** Default threshold 0 would have fired on the 2 DLQ messages; one editor defaulted to "IS ABOVE 1".
- **Fixed:** Threshold 50; changed to "IS BELOW 1" where needed; moved a rule into the right folder.
- **Tested:** Queue alert fired at 1,002 messages and resolved after draining. ES alert fired when the cluster went yellow and resolved after the replica fix.
- **Note:** The one remaining "firing" on the alert page is the built-in Watchdog rule, which is expected.

## 6. Runbooks
Wrote the two runbooks in this folder after the failures above, from what I learned. They were written after the fact and have not been used in a live incident.

## Not done
Camunda, Kafka, NiFi and AD/LDAP were not built.
