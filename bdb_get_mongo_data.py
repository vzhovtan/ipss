import json
from pymongo import MongoClient

data_for_calculation = []
client = MongoClient()
mydb = client["task_ipss_pilot"]
mycol = mydb["ipss_stats"]

doc_list = []
host_list = []
final_data = []

#grab all data from mongodb and save in doc_list
for doc in mycol.find():
    del doc['_id']
    doc_list.append(doc)
    
#create list of hostname for non-empty items and remove duplicates     
for item in doc_list:
    if list(item.keys())[0]:
        host_list.append(list(item.keys())[0])
    host_set = set(host_list)
      

# create final_data for entries which contain hostname, interfaces info and line card info
host_done = []
for host in host_set:
    for item in doc_list:
        final_entry = {}
        if list(item.keys())[0] == host and host not in host_done:
            host_done.append(host)
            final_entry[host] = {}
            if list(item.values())[0]['interfaces']:
                final_entry[host]['line_cards'] = list(item.values())[0]['line_cards']
                final_entry[host]['interfaces'] = list(item.values())[0]['interfaces']

        if final_entry and bool(list(final_entry.values())[0]):
            final_data.append(final_entry)

for item in final_data:
    print(item)
    print("\n")
print(len(final_data))

with open("outcome.json", "w") as file:
        file.write(json.dumps(final_data))
