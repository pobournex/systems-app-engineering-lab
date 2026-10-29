# Screenshots

Evidence from the lab, grouped by scenario. Filenames match the steps in the main README and `docs/lab-notes.md`.

## RabbitMQ: queue backs up, drains, unacked stall
| File | Shows |
|---|---|
| 01-queue-piled-up.png | Overview: 1,005 ready, 0 consumers |
| 01b-queues-page-piled-up.png | Queues page: `orders` with 1,005 ready |
| 02-list-queues-piled-up.png | `rabbitmqctl list_queues`: orders 1005, consumers 0 |
| 02a-pika-install-producer-test.png | pika installed; test producer sends 5 messages |
| 03-draining.png | Overview while draining: 501 ready, 10 unacked, 1 consumer |
| 03b-list-queues-draining.png | `list_queues` while draining |
| 04-recovered.png | Queue drained |
| 05-unacked-stuck.png | Messages held unacked by a consumer that never acks |
| 06-requeued.png | After stopping that consumer: 100 ready, 0 unacked, 0 consumers |
| 20c-overview-piled-up.png | Overview with the queue piled up (used for the alert test) |
| 21b-drained.png | Queue drained after the alert test |

## RabbitMQ: dead-letter queue
| File | Shows |
|---|---|
| 07-dlq-queue.png, 07-dlq-queues.png | Dead-letter queue views |
| 07a-overview-dlq.png | Overview with the DLQ in place (3 queues, 2 ready) |
| 08-x-death.png | `x-death` header on a dead-lettered message |
| 08-x-death-bad-order-2.png | `x-death` header on `bad-order-2` |

## Elasticsearch and Kibana
| File | Shows |
|---|---|
| 09-es-green-baseline.png | Cluster health green |
| 10a-es-create-index-replica1.png | Creating an index with 1 replica on a single node |
| 10-es-yellow.png | Cluster yellow, 1 unassigned shard |
| 10-es-explain.png, 10b-es-explain-same-shard.png | Allocation explain: `same_shard` decider |
| 11-es-green-fixed.png | Green after setting replicas to 0 |
| 12-kibana-home.png, 12-kibana-data-view.png, 12-kibana-discover.png | Kibana home, data view, Discover |
| 13-kibana-search.png | KQL search |

## Metrics
| File | Shows |
|---|---|
| 14-metrics-sources.png | Metrics endpoints on the lab VM |
| 15-scrape-applied.png | Scrape config applied to the cluster |
| 16-prometheus-targets-up.png | Prometheus targets up |
| 17-grafana-explore-rabbit.png, 17-grafana-explore-rabbit2.png | Grafana Explore: RabbitMQ metrics |
| 18-grafana-explore-es.png | Grafana Explore: Elasticsearch metrics |

## Alerting
| File | Shows |
|---|---|
| 19-alert-rules.png | Alert rules list |
| 19a-rule1-preview.png, 19b-rule2-preview.png, 19b-rule2.png | Rule previews and editor |
| 19c-new-rule-form.png | New rule form (queue depth) |
| 19e-rule1-detail.png | Queue rule detail, threshold above 50 |
| 19f-rule2-form.png, 19g-rule2-detail.png | Elasticsearch rule form and detail, "is below 1" |
| 19h-rules-one-pending.png | Rules list with one rule pending |
| 20-alert-queue-firing.png, 20b-alert-instance.png | Queue alert firing and its instance |
| 21-alert-queue-resolved.png | Queue alert resolved |
| 22a-es-trigger-yellow.png | Setting replicas to 1 to turn the cluster yellow |
| 22-alert-es-firing.png, 22b-alert-es-pending.png | ES alert firing and pending |
| 22c-alert-es-detail.png, 22d-alert-es-instance.png | ES alert detail and instance |
| 23-alert-es-resolved.png | ES alert resolved: rule back to Normal after replicas set to 0 |
| 23-alerts-normal-final.png | Both lab rules back to Normal |
