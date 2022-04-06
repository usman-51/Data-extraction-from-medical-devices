from time import sleep
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["qure"]
mycol = mydb["medical_devices"]

def insert_values(mycol,document):
    x = mycol.insert_many(document)
    return x.inserted_ids


def return_all_data(collection):
    all_data = []
    for documents in collection.find():
        all_data.append(documents)
    return all_data

def return_all_users_email(collection):
    all_emails = []
    for documents in collection.find():
        all_emails.append(documents['email'])
    return all_emails

def find_documents_on_email(mycol,email):
    myquery = { "email": email }
    mydocs = mycol.find(myquery,{'_id':0})
    # return mydocs
    records = []
    for x in mydocs:
        records.append(x)
    if records:
        return records
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




    
