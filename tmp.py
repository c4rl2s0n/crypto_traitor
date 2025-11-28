import json

t = open("tmp3.json").read()
j = json.loads(t)
links = j["links"]
for key in links.keys():
    entry = links[key]
    if entry is None:
        continue
    if isinstance(entry, str):
        print(f"{key}: {entry}")
    if isinstance(entry, list):
        if len(entry) == 0:
            continue
        print("List")
        for link in entry:
            print(f"{key}: {link}")
    if isinstance(entry, dict):
        print("Dict")
        for ekey in entry.keys():
            for link in entry[ekey]:
                print(f"{ekey}: {link}")

print(j)