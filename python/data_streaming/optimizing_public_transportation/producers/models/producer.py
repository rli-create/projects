"""Producer base-class providing common utilites and functionality"""
import logging
import time

from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroProducer, CachedSchemaRegistryClient

logger = logging.getLogger(__name__)

BROKER_URL = "PLAINTEXT://localhost:9092"
SCHEMA_REGISTRY_URL = "http://localhost:8081"


class Producer:
    """Defines and provides common functionality amongst Producers"""

    # Tracks existing topics across all Producer instances
    existing_topics = set([])

    def __init__(
            self,
            topic_name,
            key_schema,
            value_schema=None,
            num_partitions=1,
            num_replicas=1,
    ):
        """Initializes a Producer object with basic settings"""
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas

        #
        #
        # TODO: Configure the broker properties below. Make sure to reference the project README
        # and use the Host URL for Kafka and Schema Registry!
        #
        #
        self.broker_properties = {
            "bootstrap.servers": BROKER_URL
        }

        # If the topic does not already exist, try to create it
        if self.topic_name not in Producer.existing_topics:
            self.create_topic()
            Producer.existing_topics.add(self.topic_name)

        # TODO: Configure the AvroProducer
        schema_registry = CachedSchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
        self.producer = AvroProducer(self.broker_properties, schema_registry=schema_registry)

    def create_topic(self):
        """Creates the producer topic if it does not already exist"""
        #
        # TODO: Write code that creates the topic for this producer if it does not already exist on
        # the Kafka Broker.
        #
        client = AdminClient({"bootstrap.servers": BROKER_URL})
        futures = client.create_topics(
            [
                NewTopic(
                    topic=self.topic_name,
                    num_partitions=3,
                    replication_factor=1,
                    config={
                        "cleanup.policy": "compact",
                        "compression.type": "lz4",
                        "delete.retention.ms": 100,
                        "file.delete.delay.ms": 100
                    }
                )
            ]
        )
        for topic, future in futures.items():
            try:
                future.result()
                logger.info("topic: {} created".format(topic))
            except Exception as e:
                logger.info("topic: {} creation kafka integration incomplete - skipping".format(topic))
                raise

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        #
        #
        # TODO: Write cleanup code for the Producer here
        #
        #
        client = AdminClient({"bootstrap.servers": BROKER_URL})
        try:
            client.delete_topics(Producer.existing_topics)
        except Exception as e:
            logger.info("producer close incomplete - skipping")
            raise

    def time_millis(self):
        """Use this function to get the key for Kafka Events"""
        return int(round(time.time() * 1000))
