*You can follow the demo video on how to use this application at https://cisco.box.com/s/mwbnxwmax0rhtpd7plt9uuq59dzn94dx

Procedure to use this executable:
1. Extract the patcher.zip file
2. Open terminal in the same folder where executable is present.
3. Try running ./patcher --help
4. If you don't see any error, instead see a help message then patcher is ready to be used.
5. If you get an error saying permission Denied or unverified developer, then please open security&privacy tab on your mac, and click open anyway button to allow patcher application.
	you can visit https://support.apple.com/en-gb/HT202491 for more info.
6. Once done, you can add this application to global level by adding executable path to your environment variable.
7. After these 6 steps you can open your terminal in any random path, and just type $patcher --help and it will work!

Some sample usage commands

$ patcher --help
$ patcher -fpath .\dot11ax-7.7.385-SNAPSHOT.xar -ip 10.222.11.118 -cname network-pr -xde
$ patcher -fpath .\logback_debug_inv.xml -ip 10.222.11.118  -cname inventory -log

