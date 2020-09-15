from dataclasses import dataclass
from typing import Union, Tuple, Dict, Optional, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError
from torch.utils.data import Dataset

try:
    from .dataset import Sample
except ImportError:
    from dataset import Sample

MLSet = Union[str, Tuple[str]]
MongoFilter = Union[Dict[str, str], Dict[str, int], Dict[str, Dict[str, Tuple[str]]]]


@dataclass
class MongoDatabaseInfo:
    host: str = MongoClient.HOST
    port: int = MongoClient.PORT
    db: str = "learning_machine"
    collection: str = "kaggle_faces"


class MongoProxy:
    """Class to Proxy Dataset interactions with MongoDB"""

    def __init__(self, mongodb_info: MongoDatabaseInfo, ml_set: MLSet):
        self._ml_set_filter = self._generate_mongo_filter(ml_set)
        self.db_info = mongodb_info
        self._mongo_client = self._init_mongo_connection()
        self._db = self._set_database()
        self._collection = self._set_collection()
        self._sample_oids = self._retrieve_all_oids()

    @staticmethod
    def _generate_mongo_filter(ml_set: MLSet) -> MongoFilter:
        if isinstance(ml_set, str):
            return {"set": ml_set}
        return {"set": {"$in": tuple(s for s in ml_set)}}

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
            print(
                "Connection to MongoDB[{}:{}] refused! Please check.".format(host, port)
            )
            return None
        else:
            return mongo_client

    def _set_database(self) -> Optional[Database]:
        """Initialise the Database as set in the
        provided `MongoDatabaseInfo`.
        If no matching database is found, None is returned."""
        if self._mongo_client is None:
            return None
        db_name = self.db_info.db
        if db_name not in self._mongo_client.list_database_names():
            return None
        return self._mongo_client[db_name]

    def _set_collection(self) -> Optional[Collection]:
        """Initialise the Mongo Collection as set in the
        provided `MongoDatabaseInfo`.
        If no matching collection is found, None is returned."""
        if self._mongo_client is None or self._db is None:
            return None
        collection = self.db_info.collection
        if collection not in self._db.list_collection_names():
            return None
        return self._db[collection]

    def _retrieve_all_oids(self) -> Optional[Tuple[Any, ...]]:
        """Retrieve all the ObjectIds of the sample in the Mongo Collection,
        provided the selection filter on the ml_set(s).
        If case of any error in connecting to the db or the collection, None
        is returned.
        """
        if all((self._mongo_client, self._db, self._collection)):
            # fetch all IDs of docs matching current filter
            ids_cursor = self._collection.find(self._ml_set_filter, {"_id": 1}).sort(
                "_id"
            )
            return tuple(obj_id["_id"] for obj_id in ids_cursor)
        return None

    def count(self, query_filter: MongoFilter = None):
        """Returns the total number of sample in the reference collection.
        An additional query filter can be provided to refine the selection,
        in addition to the default selection on the `ml_set`
        """
        if all((self._mongo_client, self._db, self._collection)):
            filter = self._ml_set_filter
            if query_filter:
                filter.update(query_filter)
            return self._collection.count_documents(filter)
        return 0

    def fetch(self, index):
        try:
            oid = self._sample_oids[index]
        except IndexError:
            pass
        else:
            query_filter = {"_id": oid}
            query_filter.update(self._ml_set_filter)
            return self._collection.find_one(query_filter)


class KaggleMongoDataset(Dataset):
    def __init__(
        self, ml_set: MLSet, transform=None, db_info: MongoDatabaseInfo = None
    ):
        self._transform = transform
        if db_info is None:
            db_info = MongoDatabaseInfo()  # default values
        self._mongo_proxy = MongoProxy(ml_set=ml_set, mongodb_info=db_info)

    def __len__(self):
        return self._mongo_proxy.count()

    def __getitem__(self, index):
        db_entry = self._mongo_proxy.fetch(index)
        sample = Sample.from_json(db_entry)
        if self._transform:
            sample.image = self._transform(sample.image)
        return sample

    def class_weights(self) -> Dict[int, float]:
        """"""
        num_samples = self._mongo_proxy.count()
        n_classes = len(Sample.EMOTION_MAP.keys())
        class_weights = {}
        for emotion in Sample.EMOTION_MAP:
            y_count = self._mongo_proxy.count(query_filter={"emotion": emotion})
            class_weights[emotion] = num_samples / (n_classes * y_count)
        return class_weights
