<img src="logo.png">

## WHAT?
Python script that automates initialising new Ubuntu server (not tested on other distros) - upgrade, install basic stuff, configure web server - all in one click.

## DOCUMENTATION

### PASSWORDS

You HAVE to write ONLY the ROOT pass (<b>'root\_pass'</b>) for server, other passwords will be generated.

<b>'password\_format'</b> options: <b>'txt'</b> (simple txt file) and <b>'pdf'</b> (fancy file with logo).

### NEW

For new installation delete <b>'user\_pass'</b>'s value (but not the key!) - if exist already means that the script already had been executed and created a new user. It will skip the create new user part.

### SERVER

<b>'server'</b> options:

'<b>1</b>' = Apache

'<b>2</b>' = Nginx

'<b>3</b>' = Apache with Nginx as reverse proxy (not available in this version)

### PROGRAMMING LANGUAGE

<b>'language'</b>(s) available:

<b>'python'</b>

<b>'php'</b>

Each must have '<b>v</b>' (version) in float

### DATABASE

<b>'db'</b> available:

<b>'maria'</b> (Mariadb)

<b>'mongo'</b> (Mongodb)

Only <b>'gui'</b> option available is <b>'phpmyadmin'</b> for <b>'maria'</b>

<b>'dbuser'</b> and <b>'dbname'</b> for both DB are optional, by default it will be <b>'admin'</b> and <b>'main\_db'</b>

### DOMAINS

<b>'domains'</b> options:

<b>'wp'</b> (not available in this version)

<b>'django'</b> (not available in this version)

Can be <b>empty</b> (will install empty HTML file)