from copy import deepcopy
from typing import List, Optional, Any, Dict, Iterable, Callable

from dnastack.alpha.app.publisher_helper.collection_wrapper import BlobApiMixin, CollectionApiMixin
from dnastack.alpha.app.publisher_helper.exceptions import NoCollectionError, TooManyCollectionsError
from dnastack.alpha.app.publisher_helper.data_connect import SearchOperation
from dnastack.alpha.app.publisher_helper.models import BaseItemInfo, ItemType, TableInfo, \
    BlobInfo
from dnastack.client.collections.client import CollectionServiceClient, UnknownCollectionError
from dnastack.client.collections.model import Collection as CollectionModel
from dnastack.client.data_connect import DataConnectClient
from dnastack.client.drs import DrsClient, Blob
from dnastack.client.factory import EndpointRepository
from dnastack.client.models import ServiceEndpoint
from dnastack.common.logger import get_logger_for
from dnastack.common.simple_stream import SimpleStream
from dnastack.context.helper import use


class Collection(BlobApiMixin):
    """ High-level Collection API Client """

    def __init__(self,
                 factory: EndpointRepository,
                 cs: CollectionServiceClient,
                 collection: CollectionModel,
                 no_auth: bool):
        self._logger = get_logger_for(self)
        self._factory = factory
        self._cs = cs
        self._collection = collection
        self._no_auth = no_auth
        self._dc: DataConnectClient = self.data_connect()
        self._drs: DrsClient = self._factory.get_one_of(client_class=DrsClient)

    def get_record(self) -> CollectionModel:
        return self._collection

    def query(self, query: str):
        return SearchOperation(self._dc, self._no_auth, query)

    def list_items(self,
                   *,
                   limit: Optional[int],
                   kind: Optional[ItemType] = None,
                   kinds: Optional[Iterable[ItemType]] = None,
                   on_has_more_result: Optional[Callable[[int], None]] = None) -> List[BaseItemInfo]:
        # We opt for an enum on item types (kind/kinds) in this case to avoid SQL-injection attempts.
        assert limit >= 0, 'The limit has to be ZERO (no limit) or at least 1 (to impose the limit).'

        items: List[BaseItemInfo] = []

        items_query = self._collection.itemsQuery.strip()

        # We use +1 as an indicator whether there are more results.
        actual_items_query = f'SELECT * FROM ({items_query})'

        if kind:
            actual_items_query = f"{actual_items_query} WHERE type = '{kind.value}'"

        if kinds:
            types = ', '.join([f"'{kind}'" for kind in kinds])
            actual_items_query = f"{actual_items_query} WHERE type IN {types}"

        if limit is not None and limit > 1:
            actual_items_query = f"{actual_items_query} LIMIT {limit + 1}"

        items.extend([
            self.__simplify_item(i)
            for i in self._dc.query(actual_items_query, no_auth=self._no_auth)
        ])

        row_count = len(items)

        if 0 < limit < row_count and on_has_more_result and callable(on_has_more_result):
            on_has_more_result(row_count)

        return items

    def data_connect(self):
        default_no_auth_properties = {'authentication': None, 'fallback_authentications': None}

        proposed_data_connect_endpoint = self._cs.data_connect_endpoint(self._collection.slugName,
                                                                        no_auth=self._no_auth)

        target_endpoint: Optional[ServiceEndpoint] = None

        # Look up for any similar registered service endpoint.
        for endpoint in self._factory.all(client_class=DataConnectClient):
            proposed_data_connect_endpoint_url = proposed_data_connect_endpoint.url
            if not proposed_data_connect_endpoint_url.endswith('/'):
                proposed_data_connect_endpoint_url += '/'

            reference_data_connect_endpoint_url = endpoint.url
            if not reference_data_connect_endpoint_url.endswith('/'):
                reference_data_connect_endpoint_url += '/'

            if proposed_data_connect_endpoint_url == reference_data_connect_endpoint_url:
                target_endpoint = endpoint
                break

        if not target_endpoint:
            target_endpoint = proposed_data_connect_endpoint

            self._logger.debug(
                f'Unable to find a registered {proposed_data_connect_endpoint.type} endpoint '
                f'at {proposed_data_connect_endpoint.url}.'
            )

        return DataConnectClient.make(
            target_endpoint.copy(update=default_no_auth_properties)
            if self._no_auth
            else target_endpoint
        )

    def find_blob_by_name(self, objectname: str) -> Blob:
        return self._find_blob_by_name(objectname=objectname, column_name='drs_url')

    @staticmethod
    def __simplify_item(row: Dict[str, Any]) -> BaseItemInfo:
        if row['type'] == ItemType.BLOB.value:
            return BlobInfo(**row)
        elif row['type'] == ItemType.TABLE.value:
            row_copy = deepcopy(row)
            row_copy['name'] = (
                    row.get('qualified_table_name')
                    or row.get('preferred_name')
                    or row.get('display_name')
                    or row['name']
            )
            return TableInfo(**row_copy)
        else:
            return BaseItemInfo(**row)


class Explorer(CollectionApiMixin):
    """ High-level Explorer API Client

        .. code-block:: python

            from dnastack.alpha.app.explorer import Explorer

            # Data Connect
            query = collection.query('SELECT * FROM collections.public_datasets.metadata LIMIT 5')
            df = query.to_data_frame()
            rows = query.to_list()

            # DRS (not yet manually tested with collections with blobs)
            blob: Optional[Blob] = collection.blob(id='123-456') or collection.blob(name='foo-bar')
            blobs: Dict[str, Optional[Blob]] = collection.blobs(ids=['123-456']) or collection.blobs(names=['foo-bar'])

    """

    def __init__(self, context_name_or_url: str, *, no_auth: bool = False):
        self._logger = get_logger_for(self)
        self._context_name_or_url = context_name_or_url
        self._factory = use(self._context_name_or_url, no_auth=no_auth)
        self._cs: CollectionServiceClient = self._factory.get_one_of(client_class=CollectionServiceClient)
        self._no_auth = no_auth

    def collection(self, id_or_slug_name: Optional[str] = None, *, name: Optional[str] = None) -> Collection:
        # NOTE: "ID" and "slug name" are unique identifier whereas "name" is not.
        return Collection(self._factory,
                          self._cs,
                          self.get_collection_info(id_or_slug_name=id_or_slug_name, name=name),
                          no_auth=self._no_auth)
