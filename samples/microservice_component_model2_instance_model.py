"""
*File Name:* samples/microservice_component_model2.py

This is a Codeable Models example realizing a sample component model.
It is used to explain meta-modelling with stereotypes. It uses meta-classes from the :ref:`component_metamodel`.

The example is explained in :ref:`meta_model_stereotypes`.

"""

from codeable_models import CClass, CBundle, add_links, CStereotype
from metamodels.component_metamodel import component, connectors_relation
from plant_uml_renderer import PlantUMLGenerator

# meta-model extensions
service = CStereotype("Service", extended=component)
database = CStereotype("Database", extended=component)

facade = CStereotype("Facade", extended=component)
web_ui = CStereotype("Web UI", superclasses=facade)
gateway = CStereotype("Gateway", extended=component)

jdbc = CStereotype("JDBC", extended=connectors_relation)
restful_http = CStereotype("RESTful HTTP", extended=connectors_relation)

# class model
api_gateway = CClass(component, "API Gateway", stereotype_instances=[gateway, facade])
inventory_service = CClass(component, "Inventory Service", stereotype_instances=service)
shipping_service = CClass(component, "Shipping Service", stereotype_instances=service)
web_frontend = CClass(component, "Web Frontend", stereotype_instances=web_ui)
inventory_db = CClass(component, "Inventory DB", stereotype_instances=database)
shipping_db = CClass(component, "Shipping DB", stereotype_instances=database)

add_links({api_gateway: [inventory_service, shipping_service],
           web_frontend: [inventory_service, shipping_service]},
          role_name="target", stereotype_instances=restful_http)

add_links({inventory_service: inventory_db, shipping_service: shipping_db},
          role_name="target", stereotype_instances=jdbc)

microservice_component_model2 = CBundle("microservice_component_model2",
                                        elements=api_gateway.class_object.get_connected_elements())

component_meta_model = CBundle("component_meta_model",
                               elements=(component.get_connected_elements(add_stereotypes=True) +
                                         [jdbc, restful_http]))


def run():
    print("***************** Microservice Component Model 2: Meta-modelling example *****************")
    print('*** Plant UML Generation')
    generator = PlantUMLGenerator()
    generator.object_model_renderer.left_to_right = True
    generator.generate_object_models("microservice_component_model2", [microservice_component_model2, {}])
    generator.generate_class_models("microservice_component_model2", [component_meta_model, {}])
    print(f"... Generated models in {generator.directory!s}/microservice_component_model2")


if __name__ == "__main__":
    run()
