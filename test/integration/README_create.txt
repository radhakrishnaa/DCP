README.txt

create.py is a tool for creating fake CCE or legacy devices from an IMEI input list. 
It is designed to be integrated with other tools that will be used to run automated
regression tests on OTAMatic.

REQUIRED COMPONENTS
-------------------
1. Fabric (tested on 1.4.3)
2. admin-cmdline JAR file and libraries. You can build this from Butters; alternatively
   you can pull a snapshot from adm01.sdc2.svcmot.com:/home/xhbn37/admin-cmdline.tgz
   In any case, put the JAR file and lib into a folder called "admin-cmdline".

@TODO
1. Show deviceid for legacy devices; for this, we can just query GDI

---------------------------------------------------------------------------------------------------------
USAGE
-----

EXAMPLE 1: Create legacy devices

In this example, the ImeiListLegacy.txt contains the following lines:

1200999920121231001
1200999920121231002
1200999920121231003
1200999920121231004
1200999920121231005
1200999920121231006
1200999920121231007
1200999920121231008
1200999920121231009
1200999920121231010

Run the tool:

$ fab --fabfile create.py create_accounts:cloudset=QA300,blurVersion=Blur_Version.2.0.0.MB200.AmericaMovil.en.MX,imeifile=ImeiListLegacy.txt

cloudset=qa300  blurVersion=Blur_Version.2.0.0.MB200.AmericaMovil.en.MX  imeilist=ImeiListLegacy.txt cce=False
WARNING: Cannot open file 'default_params_legacy.txt' .. no parameters were read in
INFO: Account successfully created for IMEI 1200999920121231001
INFO: Account successfully created for IMEI 1200999920121231002
INFO: Account successfully created for IMEI 1200999920121231003
INFO: Account successfully created for IMEI 1200999920121231004
INFO: Account successfully created for IMEI 1200999920121231005
INFO: Account successfully created for IMEI 1200999920121231006
INFO: Account successfully created for IMEI 1200999920121231007
INFO: Account successfully created for IMEI 1200999920121231008
INFO: Account successfully created for IMEI 1200999920121231009
INFO: Account successfully created for IMEI 1200999920121231010

*** SUMMARY: created 10 of 10 IMEI accounts
---------------------------------------------------------------------------------------------------------

EXAMPLE 2: Create CCE devices (note the 'cce' flag)

In this example, the ImeiListCCE.txt contains the following lines:

1300999920121231001
1300999920121231002
1300999920121231003
1300999920121231004
1300999920121231005
1300999920121231006

$ fab --fabfile create.py create_accounts:cloudset=QA300,blurVersion=Blur_Version.0.0.3.XT926.Verizon.en.US,imeifile=ImeiListCCE.txt,cce=true

cloudset=qa300  blurVersion=Blur_Version.0.0.3.XT926.Verizon.en.US  imeilist=ImeiListCCE.txt cce=True
INFO: Defining a new device account...
INFO: DP service created new account: deviceid=882756914033139712, imei=1300999920121231001, blurVersion=Blur_Version.0.0.3.XT926.Verizon.en.US
INFO: Defining a new device account...
INFO: DP service created new account: deviceid=882756914040098816, imei=1300999920121231002, blurVersion=Blur_Version.0.0.3.XT926.Verizon.en.US
INFO: Defining a new device account...
INFO: DP service created new account: deviceid=882756914046681088, imei=1300999920121231003, blurVersion=Blur_Version.0.0.3.XT926.Verizon.en.US
INFO: Defining a new device account...
INFO: DP service created new account: deviceid=882756914053656576, imei=1300999920121231004, blurVersion=Blur_Version.0.0.3.XT926.Verizon.en.US
INFO: Defining a new device account...
INFO: DP service created new account: deviceid=873749714805923840, imei=1300999920121231005, blurVersion=Blur_Version.0.0.3.XT926.Verizon.en.US
INFO: Defining a new device account...
INFO: DP service created new account: deviceid=873749714812944384, imei=1300999920121231006, blurVersion=Blur_Version.0.0.3.XT926.Verizon.en.US

*** SUMMARY: created 6 of 6 IMEI accounts
