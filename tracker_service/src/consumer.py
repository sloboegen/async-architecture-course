from typing import final

from kafka import KafkaConsumer  # type: ignore[import-untyped]


@final
class KafkaTopic:
    ROLE_CHANGED = "role_changed"


def run_kafka_consumer(consumer: KafkaConsumer) -> None:
    consumer.subscribe(topics=[KafkaTopic.ROLE_CHANGED])

    for msg in consumer:
        print(msg)
