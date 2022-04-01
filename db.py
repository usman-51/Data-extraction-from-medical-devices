from time import sleep
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["qure"]
mycol = mydb["medical_devices"]

def insert_values(mycol,document):
    x = mycol.insert_many(document)
    return x.inserted_ids


def return_all_docs_url(collection):
    all_urls = []
    for documents in collection.find():
        all_urls.append(documents)
    return all_urls

def find_document_on_url(mycol,email):
    myquery = { "email": email }
    mydoc = mycol.find(myquery)
    for x in mydoc:
        return x
    return {}

# def update_document(url,newvalues):
#     myquery = { 'url': url }
#     mycol.update_one(myquery, newvalues)
#     return mycol


def update_document(url,newvalues):
    myquery = { 'url': url }
    x=find_document_on_url(mycol,url)
    newvalues['$set']['scores'].update(x['scores'])
        
    mycol.update_one(myquery, newvalues)
    return mycol




    
