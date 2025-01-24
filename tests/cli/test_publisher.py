import click

from dnastack.client.collections.model import Collection
from tests.cli.base import PublisherCliTestCase


class TestPublisherCommand(PublisherCliTestCase):
    @staticmethod
    def reuse_session() -> bool:
        return True

    def setUp(self) -> None:
        super().setUp()
        self.invoke('use', self.service_registry_base_url)
        collection_service_registry_id = 'collection-service-registry'
        existing_registries = self.simple_invoke('config', 'registries', 'list')
        if not any(registry['id'] == collection_service_registry_id for registry in existing_registries):
            self.invoke(
                'config', 'registries', 'add',
                f'{collection_service_registry_id}', f'{self.collection_service_base_url}/service-registry'
            )
        else:
            click.echo(f'Registry {collection_service_registry_id} already exists. Skipping adding it.')

    def _get_first_collection(self):
        collections_result = self.simple_invoke(
            'publisher', 'collections', 'list'
        )
        return Collection(**collections_result[0])

    def test_collections_list(self):
        collections_result = [Collection(**collection) for collection in self.simple_invoke(
            'publisher', 'collections', 'list'
        )]

        self.assert_not_empty(collections_result, f'Expected at least one collection. Found: {collections_result}')
        for collection in collections_result:
            self.assert_not_empty(collection.id, 'Collection ID should not be empty')

    def test_collections_items_list(self):
        first_collection = self._get_first_collection()
        items_result = self.simple_invoke(
            'publisher', 'collections', 'items', 'list',
            '--collection', first_collection.slugName,
            '--limit', 1
        )

        self.assertEqual(len(items_result), 1, f'Expected exactly one item. Found {items_result}')
        for item in items_result:
            self.assert_not_empty(item['id'], 'Item ID should not be empty')

    def test_collections_tables_list(self):
        first_collection = self._get_first_collection()
        tables_result = self.simple_invoke(
            'publisher', 'collections', 'tables', 'list',
            '--collection', first_collection.slugName
        )

        self.assert_not_empty(tables_result, f'Expected at least one table. Found: {tables_result}')
        for table in tables_result:
            self.assert_not_empty(table['name'], 'Table name should not be empty')

    def test_collections_query(self):
        first_collection = self._get_first_collection()
        tables_result = self.simple_invoke(
            'publisher', 'collections', 'tables', 'list',
            '--collection', first_collection.slugName
        )
        first_table = tables_result[0]
        query_result = self.simple_invoke(
            'publisher', 'collections', 'query',
            '--collection', first_collection.slugName,
            f'SELECT * FROM {first_table["name"]} LIMIT 1'
        )

        self.assertIsNotNone(query_result, 'Query result should not be None (can be empty though)')
