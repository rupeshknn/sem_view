import json

def search_json_keys():
    with open("metadata_dump.json", "r") as f:
        data = json.load(f)
        
    targets = ['eht', 'volt', 'wd', 'working', 'mag', 'aperture', 'user', 'operator', 'serial', 'instrument']
    
    with open("matches.txt", "w") as f:
        f.write("--- Matches ---\n")
        for k, v in data.items():
            k_lower = k.lower()
            if any(t in k_lower for t in targets):
                f.write(f"{k}: {v}\n")

if __name__ == "__main__":
    search_json_keys()
