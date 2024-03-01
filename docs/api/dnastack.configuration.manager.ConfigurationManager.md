#### Class `dnastack.configuration.manager.ConfigurationManager(file_path: str)`
##### Methods
###### `def load() -> dnastack.configuration.models.Configuration`
Load the configuration object
###### `def load_raw() -> str`
Load the raw configuration content
###### `@staticmethod def migrate(configuration: dnastack.configuration.models.Configuration) -> dnastack.configuration.models.Configuration`
Perform on-line migration on the Configuration object.
###### `@staticmethod def migrate_endpoint(endpoint: dnastack.client.models.ServiceEndpoint) -> dnastack.client.models.ServiceEndpoint`
Perform on-line migration on the ServiceEndpoint object.
###### `def save(configuration: dnastack.configuration.models.Configuration)`
Save the configuration object