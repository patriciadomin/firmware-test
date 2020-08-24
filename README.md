This is an experimental version for checking HPE GEN10 available firmwares

You need to download a .json provided by HPE:
To do that:

A user-generated token must be supplied as the http username to access these repositories.
Login with your HPE Passport credentials and generate your token.
The instructions and links are available here: 
http://downloads.linux.hpe.com/project/fwpp/fwget.html

A user-generated token must be supplied as the http username to access these repositories.
Login with your HPE Passport credentials and generate your token.
Once you have a valid token, you may access the FWPP repositories.
NOTE: you must additionally have an active warranty or support contract linked to your HPE
Passport account to access HPE firmware updates for ProLiant G7, Gen8 and Gen9 servers.
Warranty/support is NOT required for Gen10 servers.

Once you have a valid token, you may access the FWPP repositories with: 
wget --user=$HPE_TOKEN --password=
https://downloads.linux.hpe.com/SDR/repo/fwpp-gen10/current/fwrepodata/fwrepo.json
