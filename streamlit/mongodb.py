
from pymongo.mongo_client import MongoClient

class MongoDBHandler:
    def __init__(self, connection_uri):
        """
        Initialize the MongoDBHandler class and test the connection to the database and collection.

        Args:
            connection_uri (str): MongoDB connection URI.
        """
        self.connection_uri = connection_uri
        self.client = None
        self.db = None
        self.collection = None

    def connect_and_test(self):
        """
        Connect to the MongoDB Atlas database and check for the existence of the 'current_domains' collection.

        Raises:
            Exception: If the database or collection does not exist or connection fails.
        """
        try:
            # Connect to MongoDB Atlas
            self.client = MongoClient(self.connection_uri)

            # Access the 'streamlit' database
            db_name = "streamlit"
            if db_name in self.client.list_database_names():
                self.db = self.client[db_name]

                # Check for 'current_domains' collection
                collection_name = "current_domains"
                if collection_name in self.db.list_collection_names():
                    self.collection = self.db[collection_name]
                    print(f"Connected to database '{db_name}' and collection '{collection_name}' successfully.")
                else:
                    raise Exception(f"Collection '{collection_name}' not found in database '{db_name}'.")
            else:
                raise Exception(f"Database '{db_name}' not found.")
        except Exception as e:
            raise Exception(f"An error occurred during connection: {e}")

    def update_url_if_needed(self, document_id, new_url):
        """
        Update the URL in the document if it differs from the existing URL.

        Args:
            document_id (str): The ID of the document to check and update.
            new_url (str): The new URL to compare and update if necessary.

        Returns:
            str: A message indicating whether the URL was updated or unchanged.
        """
        try:
            # Find the document by ID
            document = self.collection.find_one({"_id": document_id})
            if not document:
                return f"Document with ID '{document_id}' not found."

            old_url = document.get("name")
            if old_url == new_url:
                print("No changes needed. The new URL matches the existing URL.")
                return new_url
            else:
                # Update the URL in the document
                self.collection.update_one({"_id": document_id}, {"$set": {"name": new_url}})
                print(f"URL updated from '{old_url}' to '{new_url}'.")
                return new_url
        except Exception as e:
            raise Exception(f"An error occurred while updating the URL: {e}")
    
    def get_current_url(self,document_id):
        """
        Connect to the MongoDB Atlas database and get the current url for a given id.

        Raises:
            Exception: If the database or collection does not exist or connection fails.
        """
        try:
            # Find the document by ID
            document = self.collection.find_one({"_id": document_id})
            if not document:
                return f"Document with ID '{document_id}' not found."

            return document.get("name")
        except Exception as e:
            raise Exception(f"An error occurred while getting the URL: {e}")
        

