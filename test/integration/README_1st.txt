README_1st.txt

SUMMARY
=======

This folder contains the automated testsuite for testing the Upgrade Management service. 
It uses PyTest (pytest.org) as the test execution framework. There are two ways to run 
the testsuite:

1. On the QA Jenkins server
  * Login to http://qabuild01.qa.blurdev.com/
  * Search for "Test_SUP_API"
  * Click on the "Build Now" link

  You get two benefits when running the tests on QA Jenkins: a nice-looking report in 
  JUnit format and your results are saved (for a while) for historical tracking.
  
2. On your computer

  Running locally allows you to modify the tests without redeploying, run a debug 
  trace, etc.


SOURCE TREE ORGANIZATION
========================

The testsuite is located under the gdicfg/test/integration folder. The actual 
testcases are in the Tests-* folder (eg, "Tests-Component"). Since we use py.test 
to execute the testsuite, it automatically finds the tests.

test
├── integration
│   ├── README_1st.txt
│   ├── README_create.txt
│   ├── Tests-Component
│   │   ├── SUP_TruthTable.csv
│   │   ├── test_listaccess.py
│   │   └── test_upgrades.py
│   ├── autojenkins.py
│   ├── cceclient.py
│   ├── common.py
│   ├── conftest.py
│   ├── create.py
│   ├── default_params_cce.txt
│   ├── fabfile.py
│   ├── gdihelper.py
│   ├── tlmsdriver.py
│   └── umdriver.py


HOW TO SET UP THE SUP TESTSUITE ON YOUR LOCAL COMPUTER
======================================================

The following sections explain how to setup and run the testsuite locally.

PREREQUISITES
=============

1. Install py.test as follows

  $ pip install pytest   (or 'easy_install pytest')

2. Copy the cceclient.py and default_params_cce.txt files into this folder. You can get 
   these from the Dilbert repo under "infrastructure/public/tools/cceclient"

  @TODO: Write a build script that automatically copies these files
    

RUNNING THE TESTS
=================

1. Before running the test, do the following:

   - Add the test IMEI (91375827384896 if you're testing on SDC200, or 91375829555018 for 
    QA300) to the UM Portal's master whitelist
   - The OTA package used for testing is still in Jenkins. Currently it is
   
    zipFileUrl = 'http://jenkins-main.am.mot.com/view/XLine-Daily/job/platform_dev_ghost-verizon_userdebug_main-jb-qcpro-4.2-xline_linux_daily/169/artifact/platform/release/ghost_verizon/OTA/delta-ota-Blur_Version.13.0.3008-13.0.3019.ghost_verizon.Verizon.en.US.zip'
    sourceVersion = 'Blur_Version.13.0.3008.ghost_verizon.Verizon.en.US'
    
   - If the package no longer exists in Jenkins, choose another one (eg, the latest) and replace the following 2 lines inside the
      function "test_UmService_CreatePath_PathIsCreated()" in Tests-Component/test_umservice.py

    zipFileUrl = '<your_new_OTA_package_zip_url>'
    sourceVersion = '<your_new_OTA_package_source_version'

   - Uncomment the appropriate IMEI inside the function test_UmService_CreatePath_PathIsCreated() 
     for the cloudset where you will run the test on.

2. Run py.test in verbose mode, specifying the cloudset to test against

  $ py.test -s -v --cloudset sdc200


MODIFYING TESTS AND UPDATING QA JENKINS
=======================================

If you modify the tests, push your changes to Git and also update QA Jenkins. There is 
Fabric file that makes the update easy:

  $ cd gdicfg/test/integration
  $ fab zip         (this creates the "integration.zip" file)
  $ fab deploy      (this pushes the zip file to QA Jenkins)
  
Then test by running a new Test_SUP_API job and reviewing the results.


EXAMPLE OUTPUT
==============

$ py.test -s -v --cloudset sdc200
=============================================== test session starts ================================================
platform darwin -- Python 2.6.7 -- pytest-2.3.4 -- /usr/bin/python2.6
collected 5 items 

Tests-Component/test_umservice.py:25: test_UmService_ListPaths_ReturnsPaths 
INFO: *** test_UmService_ListPaths_ReturnsPaths:
PASSED

Tests-Component/test_umservice.py:42: test_UmService_GetPath_ReturnsPath 
INFO: *** test_UmService_GetPath_ReturnsPath:

INFO: *** test_UmService_ListPaths_ReturnsPaths:
INFO: Getting profile for a randomly chosen upgradePath 47c2bd05-d63a-4000-b937-a03cba1c3b36
INFO: Yup, got the path info
PASSED

Tests-Component/test_umservice.py:60: test_UmService_GetNonexistentPath_ReturnsProfileDoesNotExist 
INFO: *** test_UmService_GetNonexistentPath_ReturnsProfileDoesNotExist:
PASSED

Tests-Component/test_umservice.py:74: test_UmService_CreatePath_PathIsCreated 
INFO: *** test_UmService_CreatePath_PathIsCreated:
INFO: Successfully created upgradePath 3dab3bac-b17f-43fb-a292-c6d65e4bb972
INFO: Downloading OTA package from https://dlmgr-sdc200.blurdev.com/dl/dlws/1/download/40G60NT8psaVUAjs%2BVVUSC45n92Ll3Q97AfokQjOBllB%2F%2Fsrr9%2FTGcSPHtQRXWjlYPkfe9LYyo4rAHoGb%2FW7x1HHaAV7gYOOrFHFrsaENFI%3D
INFO: Saving to file Blur_Version.13.0.3008.ghost_verizon.Verizon.en.US.zip...
Fetching OTA package...
INFO: Download complete. OTA package saved in Blur_Version.13.0.3008.ghost_verizon.Verizon.en.US.zip
INFO: Deleting upgradePath... deleteUrl= http://ipws-ssota-sdc200.blurdev.com/upgrade-management/1/upgradepaths/3dab3bac-b17f-43fb-a292-c6d65e4bb972
PASSED

Tests-Component/test_umservice.py:105: test_UmService_CreateExistingPath_ReturnsPathExists 
INFO: *** test_UmService_CreateExistingPath_ReturnsPathExists:
INFO: Created upgradePath 473cc74d-f2ad-40a9-80db-16076a409bc5; now test if we can create it again..
INFO: Good, UM service reported that path already exists.
INFO: Deleting upgradePath... deleteUrl= http://ipws-ssota-sdc200.blurdev.com/upgrade-management/1/upgradepaths/473cc74d-f2ad-40a9-80db-16076a409bc5
PASSED

============================================ 5 passed in 15.40 seconds =============================================




