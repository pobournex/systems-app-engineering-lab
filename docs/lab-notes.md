# Lab notes

Each step: what I did / what broke / how I fixed it, with the screenshot next to it.

## 1. VM and base setup
- **Did:** Created an Ubuntu Server 24.04 VM on a Proxmox VE 9.1 cluster, installed OpenSSH, Docker and Compose.
- **Broke:** Console paste didn't work; SSH timed out though ping worked; installer used only half the disk.
- **Fixed:** Moved to SSH; installed `openssh-server`; `lvextend -r -l +100%FREE`.

## 2. RabbitMQ
**Queue piles up with no consumer.** Published 1,000+ messages with nothing consuming.

![Overview: 1,005 ready, 0 consumers](images/01-queue-piled-up.png)
![Queues page](images/01b-queues-page-piled-up.png)
![list_queues: orders 1005, consumers 0](images/02-list-queues-piled-up.png)

**Drain it.** Started a consumer with prefetch 10 and acks.

![Draining](images/03-draining.png)
![list_queues while draining](images/03b-list-queues-draining.png)
![Recovered](images/04-recovered.png)

**Unacked stall.** A consumer that receives but never acks holds messages unacked; stopping it returns them to ready.

![Unacked stuck](images/05-unacked-stuck.png)
![Requeued](images/06-requeued.png)

**Dead-letter queue.** Rejected "bad" messages with `requeue=false`; they went through the dead-letter exchange to `dead_letters`.

![Overview with the DLQ](images/07a-overview-dlq.png)
![DLQ queue](images/07-dlq-queue.png)
![x-death header](images/08-x-death.png)
![x-death on bad-order-2](images/08-x-death-bad-order-2.png)

- **Learned:** Ready vs unacked vs consumers tells you which failure you have.

## 3. Elasticsearch and Kibana
**Green baseline, then yellow on purpose.** An index with 1 replica on a single node leaves the replica unassigned.

![Green baseline](images/09-es-green-baseline.png)
![Create index with 1 replica](images/10a-es-create-index-replica1.png)
![Yellow](images/10-es-yellow.png)

**Why.** The allocation explain API showed the `same_shard` decider.

![Allocation explain](images/10-es-explain.png)
![Explain, same_shard](images/10b-es-explain-same-shard.png)

**Fix.** Set replicas to 0 (a lab shortcut, not a production fix).

![Green again](images/11-es-green-fixed.png)

**Kibana.** Created a data view (no time field, since the documents have no timestamp) and searched with KQL.

![Kibana home](images/12-kibana-home.png)
![Data view](images/12-kibana-data-view.png)
![Discover](images/12-kibana-discover.png)
![KQL search](images/13-kibana-search.png)

## 4. Metrics
Added static Endpoints, Service and ServiceMonitor objects so the existing Prometheus Operator scrapes the VM, then confirmed targets up and queried both in Grafana Explore.

![Metrics sources](images/14-metrics-sources.png)
![Scrape config applied](images/15-scrape-applied.png)
![Targets up](images/16-prometheus-targets-up.png)
![Grafana: RabbitMQ](images/17-grafana-explore-rabbit.png)
![Grafana: RabbitMQ, second query](images/17-grafana-explore-rabbit2.png)
![Grafana: Elasticsearch](images/18-grafana-explore-es.png)

- **Broke:** Prometheus API query returned `bad_data` from shell quoting.
- **Fixed:** `curl -G --data-urlencode`.

## 5. Alerts
Two Grafana-managed rules in folder `lab`, group `lab-alerts`: queue depth above 50, and ES cluster not green.

![New rule form](images/19c-new-rule-form.png)
![Queue rule detail](images/19e-rule1-detail.png)
![ES rule form](images/19f-rule2-form.png)
![ES rule detail](images/19g-rule2-detail.png)
![Rules list](images/19-alert-rules.png)

- **Broke:** Default threshold 0 would have fired on the 2 DLQ messages; one editor defaulted to "IS ABOVE 1".
- **Fixed:** Threshold 50; changed to "IS BELOW 1" where needed; moved a rule into the right folder.

**Queue alert: fires, then resolves after draining.**

![Overview piled up](images/20c-overview-piled-up.png)
![Queue alert firing](images/20-alert-queue-firing.png)
![Alert instance](images/20b-alert-instance.png)
![Drained](images/21b-drained.png)
![Queue alert resolved](images/21-alert-queue-resolved.png)

**Elasticsearch alert: fires when yellow, resolves after the fix.**

![Trigger yellow](images/22a-es-trigger-yellow.png)
![ES alert pending](images/22b-alert-es-pending.png)
![ES alert firing](images/22-alert-es-firing.png)
![ES alert detail](images/22c-alert-es-detail.png)
![ES alert instance](images/22d-alert-es-instance.png)
![ES alert resolved](images/23-alert-es-resolved.png)
![Both rules Normal](images/23-alerts-normal-final.png)

- **Note:** The one remaining "firing" on the alert page is the built-in Watchdog rule, which is expected.

## 6. Runbooks
Wrote [queue backing up](runbook-queue-backing-up.md) and [Elasticsearch yellow/red](runbook-elasticsearch-yellow-red.md) after the failures above, from what I learned. They were written after the fact and have not been used in a live incident.

## Not done
Camunda, Kafka, NiFi and AD/LDAP were not built.
