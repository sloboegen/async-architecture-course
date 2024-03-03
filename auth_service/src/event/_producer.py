from kafka import KafkaProducer


class MsgProducer:
    def __init__(self) -> None:
        self._producer = KafkaProducer()
