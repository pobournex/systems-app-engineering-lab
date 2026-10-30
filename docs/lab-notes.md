# Lab notes

Each step: what I did, what broke, how I fixed it, with the screenshot and a one-line note on what it shows.

## 1. VM and base setup
- **Did:** Built a new Ubuntu Server 24.04 VM from the ISO on a Proxmox VE 9.1 cluster (not a clone), then installed OpenSSH, Docker and Compose.
- **Broke:** Console paste didn't work; SSH timed out though ping worked; installer used only half the disk.
- **Fixed:** Moved to SSH; installed `openssh-server`; `lvextend -r -l +100%FREE`.

## 2. RabbitMQ

### Queue piles up with no consumer
I installed pika and sent 5 test messages, then 1,000 more with nothing consuming.

![pika install and test producer](images/02a-pika-install-producer-test.png)
*pika installed; the producer sends 5 messages and `list_queues` shows `orders` with 5.*

![Overview, piled up](images/01-queue-piled-up.png)
*Overview: 1,005 ready, 0 unacked, 0 consumers.*

![Queues page](images/01b-queues-page-piled-up.png)
*Queues page: the durable `orders` queue holds 1,005 ready messages.*

![list_queues, piled up](images/02-list-queues-piled-up.png)
*`rabbitmqctl list_queues`: orders 1005, consumers 0.*

### Drain it
I started a consumer with prefetch 10 and acks.

![Draining](images/03-draining.png)
*Overview while draining: 501 ready, 10 unacked, 1 consumer, about 20 messages/s.*

![list_queues, draining](images/03b-list-queues-draining.png)
*`list_queues` mid-drain: 90 ready, 10 unacked, 1 consumer.*

![Recovered](images/04-recovered.png)
*Queue back to empty after the drain.*

### Unacked stall
A consumer that receives but never acks holds messages unacked. Stopping it returns them to ready.

![Unacked stuck](images/05-unacked-stuck.png)
*Messages held unacked by the non-acking consumer.*

![Requeued](images/06-requeued.png)
*After stopping it: 100 ready, 0 unacked, 0 consumers. The messages went back to ready.*

### Dead-letter queue
I rejected "bad" messages with `requeue=false`. They went through the dead-letter exchange to `dead_letters`.

![Overview with DLQ](images/07a-overview-dlq.png)
*Overview with 3 queues and 2 ready messages (the dead letters).*

![DLQ queue](images/07-dlq-queue.png)
*The `dead_letters` queue holding the rejected messages.*

![DLQ queues](images/07-dlq-queues.png)
*Queues list showing the demo queue and the dead-letter queue.*

![x-death header](images/08-x-death.png)
*The `x-death` header on a dead-lettered message: original queue and reason.*

![x-death on bad-order-2](images/08-x-death-bad-order-2.png)
*The same header on `bad-order-2`.*

**Learned:** ready vs unacked vs consumers tells you which failure you have.

## 3. Elasticsearch and Kibana

### Green, then yellow on purpose
![Green baseline](images/09-es-green-baseline.png)
*Cluster health green before the change.*

![Create index with 1 replica](images/10a-es-create-index-replica1.png)
*Creating `orders-lab` with 1 replica on a single node.*

![Yellow](images/10-es-yellow.png)
*Cluster yellow with an unassigned replica shard.*

### Why
![Allocation explain](images/10-es-explain.png)
*Allocation explain output.*

![Explain, same_shard](images/10b-es-explain-same-shard.png)
*Decider `same_shard`: a copy of the shard is already on this node, so the replica can't be placed.*

### Fix
Set replicas to 0. This is a lab shortcut, not a production fix.

![Green again](images/11-es-green-fixed.png)
*Cluster green, 0 unassigned shards.*

### Kibana
I created a data view (no time field, because the documents have no timestamp) and searched with KQL.

![Kibana home](images/12-kibana-home.png)
*Kibana home.*

![Data view](images/12-kibana-data-view.png)
*Creating the data view for `orders-lab`.*

![Discover](images/12-kibana-discover.png)
*Discover listing the documents.*

![KQL search](images/13-kibana-search.png)
*A KQL query filtering the documents.*

## 4. Metrics
I added static Endpoints, Service and ServiceMonitor objects so the existing Prometheus Operator scrapes the VM.

![Metrics sources](images/14-metrics-sources.png)
*The metrics endpoints exposed on the lab VM.*

![Scrape config applied](images/15-scrape-applied.png)
*`kubectl apply` of the scrape config.*

![Targets up](images/16-prometheus-targets-up.png)
*Prometheus showing the lab targets as up.*

![Grafana RabbitMQ](images/17-grafana-explore-rabbit.png)
*Grafana Explore: a RabbitMQ metric.*

![Grafana RabbitMQ 2](images/17-grafana-explore-rabbit2.png)
*A second RabbitMQ query.*

![Grafana Elasticsearch](images/18-grafana-explore-es.png)
*Grafana Explore: an Elasticsearch metric from the exporter.*

- **Broke:** the Prometheus API query returned `bad_data` from shell quoting.
- **Fixed:** `curl -G --data-urlencode`.

## 5. Alerts
Two Grafana-managed rules in folder `lab`, group `lab-alerts`: queue depth above 50, and Elasticsearch cluster not green.

![Rule 1 preview](images/19a-rule1-preview.png)
*Previewing the queue rule's condition.*

![New rule form](images/19c-new-rule-form.png)
*The queue rule editor with the default threshold still at 0 (IS ABOVE 0). That would have fired on the 2 messages in the DLQ.*

![Rule 1 detail](images/19e-rule1-detail.png)
*After the fix: threshold above 50, current value 2, state Normal.*

![Rule 2 form](images/19f-rule2-form.png)
*The Elasticsearch rule editor, querying `elasticsearch_cluster_health_status{color="green"}`.*

![Rule 2 editor](images/19b-rule2.png)
*Changing the condition for rule 2.*

![Rule 2 preview](images/19b-rule2-preview.png)
*Previewing rule 2.*

![Rule 2 detail](images/19g-rule2-detail.png)
*Rule 2 saved as "is below 1", state Normal.*

![Rules list](images/19-alert-rules.png)
*Both rules in `lab > lab-alerts`, Normal.*

![Rules list, one pending](images/19h-rules-one-pending.png)
*Rules list while one rule is pending.*

- **Broke:** default threshold 0, and one editor defaulted to "IS ABOVE 1".
- **Fixed:** threshold 50; changed to "IS BELOW 1"; moved a rule into the right folder.

### Queue alert: fires, then resolves after draining
![Overview piled up](images/20c-overview-piled-up.png)
*Queue piled up for the test.*

![Queue alert firing](images/20-alert-queue-firing.png)
*The queue alert firing.*

![Alert instance](images/20b-alert-instance.png)
*The firing alert's instance and labels.*

![Drained](images/21b-drained.png)
*Queue drained.*

![Queue alert resolved](images/21-alert-queue-resolved.png)
*The queue alert back to Normal.*

### Elasticsearch alert: fires when yellow, resolves after the fix
![Trigger yellow](images/22a-es-trigger-yellow.png)
*Setting replicas to 1 to turn the cluster yellow: `unassigned_shards: 1`.*

![ES alert pending](images/22b-alert-es-pending.png)
*The rule pending before it fires.*

![ES alert firing](images/22-alert-es-firing.png)
*The Elasticsearch alert firing.*

![ES alert detail](images/22c-alert-es-detail.png)
*Alert detail while firing.*

![ES alert instance](images/22d-alert-es-instance.png)
*The firing instance and its labels.*

![ES alert resolved](images/23-alert-es-resolved.png)
*After setting replicas back to 0: both rules Normal.*

![Both rules Normal](images/23-alerts-normal-final.png)
*Final state: both lab rules Normal.*

**Note:** the one remaining "firing" on the alert page is the built-in Watchdog rule, which is expected.

## 6. Runbooks
I wrote [queue backing up](runbook-queue-backing-up.md) and [Elasticsearch yellow/red](runbook-elasticsearch-yellow-red.md) after the failures above, from what I learned. They were written after the fact and have not been used in a live incident.

## 7. LDAP against Active Directory
- **Did:** Installed `ldap-utils` on the lab VM. Confirmed port 389 on the domain controller was reachable and that it answered an anonymous root DSE query. Bound as a lab user and searched the `LabUsers` OU for users with `sAMAccountName` and `memberOf`: 5 users. Filtered on `memberOf` for the IT-Staff group: 2 users, matching the group's Members tab in AD Users and Computers.
- **Broke:** First bind returned `Invalid credentials (49)`, data `52e`. I had typed a placeholder instead of a real account name.
- **Fixed:** Used the real account. The server was reachable the whole time, so the problem was what I sent.
- **Note:** Plain LDAP on 389 sends the password unencrypted. Lab only; production needs LDAPS (636) or StartTLS.

![LDAP search of the LabUsers OU returning 5 users and their groups](images/28-ldap-bind-search.png)
![LDAP filter for IT-Staff members returning 2 users](images/29-ldap-group-filter.png)
![IT-Staff members as shown in AD Users and Computers](images/30-ad-itstaff-members.png)

## Not done
Camunda, Kafka and NiFi were not built. AD/LDAP is covered only as read-only queries (section 7).
