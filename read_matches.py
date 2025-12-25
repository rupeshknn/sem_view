def read_matches():
    with open("matches.txt", "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if i < 50:
                print(line.strip())

if __name__ == "__main__":
    read_matches()
