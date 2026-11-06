# Systems Application Engineering Lab

A small personal homelab I built to practise running, monitoring and troubleshooting the kind of middleware a systems application engineer supports: a message broker, a search/logging stack, and metrics with alerting. I deliberately broke things, watched the alerts fire, fixed them, and wrote runbooks from what I learned.

> **Lab only.** Everything here runs on a single VM with throwaway credentials. Security is disabled on Elasticsearch for convenience; that must never be done in production.

## Summary in plain language

**RabbitMQ (message broker).** Programs send messages to a queue and other programs pick them up. I broke it three ways and read three counts to find the cause: *ready* (waiting), *unacked* (delivered but not confirmed) and *consumers* (how many are connected). No consumer means a backlog. A consumer that never confirms leaves messages stuck as unacked. A rejected "bad" message goes to a dead-letter queue instead of looping forever.

**Elasticsearch and Kibana (search and logs).** Elasticsearch stores and searches documents, and Kibana is the screen I used to search them. Cluster health is green (all shards assigned), yellow (a replica is not assigned) or red (a primary is not). On one node, an index with a replica went yellow, because a replica cannot sit on the same node as its primary. I found the reason with the allocation explain API and fixed the lab case by setting replicas to 0.

**Prometheus and Grafana (metrics and alerts).** Prometheus collects numbers from RabbitMQ and Elasticsearch on a schedule. Grafana charts them and raises an alert when a rule is true: queue depth above 50, or cluster health not green. I triggered both alerts and watched them fire and resolve.

**Active Directory (LDAP).** From the lab VM I ran read-only LDAP queries against a Windows domain controller: a bind, a list of users in one OU, and a filter by group.

## What I built

| Area | What I did |
|---|---|
| Virtualisation | Built an Ubuntu Server 24.04 VM (ISO install) on a 3-node Proxmox VE 9.1 cluster; extended the LVM volume to use the full disk (`lvextend -r`). |
| Containers | Docker 29 + Compose v5 on the VM. |
| Messaging | RabbitMQ 4.4 with the management UI. Python (pika) producers/consumers. |
| Search / logs | Elasticsearch 8.15.3 (single node) and Kibana 8.15.3. |
| Monitoring | Existing Prometheus Operator stack (kube-prometheus-stack) on a K3s cluster scrapes the VM via static Endpoints/Service/ServiceMonitor. RabbitMQ's built-in Prometheus plugin and the elasticsearch-exporter provide the metrics. |
| Alerting | Two Grafana-managed alert rules (queue backlog, Elasticsearch cluster health) that I triggered, saw fire, and saw resolve. |
| Directory | Ran LDAP queries from the lab VM against an Active Directory domain controller: bind, OU search, group filter (scenario 7). |
| Runbooks | Two: [queue backing up](docs/runbook-queue-backing-up.md) and [Elasticsearch yellow/red](docs/runbook-elasticsearch-yellow-red.md). |

## Architecture

```
            Proxmox VE cluster (3 nodes)
   +---------------------------------------------+
   |  lab VM (Ubuntu 24.04, Docker)              |
   |   RabbitMQ :5672 / :15672 UI / :15692 metrics|
   |   Elasticsearch :9200   Kibana :5601        |
   |   elasticsearch-exporter :9114              |
   +----------------------+----------------------+
                          | scrape (15s)
   +----------------------v----------------------+
   |  K3s: Prometheus Operator (monitoring ns)   |
   |   ServiceMonitors -> Prometheus -> Grafana  |
   |                          alert rules        |
   +---------------------------------------------+
```

## Scenarios I ran

1. **Queue piles up with no consumers.** Published 1,000+ messages to a durable `orders` queue with no consumer. Management UI showed ~1,005 ready, 0 consumers. Started a consumer and watched it drain. ([screenshots 01-04](docs/images/README.md))
2. **Stuck unacked messages.** A consumer that receives but never acks held 10 messages unacked (prefetch 10). Stopping it returned them to *ready*. ([05-06](docs/images/README.md))
3. **Poison messages and a dead-letter queue.** Rejected messages with `requeue=false` were routed through a dead-letter exchange to `dead_letters`; inspected the `x-death` header. ([07-08](docs/images/README.md))
4. **Elasticsearch goes yellow.** An index with 1 replica on a single node leaves the replica shard unassigned. `_cluster/allocation/explain` showed the `same_shard` decider. Fixed by setting replicas to 0 (fine for a lab, not a fix for production). ([09-11](docs/images/README.md))
5. **Kibana.** Created a data view and searched documents in Discover with KQL. ([12-13](docs/images/README.md))
6. **Metrics and alerts.** Verified Prometheus targets up, queried both sources in Grafana Explore, built the two alert rules, and triggered and resolved each. ([14-23](docs/images/README.md))
7. **LDAP against Active Directory.** From the lab VM I confirmed the domain controller answered on port 389, bound as a lab user, listed the 5 users in an OU with their group memberships, and filtered for the members of one group (2 users). That matched the Members tab in AD Users and Computers. My first bind failed with `Invalid credentials (49)` because I had typed a placeholder instead of a real account. ([28-30](docs/images/README.md))

## Screenshots

<table>
<tr>
<td><img src="docs/images/01-queue-piled-up.png" width="420"><br><sub>Queue piled up: 1,005 ready, 0 consumers</sub></td>
<td><img src="docs/images/03-draining.png" width="420"><br><sub>Consumer attached, queue draining</sub></td>
</tr>
<tr>
<td><img src="docs/images/08-x-death.png" width="420"><br><sub>Dead-lettered message and its <code>x-death</code> header</sub></td>
<td><img src="docs/images/10-es-explain.png" width="420"><br><sub>Elasticsearch yellow: allocation explain</sub></td>
</tr>
<tr>
<td><img src="docs/images/20-alert-queue-firing.png" width="420"><br><sub>Queue alert firing</sub></td>
<td><img src="docs/images/23-alert-es-resolved.png" width="420"><br><sub>Elasticsearch alert back to Normal</sub></td>
</tr>
</table>

All 50+ screenshots, step by step with notes: [docs/lab-notes.md](docs/lab-notes.md).

## Run it yourself

Prerequisites: a Linux VM with Docker and Compose, Python 3.

```bash
# RabbitMQ
cd rabbitmq
cp .env.example .env        # set a lab-only password
set -a; . ./.env; set +a   # loads RABBITMQ_USER / RABBITMQ_PASS into your shell
docker compose up -d
pip install -r requirements.txt
python producer.py 1000
python consumer.py

# Elasticsearch + Kibana + exporter
cd ../elk
docker compose up -d
./load-sample-data.sh
curl -s localhost:9200/_cluster/health?pretty
```

To have an existing Prometheus Operator scrape the VM, edit `LAB_VM_IP` in [`k8s/lab-scrape.yaml`](k8s/lab-scrape.yaml) and `kubectl apply -f` it.

Useful checks:

```bash
docker exec lab-rabbitmq rabbitmqctl list_queues name messages_ready messages_unacknowledged consumers
curl -s "localhost:9200/_cluster/allocation/explain?pretty"
curl -s -G 'localhost:9090/api/v1/query' --data-urlencode 'query=up{job=~"lab-.*"}'
```

## What I got wrong along the way

- Pasting into the Proxmox web console didn't work, so I switched to SSH.
- SSH timed out even though ping worked: `openssh-server` wasn't installed.
- The installer's default LVM layout used only half the disk; fixed with `lvextend -r -l +100%FREE`.
- A Prometheus API query failed from shell quoting; fixed with `curl -G --data-urlencode`.
- The Grafana alert default threshold (0) would have fired on the 2 messages sitting in the DLQ; I set it to 50.
- One alert editor defaulted to "IS ABOVE"; the no-data rule needed "IS BELOW".

Full detail in [docs/lab-notes.md](docs/lab-notes.md).

## Honest limits

- Scale is tiny: ~1,000 messages, a single-node Elasticsearch, one VM.
- Elasticsearch security is off (lab only). Production needs TLS, authentication and roles.
- Single-node ES with replicas=0 has no redundancy.
- RabbitMQ is a single node, no clustering or quorum-queue tuning.

## Not built

I did **not** build or run these, so nothing here claims experience with them: Camunda, Kafka, NiFi. They are next on my learning list.

Active Directory/LDAP is only partly covered: read-only LDAP queries from the lab VM against a lab domain controller over plain LDAP (port 389). No application signs in against it, the VM is not domain-joined, and I did not test LDAPS.

## Layout

```
rabbitmq/   compose, pika scripts
elk/        compose (ES, Kibana, exporter), sample data script
k8s/        scrape config for Prometheus Operator
docs/       runbooks, lab notes, screenshots
```
