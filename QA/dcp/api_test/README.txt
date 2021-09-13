Setup
=====

1) Setup using VirtualEnv:

    pip install virtualenv

    virtualenv .venv

    source .venv/bin/activate

2) Install requirements

    pip install -r requirements.txt


Running DCP API Tests
=====================

1) Enter your Virtual Environment:

    source .venv/bin/activate

2) Before running tests the first time, it's needed to authenticate in DCP
   Portal using the following command:

   python cas_login.py http://localhost:8000/


3) Choose one of the following:

 a) Run all tests for QA environment:

    py.test --hostname=http://ws001-dcp-qa300.ilc.blurdev.com/


 b) Run all tests for localhost:

    py.test --hostname=http://localhost:8000/


 c) Run only a specific testsuite: (carrier table tests, for instance)

    py.test --hostname=http://localhost:8000/ table/test_carrier.py
