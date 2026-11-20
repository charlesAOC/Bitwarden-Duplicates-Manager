
import sys
import json

TYPE = 1    # 1 for logins | 2 for notes
USERNAME = 'username'
PASSWORD = 'password'
ID = 'id'
IMPORTANT_KEY = '1ba00727-d416-4c69-985e-b4fc00781baa'
PRINT_DUPLICATES = True     # set to false to print list of non duplicates

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


# find all URI duplictes. return them as list (group by URI)
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

# group data by key
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

# extract ID of duplicates to be deleted
def groupDuplicateIDs(list: list[dict]) -> list[int]:
    duplicates = []

    outer = 0    
    while outer < len(lines):
        added = False
        inner = outer + 1

        user1:dict = lines[outer].get("login")
        if inner < len(lines): user2:dict = lines[inner].get("login")

        while inner < len(lines) and equals(user1, user2):
            if lines[inner].get(ID) == IMPORTANT_KEY or lines[outer].get(ID) == IMPORTANT_KEY:
                duplicates.append(lines[outer].get(ID) if lines[inner].get(ID) == IMPORTANT_KEY else lines[inner].get(ID) == IMPORTANT_KEY  )
            else: duplicates.append(lines[inner].get(ID))
            inner = inner + 1
            if inner < len(lines): user2 = lines[inner].get("login")

        outer = inner                  

    return duplicates 

# prints the list of duplicate accounts
def printDuplicates(lines: list[dict], duplicates: list[int]):
    [[print(f"{k}: {v} {'\n' if i == len(x.items()) -1 else ""}") for i,(k,v) in enumerate(x.items()) ] for x in lines if printDuplicatesEquals(duplicates, x.get(ID))]

def printDuplicatesEquals(duplicates: list[dict], id: int):
    if PRINT_DUPLICATES: return id in duplicates
    return id not in duplicates

# check whether 2 logins are the same username & password match
def equals(user1: dict, user2: dict):
    if user1 is not None and user2 is not None:
        if user1.get(USERNAME) == user2.get(USERNAME):
            if user1.get(PASSWORD) == user2.get(PASSWORD):
                return True
    return False

# helpre function for debugging
def printGroups(added: bool, URI: str):
    print(f"{URI if not added else " " * len(URI)} - {URI}", "\n")

#return the URI of a list item~~
def getURI(line: dict) -> str:
    return line.get("login").get("uris")[0].get("uri")

# prints the duplicates list data line by line
def printDuplicatesHelper(list: list[dict]):
    for i in list:
        for k,v in i.items():
            print(f"{k}: {v}")
        print("\n")


if __name__ == '__main__':
    # retrieve args
    args = sys.argv[1:]  # Exclude the script name
    # fileName = args[0]
    fileName = "bitwarden_export_20261120010454.json"

    # open file (json) and store details in a list 2x2
    lines = getFileData(fileName)

    # filter out all type ones
    lines = filterTypes(lines)
    
    # sort by login.uris.uri
    lines = sortByURI(lines)

    # group by URI
    duplicateURIs = groupByURI(lines)   

    # group by username
    duplicateUsernames = groupByKey(duplicateURIs, USERNAME)   

    # printDuplicates(duplicates2)
    duplicates = groupDuplicateIDs(duplicateUsernames)
    # [print(x) for x in duplicates]
    printDuplicates(lines, duplicates)

    print("URI ->", f"total - {len(lines)}", f"duplicates - {len(duplicateURIs)}", f"dif = {len(lines) - len(duplicateURIs)}")
    print("USERNAME ->", f"total - {len(duplicateURIs)}", f"duplicates - {len(duplicateUsernames)}", f"dif = {len(duplicateURIs) - len(duplicateUsernames)}")
    print("DUPLICATES ->", f"total - {len(duplicateUsernames)}", f"duplicates - {len(duplicates)}", f"dif = {len(duplicateUsernames) - len(duplicates)}")
    print("FINAL ->", f"total - {len(lines)}", f"duplicates - {len(duplicates)}", f"dif = {len(lines) - len(duplicates)}")
    print(f"\nTOtal accounts to delete -> {len(duplicates)}")