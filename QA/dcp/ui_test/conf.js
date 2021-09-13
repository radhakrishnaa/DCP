exports.config = {
    // The following 2 params don't seem to do anything!!!  12/15/13
//  seleniumServerJar: '/Users/xhbn37/git/sustaining-tools/gdicfg/test/protractor/selenium/selenium-server-standalone-2.37.0.jar',
        // '../selenium/selenium-server-standalone-2.35.0.jar',
//  chromeDriver: '/Users/xhbn37/git/sustaining-tools/gdicfg/test/protractor/selenium/chromedriver',
        // '../selenium/chromedriver',

  seleniumAddress: 'http://localhost:4444/wd/hub',

  allScriptsTimeout: 240000,

  capabilities: {
    'browserName': 'chrome',
    'chromeOptions': {
        'args': ['--user-data-dir=/tmp/dcp_tests/']
    }
  },

  specs: ['dcp_spec.js'],

  // Options to be passed to Jasmine-node.
  jasmineNodeOpts: {
    showColors: true,
    defaultTimeoutInterval: 240000 // entire spec must complete before this time
  }
};
