
import sys
import json

TYPE = 1    # 1 for logins | 2 for notes

# get the data from a file
def getFileData(filename : str) -> list[dict]:
    with open(filename, "r") as file:
        result = json.load(file)

    result = result.get("items")
    
    return result


# filter out non-login data
def filterTypes(lines: list[dict]) -> list[dict]:
    return [i for i in lines if i.get('type') == TYPE]


#sort list items by URI
def sortByURI(lines: list[dict]) -> list[dict]:
    return sorted(lines, key=getURI)


# find all URI duplictes. return them as list
def groupByURI(lines: list[dict]) -> list[dict]:
    duplicates = []
    outer = 0

    while outer < len(lines) - 1:
        added = False
        inner = outer + 1

        while inner < len(lines) and getURI(lines[inner]).startswith(getURI(lines[outer])):
            # add comparator only on the first match
            if not added:
                duplicates.append(lines[outer])    

            duplicates.append(lines[inner])
            added = True

            inner = inner + 1

        outer = inner                  

    return duplicates 


def groupByKey(lines: list[dict], key: str) -> list[dict]:
    duplicates = []
    outer = 0

    while outer < len(lines) - 1:
        added = False
        inner = outer + 1

        user1:str = lines[outer].get("login").get(key)
        user2:str = lines[inner].get("login").get(key)

        while inner < len(lines) and user1 is not None and user2 is not None and user2.startswith(user1):
            # add comparator only on the first match
            if not added:
                duplicates.append(lines[outer])    

            duplicates.append(lines[inner])
            # printGroups(added, getURI(lines[outer]))
            added = True


            inner = inner + 1
            if inner < len(lines): user2 = lines[inner].get("login").get(key)

        outer = inner                  

    return duplicates 


def printGroups(added: bool, URI: str):
    print(f"{URI if not added else " " * len(URI)} - {URI}", "\n")


#return the URI of a list item~~
def getURI(line: dict) -> str:
    return line.get("login").get("uris")[0].get("uri")

def printDuplicates(list: list[dict]):
    for i in list:
        for k,v in i.items():
            print(f"{k}: {v}")
        print("\n")


if __name__ == '__main__':
    # retrieve args
    args = sys.argv[1:]  # Exclude the script name
    fileName = args[0]

    # open file (json) and store details in a list 2x2
    lines = getFileData(fileName)

    # filter out all type ones
    lines = filterTypes(lines)
    
    # sort by login.uris.uri
    lines = sortByURI(lines)

    # group by URI
    duplicates = groupByURI(lines)   

    # group by username
    duplicates2 = groupByKey(duplicates, "username")   

    printDuplicates(duplicates2)

    print("USERNAME ->", f"total - {len(duplicates)}", f"duplicates - {len(duplicates2)}", f"dif = {len(duplicates) - len(duplicates2)}")
    print("URI ->", f"total - {len(lines)}", f"duplicates - {len(duplicates2)}", f"dif = {len(lines) - len(duplicates2)}")