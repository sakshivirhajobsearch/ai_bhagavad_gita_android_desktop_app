import os

def export_to_txt(shlokas):
    path = "exported_shlokas.txt"

    with open(path, "w", encoding="utf-8") as f:
        for s in shlokas:
            f.write(f"{s.get('section','')}\n")
            f.write(f"{s.get('problem','')}\n")
            f.write(f"{s.get('sloka','' )}\n")
            f.write(f"{s.get('text','')}\n")
            f.write(f"{s.get('meaning','')}\n")
            f.write(f"{s.get('example','')}\n")
            f.write("\n-----------------\n\n")

    return os.path.abspath(path)
