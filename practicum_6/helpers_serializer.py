from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONDeserializer

class SerializerClass:

    def __init__(self):
        self.schema_registry_config = {
            'url': 'http://localhost:8081'
        }

        # Определение JSON-схемы
        self.json_schema_str = """
        {
         "$schema": "http://json-schema.org/draft-07/schema#",
         "title": "Product",
         "type": "object",
         "properties": {
           "id": {
             "type": "integer"
           },
           "message": {
             "type": "string"
           }
         },
         "required": ["id", "message"]
        }
        """

    def serialize(self, message_value: str, topic: str):
        # Инициализация клиента Schema Registry
        schema_registry_client = SchemaRegistryClient(self.schema_registry_config)

        # Создание JSON-сериализатора
        json_serializer = JSONSerializer(self.json_schema_str, schema_registry_client)

        # Сериализация ключа и значения
        key_serializer = StringSerializer('utf_8')
        value_serializer = json_serializer

        key = key_serializer("user_key", SerializationContext(topic, MessageField.VALUE))
        value = value_serializer(message_value, SerializationContext(topic, MessageField.VALUE))

        return key, value

    def deserialize(self, msg):

        json_deserializer = JSONDeserializer(self.json_schema_str)

        value = json_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
        key = msg.key().decode("utf-8") if msg.key() else None

        return key, value





