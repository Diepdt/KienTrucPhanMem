from datetime import datetime, timezone
import logging

from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import PyMongoError


logger = logging.getLogger(__name__)


class MongoProductAttributesStore:
    def __init__(self):
        self._uri = getattr(settings, 'MONGO_URI', 'mongodb://localhost:27017')
        self._db_name = getattr(settings, 'MONGO_DB_NAME', 'tieuluan_product')
        self._collection_name = getattr(settings, 'MONGO_ATTRIBUTES_COLLECTION', 'product_attributes')
        self._client = None
        self._collection = None

    def _get_collection(self):
        if self._collection is not None:
            return self._collection

        self._client = MongoClient(self._uri, serverSelectionTimeoutMS=1200)
        database = self._client[self._db_name]
        self._collection = database[self._collection_name]
        return self._collection

    def get(self, product_id: int, fallback=None):
        try:
            document = self._get_collection().find_one({'product_id': int(product_id)})
            if not document:
                return fallback if isinstance(fallback, dict) else {}

            attrs = document.get('attributes', {})
            return attrs if isinstance(attrs, dict) else {}
        except (TypeError, ValueError):
            return fallback if isinstance(fallback, dict) else {}
        except PyMongoError as exc:
            logger.warning('Mongo get attributes failed for product_id=%s: %s', product_id, exc)
            return fallback if isinstance(fallback, dict) else {}

    def get_many(self, product_ids):
        normalized_ids = []
        for raw_id in product_ids:
            try:
                normalized_ids.append(int(raw_id))
            except (TypeError, ValueError):
                continue

        if not normalized_ids:
            return {}

        try:
            cursor = self._get_collection().find({'product_id': {'$in': normalized_ids}})
            result = {}
            for item in cursor:
                attrs = item.get('attributes', {})
                if isinstance(attrs, dict):
                    result[item.get('product_id')] = attrs
            return result
        except PyMongoError as exc:
            logger.warning('Mongo get_many attributes failed: %s', exc)
            return {}

    def upsert(self, product_id: int, attributes):
        payload = attributes if isinstance(attributes, dict) else {}
        try:
            self._get_collection().update_one(
                {'product_id': int(product_id)},
                {
                    '$set': {
                        'attributes': payload,
                        'updated_at': datetime.now(timezone.utc),
                    },
                    '$setOnInsert': {
                        'product_id': int(product_id),
                        'created_at': datetime.now(timezone.utc),
                    },
                },
                upsert=True,
            )
        except (TypeError, ValueError):
            return
        except PyMongoError as exc:
            logger.warning('Mongo upsert attributes failed for product_id=%s: %s', product_id, exc)

    def delete(self, product_id: int):
        try:
            self._get_collection().delete_one({'product_id': int(product_id)})
        except (TypeError, ValueError):
            return
        except PyMongoError as exc:
            logger.warning('Mongo delete attributes failed for product_id=%s: %s', product_id, exc)

    def delete_many(self, product_ids):
        normalized_ids = []
        for raw_id in product_ids:
            try:
                normalized_ids.append(int(raw_id))
            except (TypeError, ValueError):
                continue

        if not normalized_ids:
            return

        try:
            self._get_collection().delete_many({'product_id': {'$in': normalized_ids}})
        except PyMongoError as exc:
            logger.warning('Mongo delete_many attributes failed: %s', exc)
