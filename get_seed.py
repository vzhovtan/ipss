import yaml

lc_list = []

with open("seed.yml", 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)

print(data)
for key in data:
    print(key)
    lc_list.append(key)

print(lc_list)