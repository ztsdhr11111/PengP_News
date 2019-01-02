# Author : ZhangTong
import pymongo

HOST = 'localhost'
PORT = 27017


client = pymongo.MongoClient(host=HOST, port=PORT)
db = client.Spider
collection = db.PengP_News