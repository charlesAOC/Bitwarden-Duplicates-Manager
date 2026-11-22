# Bitwarden Duplicate Password Manager

* manage duplicate bitwarden passwords
* full privacy and security. script runs completely in terminal
* configurable
* Python required

## Requirements

* Python 3
* CLI
* bitwarden .json source file

## Running script

```bash
py bit-duplicates.py file_name.json
```

## Configurations

**Example Configuration**

```bash
py bit-duplicates.py -i file_name.json -std key=test-key -txt
```

-i          --->     include important keys (default)
-ii         --->    exclude important keys
-d         --->     show duplicates
-n         --->     show non-duplicates (default)
-s          --->    hide stats (default)        
-ss        --->     show stats
-std      --->     enable output to standard out (console)
-h         --->     help
key=     --->   'key=' followed by a single key you want to keep e.g. key=apple if your key is apple
del=     --->   'del=' set the delimiter (default '+') for multi key support eg. apple+orange+grape
-json    --->    export to json file [output.json] (default)
-txt       --->    export to sysout [default]
-csv      --->    export to csv file [output.csv]
out=     --->   'out=' followed by the output file name (omit file extension) (default = output)

## Why I made this script

I recently bought a new windows PC. In my quest to customize it, i learned a lot about open source softwares like windhawk, betterbird, bitwarden etc.

Migrating to bitwarden posed a few problems. I used google's password manager paired with the apple passwords app in the past. As you can imagine merging both sources into one created annoying duplicates. 

Bitwarden didnt provide a tool to do this on scale so i thought to write my own.

I hope this script helps you the way it helped me.