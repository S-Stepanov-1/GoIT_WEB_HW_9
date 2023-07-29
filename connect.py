from mongoengine import connect
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

mongo_user = config.get('DB', 'user')
mongodb_pass = config.get('DB', 'pass')
db_name = config.get('DB', 'db_name')


# connect to cluster on AtlasDB with connection string
def create_connect():
    connect(db=db_name, host=f"mongodb+srv://{mongo_user}:{mongodb_pass}@stepanovdb.codnmzv.mongodb.net/?retryWrites=true&w=majority", ssl=True)
