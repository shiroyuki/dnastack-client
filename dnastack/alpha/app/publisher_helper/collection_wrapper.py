from typing import Optional, Dict, List

from dnastack.alpha.app.publisher_helper.exceptions import NoCollectionError, TooManyCollectionsError
from dnastack.client.collections.client import UnknownCollectionError
from dnastack.client.collections.model import Collection as CollectionModel
from dnastack.client.drs import Blob
from dnastack.common.simple_stream import SimpleStream


class CollectionApiMixin:
    def list_collections(self) -> List[CollectionModel]:
        return self._cs.list_collections(no_auth=self._no_auth)

    def get_collection_info(self, id_or_slug_name: Optional[str] = None, *, name: Optional[str] = None) -> CollectionModel:
        # NOTE: "ID" and "slug name" are unique identifier whereas "name" is not.
        assert id_or_slug_name or name, 'One of the arguments MUST be defined.'

        if id_or_slug_name is not None:
            try:
                collection = self._cs.get(id_or_slug_name, no_auth=self._no_auth)
            except UnknownCollectionError as e:
                raise NoCollectionError(id_or_slug_name) from e
            return collection
        elif name is not None:
            assert name.strip(), 'The name cannot be empty.'
            target_collections = SimpleStream(self._cs.list_collections(no_auth=self._no_auth)) \
                .filter(lambda endpoint: name == endpoint.name) \
                .to_list()
            if len(target_collections) == 1:
                return target_collections[0]
            elif len(target_collections) == 0:
                raise NoCollectionError(name)
            else:
                raise TooManyCollectionsError(target_collections)
        else:
            raise NotImplementedError()


class BlobApiMixin:
    def blob(self, *, id: Optional[str] = None, name: Optional[str] = None) -> Optional[Blob]:
        blobs = self.blobs(ids=[id] if id else [], names=[name] if name else [])
        if blobs:
            return blobs.get(id if id is not None else name)
        else:
            return None

    def blobs(self, *, ids: Optional[List[str]] = None, names: Optional[List[str]] = None) -> Dict[str, Optional[Blob]]:
        assert ids or names, 'One of the arguments MUST be defined.'

        if ids:
            conditions: str = ' OR '.join([
                f"(id = '{id}')"
                for id in ids
            ])
        elif names:
            conditions: str = ' OR '.join([
                f"(name = '{name}')"
                for name in names
            ])
        else:
            raise NotImplementedError()

        collection: CollectionModel = self._collection

        id_to_name_map: Dict[str, str] = SimpleStream(
            self.query(f"SELECT id, name FROM ({collection.itemsQuery}) WHERE {conditions}").load_data()
        ).to_map(lambda row: row['id'], lambda row: row['name'])

        return {
            id if ids is not None else id_to_name_map[id]: self._drs.get_blob(id)
            for id in id_to_name_map.keys()
        }

    def _find_blob_by_name(self,
                           objectname: str,
                           column_name: str) -> Blob:
        collection: CollectionModel = self._collection

        db_slug = collection.slugName.replace("-", "_")

        # language=sql
        q = f"SELECT {column_name} FROM collections.{db_slug}._files WHERE name='{objectname}' LIMIT 1"

        results = self.query(q)
        return self._drs.get_blob(next(results.load_data())[column_name], no_auth=self._no_auth)