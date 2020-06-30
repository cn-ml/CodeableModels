"""
*File Name:* metamodels/microservice_components_metamodel.py

This is an extension of the component metamodel in :ref:`component_metamodel`.
It provides many ``component_type`` and ``connector_type`` subclasses for modelling various concepts
found in microservices and other service-based systems.

"""

from metamodels.component_metamodel import *

# Component types
service = CStereotype("Service", superclasses=component_type)
database = CStereotype("Database", superclasses=component_type)
pub_sub_component = CStereotype("Pub/Sub Component", superclasses=component_type)
message_broker = CStereotype("Message Broker", superclasses=component_type)
# a component that provides event sourcing, could be e.g. on a pub/sub component as an additional function
# or on a component listening to events
event_sourcing = CStereotype("Event Sourcing", superclasses=component_type)
# stream-processing platforms like Kafka process events and messages, and keep a persistent distributed
# log of those, which can be used for eventSourcing; thus they combine abilities of all of those
stream_processing = CStereotype("Stream Processing", superclasses=[pub_sub_component, message_broker, event_sourcing])

external_component = CStereotype("External Component", superclasses=component_type)
facade = CStereotype("Facade", superclasses=component_type)

client = CStereotype("Client", superclasses=external_component)
web_ui = CStereotype("Web UI", superclasses=facade)

in_memory_data_store = CStereotype("In-Memory Data Store", superclasses=database)
postgresql_db = CStereotype("PostgreSQL DB", superclasses=database)
mysql_db = CStereotype("MySQL DB", superclasses=database)
sql_server = CStereotype("SQL Server", superclasses=database)
mongo_db = CStereotype("Mongo DB", superclasses=database)
ldap_store = CStereotype("LDAP Store", superclasses=database)
elastic_search_store = CStereotype("Elastic Search Store", superclasses=database)
memcached_db = CStereotype("Memcached DB", superclasses=database)
redis_db = CStereotype("Redis DB", superclasses=database)
event_store = CStereotype("Event Store", superclasses=database)

monitoring_component = CStereotype("Monitoring", superclasses=component_type)
tracing_component = CStereotype("Tracing", superclasses=component_type)
logging_component = CStereotype("Logging", superclasses=component_type)

orchestrator = CStereotype("Orchestrator", superclasses=component_type)
saga_orchestrator = CStereotype("Saga Orchestrator", superclasses=orchestrator,
                                attributes={"sagas": list})

# Connector types
directed = CStereotype("Directed", superclasses=connector_type)

# use synchronousConnector especially if connector implies asynchronous communication
# (as in messaging), but is used synchronously
synchronous_connector = CStereotype("Synchronous", superclasses=connector_type)
# use asynchronousConnector especially if connector implies synchronous communication
# (as in restful_http), but is used asynchronously
asynchronous_connector = CStereotype("Asynchronous", superclasses=connector_type)
# use both syncAsyncConnector, if both forms are mixed (or leave unspecified)
sync_async_connector = CStereotype("Synchronous + Asynchronous",
                                   superclasses=[synchronous_connector, asynchronous_connector])

callback = CStereotype("Callback", superclasses=asynchronous_connector)
polling = CStereotype("Polling", superclasses=asynchronous_connector)
one_way = CStereotype("One Way", superclasses=asynchronous_connector)

indirect_relation_via_api = CStereotype("Indirect Relation via API", superclasses=connector_type)

in_memory_connector = CStereotype("In-Memory Connector", superclasses=connector_type)
database_connector = CStereotype("Database Connector", superclasses=connector_type,
                                 attributes={"read": list, "write": list, "read + write": list})
service_connector = CStereotype("Service Connector", superclasses=connector_type)
web_connector = CStereotype("Web Connector", superclasses=connector_type)
loosely_coupled_connector = CStereotype("Loosely Coupled Connector", superclasses=connector_type)
ldap = CStereotype("LDAP", superclasses=connector_type)
memcached_connector = CStereotype("Memcached Connector", superclasses=connector_type)
messaging = CStereotype("Messaging", superclasses=connector_type)
event_based_connector = CStereotype("Event-Based Connector", superclasses=loosely_coupled_connector)

publisher = CStereotype("Publisher", superclasses=event_based_connector,
                        attributes={"publishes": list})
subscriber = CStereotype("Subscriber", superclasses=event_based_connector,
                         attributes={"subscribesTo": list})

message_producer = CStereotype("Message Producer", superclasses=messaging, attributes={"outChannels": list})
message_consumer = CStereotype("Message Consumer", superclasses=messaging, attributes={"inChannels": list})

jdbc = CStereotype("JDBC", superclasses=database_connector)
odbc = CStereotype("ODBC", superclasses=database_connector)
mongo_wire = CStereotype("Mongo Wire", superclasses=database_connector)
hdfs = CStereotype("HDFS", superclasses=database_connector)
resp = CStereotype("RESP", superclasses=database_connector)
mysql_protocol = CStereotype("MySQL Protocol", superclasses=database_connector)

restful_http = CStereotype("RESTful HTTP", superclasses=service_connector)
soap = CStereotype("SOAP", superclasses=service_connector)
avro = CStereotype("AVRO", superclasses=service_connector)
grpc = CStereotype("GRPC", superclasses=service_connector)
thrift = CStereotype("Thrift", superclasses=service_connector)

jms = CStereotype("JMS", superclasses=messaging)
stomp = CStereotype("STOMP", superclasses=messaging)

http = CStereotype("HTTP", superclasses=web_connector)
https = CStereotype("HTTPS", superclasses=web_connector)
http2 = CStereotype("HTTP/2", superclasses=web_connector)

linked_to_middleware_handler = CStereotype("Linked to Middleware Handler", superclasses=connector_type,
                                           attributes={"handler": str})

_all = CBundle("_all",
               elements=component.get_connected_elements(add_stereotypes=True) + connector_type.get_connected_elements(
                   add_stereotypes=True))

component_stereotypes = CBundle("Component Stereotypes",
                                elements=component_type.get_connected_elements(add_stereotypes=True))
connector_stereotypes = CBundle("Connector Stereotypes",
                                elements=[component] + connector_type.get_connected_elements(add_stereotypes=True))

microservice_metamodel_views = [
    _all, {},
    component_stereotypes, {"render_attributes": False},
    connector_stereotypes, {"render_attributes": False}]
