# Runbook: RabbitMQ queue backing up

Written from the lab scenarios in this repo (single node, small scale). Adjust thresholds for real workloads.

## Symptom / alert
- Grafana alert "queue depth high" firing (lab threshold: > 50 ready messages).
- Management UI shows messages ready climbing.

## Impact
Messages are delayed or unprocessed; downstream work waits. Unbounded growth eventually pressures memory/disk.

## Diagnose
1. Queue state:
   ```bash
   docker exec lab-rabbitmq rabbitmqctl list_queues name messages_ready messages_unacknowledged consumers
   ```
2. Read the pattern:
   | ready | unacked | consumers | Likely cause |
   |---|---|---|---|
   | rising | 0 | 0 | No consumer running (crashed/not started) |
   | rising | low | >0 | Consumers too slow vs publish rate |
   | low | high and flat | >0 | Consumer receives but doesn't ack (bug/hung) |
   | small, steady | n/a | n/a | Check dead-letter queue for rejected messages |
3. Check the dead-letter queue (`dead_letters` in the lab) and the `x-death` header of a message for the reason and original queue.
4. Check the consumer process/logs.

## Fix
- **No consumers:** restart/start the consumer service; confirm consumers > 0.
- **Slow consumers:** add consumer instances; review prefetch.
- **Unacked stall:** fix or restart the consumer. Unacked messages return to *ready* when its channel closes.
- **Poison messages:** fix the payload/handler; inspect then deal with DLQ messages deliberately. Do not blindly requeue.
- **Purging a queue deletes messages.** Only with the data owner's agreement.

## Verify
- `messages_ready` trending to 0, consumers > 0.
- Alert returns to Normal.

## Escalate
If the consumer owner can't be reached, the queue keeps growing after consumers are healthy, or broker memory/disk alarms appear, escalate to the on-call owner of the application and the broker.
