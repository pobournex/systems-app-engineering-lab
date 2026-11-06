# Runbook: Dead-letter queue recovery

Queue: `dead_letters`. Related: runbook-queue-backing-up.md

## 1. Inspect
- RabbitMQ UI: Queues > `dead_letters` > Get messages
- Read the `x-death` header: it shows the original queue and the reason (rejected, expired, max-length)

## 2. Decide
- Consumer bug or temporary failure: fix the cause first, then requeue
- Poison message (bad data that will never succeed): purge it and record why

## 3. Recover
- Requeue: move messages back to the original queue (shovel or republish)
- Purge: Queues > `dead_letters` > Purge Messages

## 4. Verify
- `dead_letters` depth returns to 0
- The original queue's consumers are processing normally
