# Screenshot index

Put your own screenshots in this folder using these filenames (PNG). Before committing, **crop or blur** anything that shows real hostnames of other systems, workloads that aren't part of this lab, personal or business names, emails, or tokens. Tick the box once checked.

| File | Shows | Step | Checked |
|---|---|---|---|
| 01-queue-piled-up.png | Management UI: ~1,005 ready, 0 consumers | RabbitMQ | [ ] |
| 02-list-queues-piled-up.png | `rabbitmqctl list_queues` output while piled up | RabbitMQ | [ ] |
| 03-draining.png | Queue draining with consumer running | RabbitMQ | [ ] |
| 04-recovered.png | Queue at 0 | RabbitMQ | [ ] |
| 05-unacked-stall.png | 10 unacked, consumer not acking | RabbitMQ | [ ] |
| 06-requeued.png | Messages back to ready after consumer stopped | RabbitMQ | [ ] |
| 07-dlq.png | `dead_letters` holding rejected messages | DLQ | [ ] |
| 08-x-death.png | `x-death` header on bad-order-2 / bad-order-4 | DLQ | [ ] |
| 09-es-green.png | Cluster health green baseline | ES | [ ] |
| 10-es-yellow-explain.png | Yellow with allocation explain (`same_shard`) | ES | [ ] |
| 11-es-green-fixed.png | Green after replicas set to 0 | ES | [ ] |
| 12-kibana-data-view.png | Kibana data view created | Kibana | [ ] |
| 13-kibana-discover.png | Discover with a KQL search | Kibana | [ ] |
| 14-metrics-sources.png | Metrics endpoints on the VM | Metrics | [ ] |
| 15-scrape-applied.png | `kubectl apply` of scrape config | Metrics | [ ] |
| 16-targets-up.png | Prometheus targets up | Metrics | [ ] |
| 17-grafana-rabbitmq.png | Grafana Explore: RabbitMQ metric | Metrics | [ ] |
| 18-grafana-es.png | Grafana Explore: Elasticsearch metric | Metrics | [ ] |
| 19-alert-rules.png | Alert rules list | Alerts | [ ] |
| 20-queue-alert-firing.png | Queue alert firing at 1,002 | Alerts | [ ] |
| 21-queue-alert-resolved.png | Queue alert resolved | Alerts | [ ] |
| 22-es-alert-firing.png | ES alert firing | Alerts | [ ] |
| 23-es-alert-resolved.png | ES alert resolved | Alerts | [ ] |

Extras you captured (`20c`, `21b`, `22c`, `22d`, `22e`, `23a`) can be added to this table with a one-line description each.
