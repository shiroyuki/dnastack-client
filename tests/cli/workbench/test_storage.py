from build.lib.dnastack.client.workbench.storage.models import StorageAccount, Platform, Provider
from tests.cli.base import WorkbenchCliTestCase


class TestWorkbenchStorageCommand(WorkbenchCliTestCase):
    @staticmethod
    def reuse_session() -> bool:
        return True

    def setUp(self) -> None:
        super().setUp()
        self.invoke('use', f'{self.workbench_base_url}/api/service-registry')
        self.submit_hello_world_workflow_batch()
        self.storage_account = None
        self.platform = None


    def test_storage_create(self):
        created_storage_account = self._create_storage_account()
        self.assertIsNotNone(created_storage_account.id)
        self.assertIsNotNone(created_storage_account.name)
        self.assertEqual(created_storage_account.provider, Provider.aws)


    def test_storage_list(self):
        created_storage_account = self._get_or_create_storage_account()
        storage_accounts = [StorageAccount(**storage_account) for storage_account in self.simple_invoke(
             'workbench', 'storage', 'list'
        )]
        self.assert_not_empty(storage_accounts, f'Expected at least one storage account. Found {storage_accounts}')
        self.assertTrue(created_storage_account.id in [storage_account.id for storage_account in storage_accounts])


    def test_storage_describe(self):
        created_storage_account = self._get_or_create_storage_account()
        storage_accounts = [StorageAccount(**storage_account) for storage_account in self.simple_invoke(
             'workbench', 'storage', 'describe', created_storage_account.id
        )]
        self.assertEqual(len(storage_accounts), 1,
                         f'Expected exactly one storage account. Found {storage_accounts}')
        self.assertEqual(storage_accounts[0].id, created_storage_account.id)
        self.assertEqual(storage_accounts[0].name, created_storage_account.name)
        self.assertEqual(storage_accounts[0].provider, Provider.aws)


    def test_platform_create(self):
        created_storage_account = self._create_storage_account()
        created_platform = self._create_platform(created_storage_account=created_storage_account, id='test-platform')
        self.assertIsNotNone(created_platform.id)
        self.assertEqual(created_platform.name, 'Test Platform')
        self.assertEqual(created_platform.type, 'pacbio')
        self.assertEqual(created_platform.storage_account_id, created_storage_account.id)


    def test_platforms_list(self):
        created_storage_account = self._get_or_create_storage_account()
        created_platform = self._get_or_create_platform()
        platforms = [Platform(**platform) for platform in self.simple_invoke(
             'workbench', 'storage', 'platforms', 'list'
        )]
        self.assert_not_empty(platforms, f'Expected at least one platform. Found {platforms}')
        self.assertTrue(created_platform.id in [platform.id for platform in platforms])


    def test_platform_describe(self):
        created_storage_account = self._get_or_create_storage_account()
        created_platform = self._get_or_create_platform()
        platforms = [Platform(**platform) for platform in self.simple_invoke(
             'workbench', 'storage', 'platforms', 'describe', created_platform.id,
            '--storage-id', created_storage_account.id
        )]
        self.assertEqual(len(platforms), 1, f'Expected exactly one platform. Found {platforms}')
        self.assertEqual(platforms[0].id, created_platform.id)
        self.assertEqual(platforms[0].name, created_platform.name)
        self.assertEqual(platforms[0].type, created_platform.type)
        self.assertEqual(platforms[0].storage_account_id, created_storage_account.id)
    def test_platform_delete(self):
        created_storage_account = self._get_or_create_storage_account()
        created_platform = self._get_or_create_platform()
        output = self.simple_invoke(
             'workbench', 'storage', 'platforms', 'delete', created_platform.id,
            '--storage-id', created_storage_account.id,
            '--force',
            parse_output=False
        )
        self.assertTrue("deleted successfully" in output)

        platforms = [Platform(**platform) for platform in self.simple_invoke(
             'workbench', 'storage', 'platforms', 'list'
        )]
        self.assertTrue(created_platform.id not in [platform.id for platform in platforms])

        result = self.invoke(
             'workbench', 'storage', 'platforms', 'describe', created_platform.id,
            '--storage-id', created_storage_account.id,
            bypass_error=True
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertTrue('"error_code":404' in result.stderr)

    def test_storage_delete(self):
        created_storage_account = self._create_storage_account()
        output = self.simple_invoke(
             'workbench', 'storage', 'delete', created_storage_account.id,
            '--force',
            parse_output=False
        )
        self.assertTrue("deleted successfully" in output)

        storage_accounts = [StorageAccount(**storage_account) for storage_account in self.simple_invoke(
             'workbench', 'storage', 'list'
        )]
        self.assertTrue(
            created_storage_account.id not in [storage_account.id for storage_account in storage_accounts])

        result = self.invoke(
             'workbench', 'storage', 'describe', created_storage_account.id,
            bypass_error=True
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertTrue('"error_code":404' in result.stderr)