import sys
import json
import csv

TYPE = 1    # 1 for logins | 2 for notes
USERNAME = 'username'
PASSWORD = 'password'
ID = 'id'
FILE_TYPE = '.json'
ITEMS = 'items'

# important keys
KEY = '1ba00727-d416-4c69-985e-b4fc00781baa'
KEY_LIST: list[str] = []

# configs
SHOW_DUPLICATES = False     # TRUE - print list of duplicates | FALSE - print list of non duplicates
SHOW_IMPORTANT = False      # TRUE - sets important keys as duplicates | FALSE - set important keys as non-duplicates
SHOW_STATS = False          # TRUE - print stats after running script
PRINT_JSON = True           # TRUE - outout to json
PRINT_CSV = False           # TRUE - output to csv
PRINT_TXT = False           # TRUE - output to text file
DELIMITER = '+'             # delimeter for multi-key flags
INPUT_FILE = None           # input file name (.json)
OUTPUT_FILE = 'output'      # output file name (omit file extension)
STD_OUT = False

# flags
show_imp = '-i'
hide_imp = '-ii'
show_dup = '-d'
hide_dup = "-n"     # non-duplicates
show_stat = '-s'
hide_stat = '-ss'
std_out = '-std'
text = '-txt'
json_ = '-json'
csv_ = '-csv'
help = '-h'
keys = 'key='
dels = 'del='
out = 'out='

FLAGS = {
          show_imp: "include important keys"
        , hide_imp: "exclude important keys"
        , show_dup: "show duplicates"
        , hide_dup: "show non-duplicates"
        , show_stat: "hide stats"        
        , hide_stat: "show stats"        
        , std_out: "enable output to standard out (console)"
        , help: "help"
        , keys: "'key=' followed by a single key you want to keep e.g. key=apple if your key is apple"
        , dels: "'del=' set the delimiter (default '+') for multi key support eg. apple+orange+grape"
        , json_: "export to json file [output.json]"
        , text: "export to sysout [default]"
        , csv_: "export to csv file [output.csv]"
        , out: "'out=' followed by the output file name (omit file extension)"
        }


# get the data from a file
def getFileData(filename : str) -> list[dict]:
    with open(filename, "r") as file:
        result = json.load(file)
    
    return (result, result.get(ITEMS))


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
def extractDuplicateID(lines: list[dict]) -> list[int]:
    duplicates = []

    outer = 0    
    while outer < len(lines):
        added = False
        inner = outer + 1

        user1:dict = lines[outer].get("login")
        if inner < len(lines): user2:dict = lines[inner].get("login")

        while inner < len(lines) and equalLogins(user1, user2):

            inKey = lines[inner].get(ID) == KEY or lines[outer].get(ID) == KEY
            inKey_list = len(KEY_LIST) > 0 and (lines[inner].get(ID) in KEY_LIST or lines[outer].get(ID) in KEY_LIST)

            if inKey or inKey_list:
                duplicates.append(lines[outer].get(ID) if importantKeysFilter(inner, lines) else lines[inner].get(ID))
            else: duplicates.append(lines[inner].get(ID))
            inner = inner + 1
            if inner < len(lines): user2 = lines[inner].get("login")

        outer = inner                  

    return duplicates 


# extrant final list based on SHOW_DUPLICATES
def extractDuplicateList(lines: list[dict], duplicates: list[int]) -> list[dict]:
    return [line for line in lines if printFilter(duplicates, line.get(ID))]


# output to json file
def printJSON(lines: list[dict], filename: str) -> None:
    with open(filename, 'w') as file:
        file.writelines(json.dumps(lines, indent=2))


# output to csv file
def printCSV(lines: list[dict]) -> None:
    with open(f"{OUTPUT_FILE}.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=set([key for line in lines for key in line]))
        writer.writeheader()
        writer.writerows(lines)

# #############################
# HELPER FUNCTIONS
# ############################ 


# protects important keys depending on display conditins
# determines where the important keys go
# if you want to display duplicates it excludes keys
# if you want to display none duplicates to displays keys
def importantKeysFilter(inner: int, lines : list[dict]) -> bool:
    listProvided = len(KEY_LIST) > 0

    if lines[inner].get(ID) == KEY or (listProvided and lines[inner].get(ID) in KEY_LIST): return not SHOW_IMPORTANT
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
    [print(f"{k} ---> {v}") for k,v in FLAGS.items()]
    sys.exit(0)


if __name__ == '__main__':

    # configure script
    for flag in  sys.argv[1:]:

        # important key configs (order matters for defaults if both flags are passed)
        if flag == show_imp: SHOW_IMPORTANT = True
        if flag == hide_imp: SHOW_IMPORTANT = False  # (def)

        # output list configs (same as above)
        if flag == hide_dup: SHOW_DUPLICATES = False
        if flag == show_dup: SHOW_DUPLICATES = True     # (def)

        # statitics config (same as above)
        if flag == hide_stat: SHOW_STATS = False
        if flag == show_stat: SHOW_STATS = True     # (def)

        # help prompt
        if flag == help: printHelp()

        # input and output configs (non '-' notation)
        if flag.endswith(FILE_TYPE): INPUT_FILE = flag
        if flag.count(DELIMITER): KEY_LIST = [x.strip() for x in flag.split(DELIMITER)]
        if flag.startswith(keys): KEY = flag[len(keys):]
        if flag.startswith(dels): DELIMITER = flag[len(dels):]
        if flag.startswith(out): OUTPUT_FILE = flag[len(out):]

        # supports multiple output formats
        if flag == json_: PRINT_JSON = True
        if flag == csv_: PRINT_CSV = True
        if flag == text: PRINT_TXT = True
        if flag == std_out: STD_OUT = True


    if INPUT_FILE is None: 
        print("Source file not provided. Please provide a .json file")
        sys.exit(1)

    # open file and store details in a list[dict]
    # filter out all none type 1 (non logins)   
    # sort by login.uris.uri
    completeFIle, items = getFileData(INPUT_FILE)
    lines = sortByURI(filterLoginsOnly(items))

    # group by URI (only group URI with multiple entries)
    duplicateURIs = groupDuplicateURI(lines)   

    # group by username (further filtering for duplicates [uri + username = same account])
    duplicateUsernames = groupByKey(duplicateURIs, USERNAME)   

    # printDuplicates(duplicates2)
    duplicates = extractDuplicateID(duplicateUsernames)

    # list to export
    final_list = extractDuplicateList(items, duplicates)

    # TODO let users choose if they want output in complete format or compact format (text and JSON)
    completeFIle[ITEMS] = final_list

    # export duplicates
    if PRINT_TXT: printJSON(completeFIle, f"{OUTPUT_FILE}.txt")
    if PRINT_JSON: printJSON(completeFIle, f"{OUTPUT_FILE}.json")
    if PRINT_CSV and len(final_list): printCSV(final_list)
    if STD_OUT: print(json.dumps(completeFIle, indent=2))

    # print duplicates stats
    if SHOW_STATS:
        print("URI ->", f"total - {len(lines)}", f"duplicates - {len(duplicateURIs)}", f"dif = {len(lines) - len(duplicateURIs)}")
        print("USERNAME ->", f"total - {len(duplicateURIs)}", f"duplicates - {len(duplicateUsernames)}", f"dif = {len(duplicateURIs) - len(duplicateUsernames)}")
        print("DUPLICATES ->", f"total - {len(duplicateUsernames)}", f"duplicates - {len(duplicates)}", f"dif = {len(duplicateUsernames) - len(duplicates)}")
        print("FINAL ->", f"total - {len(lines)}", f"duplicates - {len(duplicates)}", f"dif = {len(lines) - len(duplicates)}")
        print(f"TOtal accounts to delete -> {len(duplicates)}")

    # end program
    sys.exit(0)