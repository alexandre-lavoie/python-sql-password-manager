# Python-SQL CLI Password Manager 

## Overview  

A Password Manager to securely manage and store passwords with URL, username, and passwords fields. A Master Password is used to authenticate into the manager "Vault", where all other passwords are stored.  

## Requried Libraries  

```
pip3 install -r requirements.txt
```

## Setup  

### Step 1: Clone Project and Project Files   

```
git clone https://github.com/collinsmc23/python-sql-password-manager
```

### Step 2: Run Main.py  

Run main.py with all files inside the same directory.

```
main.py [ARGUMENT] [OPTIONS]
```

Example to add a password:

```
main.py add --url https://cybercademy.org --username gcollins
```

Example to list passwords:

```
main.py query --username gcollins 
```

More settings can be found in the help menu: 

```
main.py --help
```
