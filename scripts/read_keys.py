def read_keys():
    try:
        with open("context_keys.txt", "r", encoding="utf-8", errors="ignore") as f:
            print(f.read())
    except Exception as e:
        print(e)

if __name__ == "__main__":
    read_keys()
