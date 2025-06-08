import os
from dotenv import load_dotenv
from pymongo import MongoClient
from src.services.logger import DrDLogger

load_dotenv()
MONGODB_CONNECTION = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("MONGO_DATABASE_NAME")
# if MONGODB_CONNECTION is None:
#     MONGODB_CONNECTION = "mongodb://localhost:27017/"

LOG_LEVEL = "info"
WRITE_LOG_TO_FILE = False
log = DrDLogger(
    file_name='log.txt',
    write_to_file=WRITE_LOG_TO_FILE,
    mode=LOG_LEVEL)

class MongoDBConnection():
    """
    Connect to the MongoDB, change the connection string per your MongoDB environment
    """
    url = MONGODB_CONNECTION
    col = DB_NAME
    
    def __init__(self):
        print("DEBUG DEBUG", DB_NAME, MONGODB_CONNECTION, "end")
        self.client = MongoClient(self.url)
        self.db = self.client[self.col]
        try:
            # check connection is available
            self.client.admin.command('ismaster')
            log.info("CONNECT TO DB {} SUCCESSFULLY".format(self.db))

        except Exception as e:
            log.error("CONNECT TO DB {} FAIL, ERROR: {}".format(self.db, e))
            
    def drop_collection(self, collection_name):
        """Drop collection

        Args:
            collection_name (str): collection name
        """
        self.col.drop()

        log.debug("collection {} is dropped successfully!".format(collection_name))
        
        
class CRUDDocuments():
    connection = MongoDBConnection()
    
    def __init__(self):
        self.collection = None
        
    def insert_one_doc(self, obj):
        """
        Insert a single document.
        Example:
            Input: x= {'x': 1}
                result = db.test.insert_one_doc(x)
            Output: result.inserted_id
                ObjectId('54f112defba522406c9cc208')
        Parameters:
            obj: The document to insert. Must be a mutable mapping type. 
                If the document does not have an _id field one will be added automatically.
            Returns:
                An instance of InsertOneResult.
        """
        return self.collection.insert_one(obj)
    
    def insert_many_doc(self, objs, ordered=True):
        """
        Insert an iterable of documents.
        Example:
            Input:  objs = []
            result = db.test.insert_many_doc([{'x': i} for i in range(2)])
            output:
            result.inserted_ids
            >>> [ObjectId('54f113fffba522406c9cc20e'), ObjectId('54f113fffba522406c9cc20f')]
        Parameters:
            - objs: A iterable of documents to insert.
            - ordered (optional): If True (the default) documents will be inserted on the server serially,
            in the order provided. If an error occurs all remaining inserts are aborted. 
            If False, documents will be inserted on the server in arbitrary order, 
            possibly in parallel, and all document inserts will be attempted.
            return: An instance of InsertManyResult.
        """
        return self.collection.insert_many(documents=objs, ordered=ordered)
    
    def replace_one_doc(self, filterObj, replaceObj, upsert=False):
        """
        Replace a single document matching the filter.
        Example:
            Input:
            {u'x': 1, u'_id': ObjectId('54f4c5befba5220aa4d6dee7')}
            result = db.test.replace_one_doc({'x': 1}, {'y': 1})
            Or
            result = db.test.replace_one_doc({'x': 1}, {'x': 1}, True)
            Output: 
            result.matched_count
            >>> result.matched_count
                1
            >>> result.modified_count
                1
        Parameters:
            - filterObj: A query that matches the document to replace.
            - replaceObj: The new document.
            - upsert (optional): If True, perform an insert if no documents match the filter.
        return:
            An instance of UpdateResult.
        """
        return self.collection.replace_one(filter=filterObj, replacement=replaceObj, upsert=upsert)
    
    def update_one_doc(self, filterObj, updateObj, upsert=False):
        """
        Update a single document matching the filter.
        Example:
            for doc in db.test.find_doc():
                print(doc)
                {u'x': 1, u'_id': 0}
                {u'x': 1, u'_id': 1}
                {u'x': 1, u'_id': 2}
        Input: filterObj, updateObj
            >>> result = db.test.update_one_doc({'x': 1}, {'$inc': {'x': 3}})
        Output:   
            >>> result.matched_count
                1
            >>> result.modified_count
                1
            >>> for doc in db.test.find_doc():
                print(doc)
                {u'x': 4, u'_id': 0}
                {u'x': 1, u'_id': 1}
                {u'x': 1, u'_id': 2}
        Parameters:
            - filterObj: A query that matches the document to update.
            - updateObj:The modifications to apply.
            - upsert (optional): If True, perform an insert if no documents match the filter.
        """
        result = self.collection.update_one(filter=filterObj, update=updateObj, upsert=upsert)
        return result
    
    def update_many_doc(self, filterObj, updateObj, upsert=False):
        """
        Update one or more documents that match the filter.
        Example:
                >>> for doc in db.test.find_doc():
                            print(doc)
                {u'x': 1, u'_id': 0}
                {u'x': 1, u'_id': 1}
                {u'x': 1, u'_id': 2}
            Input: filterObj, updateObj, upsert
                    result = db.test.update_many_doc({'x': 1}, {'$inc': {'x': 3}})
            Output:    
                    result.matched_count
                    >>> 3
                    result.modified_count
                    >>> 3
                    for doc in db.test.find_doc():
                    print(doc)
                    {u'x': 4, u'_id': 0}
                    {u'x': 4, u'_id': 1}
                    {u'x': 4, u'_id': 2}
        Parameters:
            - filterObj: A query that matches the documents to update.
            - updateObj: The modifications to apply.
            - upsert (optional): If True, perform an insert if no documents match the filter.
                Requires MongoDB 3.6+
        Return:
            An instance of UpdateResult.
        """
        result = self.collection.update_many(filter=filterObj, update=updateObj, upsert=upsert)
        return result
    
    def delete_one_doc(self, filterObj):
        """
        Delete a single document matching the filter.
        Example:
            Input:
                db.test.count_documents({'x': 1})
                    >>> 3
                result = db.test.delete_one({'x': 1})
            Output:   
                result.deleted_count
                    >>> 1
                db.test.count_documents({'x': 1})
                    >>>2
        Parameters:
            - filterObj: A query that matches the document to delete.
        Return:
            An instance of DeleteResult.
        """
        return self.collection.delete_one(filterObj)
    
    def delete_many_doc(self, filterObj):
        """
        Delete one or more documents matching the filter.
        Example:
            db.test.count_documents({'x': 1})
                >>> 3
            Input:
                result = db.test.delete_many_doc({'x': 1})
            Output:
                result.deleted_count
                >>> 3
                db.test.count_documents({'x': 1})
                >>>   0
        Parameters:
            - filterObj: A query that matches the documents to delete.
        Return:
            An instance of DeleteResult.
        """
        return self.collection.delete_many(filterObj)
    
    def find_one_doc(self, filterObj=None):
        """
        Get a single document from the database.
        All arguments to find_doc() are also valid arguments for find_one_doc(), although any limit argument will be ignored. 
        Returns a single document, or None if no matching document is found.
        The find_one_doc() method obeys the read_preference of this Collection.
        Parameters:
            - filterObj (optional): a dictionary specifying the query to be performed OR any other type to be used as the 
            value for a query for "_id".
        Return:
            Returns a single document 
        """
        return self.collection.find_one(filter=filterObj)
    
    def find_all_doc(self):
        return self.collection.find({})
    
    def count_documents(self, filterObj):
        """
        Count the number of documents in this collection.
        The count_documents() method is supported in a transaction.
        Parameters:
            - filterObj (required): A query document that selects which documents to count in the collection. 
            Can be an empty document to count all documents.
        """
        return self.collection.count_documents(filter=filterObj)
    
    def read_documents(self, query: dict):
        documents = self.collection.find(query)
        return list(documents)