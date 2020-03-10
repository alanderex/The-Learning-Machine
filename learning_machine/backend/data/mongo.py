from dataclasses import dataclass
from typing import Union, Tuple, Dict, Optional, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError
from torch.utils.data import Dataset

MLSet = Union[str, Tuple[str]]
MongoFilter = Union[Dict[str, str],
                    Dict[str, Dict[str, Tuple[str]]]]


@dataclass
class MongoDatabaseInfo:
    host: str = MongoClient.HOST
    port: int = MongoClient.PORT
    db: str = 'learning_machine'
    collection: str = 'kaggle_faces'


class MongoProxy:
    """Class to Proxy Dataset interactions with MongoDB"""

    def __init__(self, mongodb_info: MongoDatabaseInfo, ml_set: MLSet):
        self._ml_set_filter = self._generate_mongo_filter(ml_set)
        self.db_info = mongodb_info
        self._mongo_client = self._init_mongo_connection()
        self._db = self._set_database()
        self._collection = self._set_collection()
        self._sample_oids = self._fetch_sample_ids()

    @staticmethod
    def _generate_mongo_filter(ml_set: MLSet) -> MongoFilter:
        if isinstance(ml_set, str):
            return {'set': ml_set}
        return {'set': {'$in': tuple(s for s in ml_set)}}

    def _init_mongo_connection(self) -> Optional[MongoClient]:
        """
        Initialise Client to connect to MongoDB. `None` will be returned
        if the connection cannot be established.
        """
        host, port = self.db_info.host, self.db_info.port
        mongo_client = MongoClient(host=host, port=port, serverSelectionTimeoutMS=3000)
        try:
            _ = mongo_client.server_info()
        except ServerSelectionTimeoutError:
            print('Connection to MongoDB[{}:{}] refused! Please check.'.format(host, port))
            return None
        else:
            return mongo_client

    def _set_database(self) -> Optional[Database]:
        """"""
        if self._mongo_client is None:
            return None
        db_name = self.db_info.db
        if db_name not in self._mongo_client.list_database_names():
            return None
        return self._mongo_client[db_name]

    def _set_collection(self) -> Optional[Collection]:
        """"""
        if self._mongo_client is None or self._db is None:
            return None
        collection = self.db_info.collection
        if collection not in self._db.list_collection_names():
            return None
        return self._db[collection]

    def _fetch_sample_ids(self) -> Optional[Tuple[Any, ...]]:
        """"""
        if all((self._mongo_client, self._db, self._collection)):
            # fetch all IDs of docs matching current filter
            ids_cursor = self._collection.find(self._ml_set_filter, {'_id': 1}).sort('_id')
            return tuple(obj_id['_id'] for obj_id in ids_cursor)
        return None

    def count(self):
        if all((self._mongo_client, self._db, self._collection)):
            return self._collection.count_documents(self._ml_set_filter)
        return 0

    def fetch(self, index):
        try:
            oid = self._sample_oids[index]
        except IndexError:
            pass
        else:
            query_filter = {'_id': oid}
            query_filter.update(self._ml_set_filter)
            return self._collection.find_one(query_filter)


class KaggleMongoDataset(Dataset):

    def __init__(self, ml_set: MLSet, transform=None, db_info: MongoDatabaseInfo = None):
        self._transform = transform
        if db_info is None:
            db_info = MongoDatabaseInfo()  # default values
        self._mongo_proxy = MongoProxy(ml_set=ml_set, mongodb_info=db_info)

    def __len__(self):
        return self._mongo_proxy.count()

    def __getitem__(self, index):
        sample = self._mongo_proxy.fetch(index)
        # PUT TRANSFORMERS HERE
        return sample
