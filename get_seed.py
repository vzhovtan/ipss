import yaml

lc_list = []
pattern = ""

with open("demo_seed_9k.yml", 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)

print(data)
for key in data:
    if "pattern" not in key:
        print(key)
        lc_list.append(key)

print(lc_list)

for key in data:
    if "pattern" in key:
        print(data[key][0])