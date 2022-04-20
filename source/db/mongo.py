import pymongo

mongoURL= "mongodb+srv://username:passwd@cluster0.x5fk3.mongodb.net/myFirstDatabase?retryWrites=true&w=majority";
myclient = pymongo.MongoClient(mongoURL)

mongo = myclient["adaAssistant"]

print('mydb')
print(mongo)


