
import sys
import json

TYPE = 1    # 1 for logins | 2 for notes
USERNAME = 'username'
PASSWORD = 'password'
ID = 'id'

# important keys TODO make this accept multiple
IMPORTANT_KEY = '1ba00727-d416-4c69-985e-b4fc00781baa'

# configs
SHOW_DUPLICATES = True     # TRUE - print list of duplicates | FALSE - print list of non duplicates
SHOW_IMPORTANT = False      # TRUE - sets important keys as duplicates | FALSE - set important keys as non-duplicates
SHOW_STATS = True           # TRUE - print stats after running script

# flags
show_imp = '-i'
hide_imp = '-o'
show_dup = '-d'
hide_dup = "-n"
show_stat = '-t'
hide_stat = '-u'
text = '-txt'
json_ = '-json'
help = '-h'


FLAGS = {
          show_imp: "show duplicates"
        , hide_imp: "hide duplicates"
        , show_dup: "include important keys"
        , hide_dup: "exclude important keys"
        , show_stat: "hide stats"        
        , hide_stat: "show stats"        
        , help: "help"
        }


# get the data from a file
def getFileData(filename : str) -> list[dict]:
    with open(filename, "r") as file:
        result = json.load(file)

    result = result.get("items")
    
    return result


# filter out non-login data
def filterLoginsOnly(lines: list[dict]) -> list[dict]:
    return [i for i in lines if i.get('type') == TYPE]


#sort list items by URI
def sortByURI(lines: list[dict]) -> list[dict]:
    return sorted(lines, key=getURI)


# find all URI duplictes. return them as list (group by URI)
def groupDuplicateURI(lines: list[dict]) -> list[dict]:
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


# group data by login key [username by default]
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


# extract duplicate IDs
def extractDuplicates(lines: list[dict]) -> list[int]:
    duplicates = []

    outer = 0    
    while outer < len(lines):
        added = False
        inner = outer + 1

        user1:dict = lines[outer].get("login")
        if inner < len(lines): user2:dict = lines[inner].get("login")

        while inner < len(lines) and equalLogins(user1, user2):
            if lines[inner].get(ID) == IMPORTANT_KEY or lines[outer].get(ID) == IMPORTANT_KEY:
                duplicates.append(lines[outer].get(ID) if importantKeysFilter(inner, lines) else lines[inner].get(ID))
            else: duplicates.append(lines[inner].get(ID))
            inner = inner + 1
            if inner < len(lines): user2 = lines[inner].get("login")

        outer = inner                  

    return duplicates 


# print output to sys out
def printDuplicates(lines: list[dict], duplicates: list[int]) -> None:
    [[print(f"{k}: {v} {'\n' if i == len(x.items()) -1 else ""}") for i,(k,v) in enumerate(x.items()) ] for x in lines if printFilter(duplicates, x.get(ID))]

# #############################
# HELPER FUNCTIONS
# ############################ 


# protects important keys depending on display conditins
# determines where the important keys go
# if you want to display duplicates it excludes keys
# if you want to display none duplicates to displays keys
def importantKeysFilter(inner: int, lines : list[dict]) -> bool:
    if lines[inner].get(ID) == IMPORTANT_KEY: return not SHOW_IMPORTANT
    else:  return SHOW_IMPORTANT


# chooses what goes to sys out [duplicates or non-duplicates]
def printFilter(duplicates: list[dict], id: int) -> bool:
    if SHOW_DUPLICATES: return id in duplicates     # prints duplicates to sys out
    return id not in duplicates         # prints non-duplicates to sys out


# check whether 2 logins are the same [username, password]
def equalLogins(user1: dict, user2: dict) -> bool:
    if user1 is not None and user2 is not None:
        if user1.get(USERNAME) == user2.get(USERNAME):
            if user1.get(PASSWORD) == user2.get(PASSWORD):
                return True
    return False


#return the URI of a list item
def getURI(line: dict) -> str:
    return line.get("login").get("uris")[0].get("uri")


# helpre function for debugging
# URI - URI
#     - URI
def printGroups(added: bool, URI: str) -> None:
    print(f"{URI if not added else " " * len(URI)} - {URI}", "\n")


# print help prompt
def printHelp():
    [print(f"{k} <--> {v}") for k,v in FLAGS.items()]


if __name__ == '__main__':
    # retrieve flags and filename
    *flags, fileName = sys.argv[1:]

    isHelp = False

    # configure script
    for flag in flags:
        if flag == show_imp: SHOW_IMPORTANT = True
        if flag == hide_imp: SHOW_IMPORTANT = False
        
        if flag == hide_dup: SHOW_DUPLICATES = False
        if flag == show_dup: SHOW_DUPLICATES = True

        if flag == hide_stat: SHOW_STATS = False
        if flag == show_stat: SHOW_STATS = True

        if flag == text: SHOW_IMPORTANT = True
        if flag == json_: SHOW_IMPORTANT = True
        if flags == help : isHelp = True

    if isHelp or fileName == help:
        printHelp()
    else:    

        #TODO
        # txt/json output

        # open file and store details in a list[dict]
        # filter out all none type 1 (non logins)   
        # sort by login.uris.uri
        lines = sortByURI(filterLoginsOnly(getFileData(fileName)))

        # group by URI (only group URI with multiple entries)
        duplicateURIs = groupDuplicateURI(lines)   

        # group by username (further filtering for duplicates [uri + username = same account])
        duplicateUsernames = groupByKey(duplicateURIs, USERNAME)   

        # printDuplicates(duplicates2)
        duplicates = extractDuplicates(duplicateUsernames)

        # print duplicates to sys out
        printDuplicates(lines, duplicates)

        # print duplicates stats
        if SHOW_STATS:
            print("URI ->", f"total - {len(lines)}", f"duplicates - {len(duplicateURIs)}", f"dif = {len(lines) - len(duplicateURIs)}")
            print("USERNAME ->", f"total - {len(duplicateURIs)}", f"duplicates - {len(duplicateUsernames)}", f"dif = {len(duplicateURIs) - len(duplicateUsernames)}")
            print("DUPLICATES ->", f"total - {len(duplicateUsernames)}", f"duplicates - {len(duplicates)}", f"dif = {len(duplicateUsernames) - len(duplicates)}")
            print("FINAL ->", f"total - {len(lines)}", f"duplicates - {len(duplicates)}", f"dif = {len(lines) - len(duplicates)}")
            print(f"\nTOtal accounts to delete -> {len(duplicates)}")