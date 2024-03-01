#### Class `dnastack.client.service_registry.factory.ClientFactory(registries: List[dnastack.client.service_registry.client.ServiceRegistry])`
Service Client Factory using Service Registries 
##### Methods
###### `def find_services(url: Optional[str], types: Optional[List[dnastack.client.service_registry.models.ServiceType]], exact_match: bool= True) -> Iterable[dnastack.client.service_registry.models.Service]`
Find GA4GH services
###### `@staticmethod def use(*service_registry_endpoints)`
.. note:: This only works with public registries.