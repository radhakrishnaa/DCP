
// Use Jasmine reporter to output test results in XML format. Before running, you will 
// need to 'npm install jasmine-reporters'
//   @todo : configure protractor so we don't have to give an explicit path to require()
require('../protractor/node_modules/jasmine-reporters');

// SUP tester configuration file

exports.config = {
  // Uncomment the following 2 lines so Protractor will auto-launch the Selenium webserver
  seleniumServerJar: '/Users/ssudhaka/Suba/git_repo/sustaining-tools/gdicfg/test/protractor/selenium/selenium-server-standalone-2.37.0.jar',
  chromeDriver: '/Users/ssudhaka/Suba/git_repo/sustaining-tools/gdicfg/test/protractor/selenium/chromedriver',
  
  // Or uncomment the following line if you are manually running the Selenium webserver
  SeleniumAddress: 'http://localhost:4444/wd/hub',

  // Capabilities to be passed to the webdriver instance.
  capabilities: {
    'browserName': 'chrome'
  },

  // Spec patterns are relative to the current working directly when
  // protractor is called.
  specs: ['test_ui_sanity.js',
    //'test_SUPQA.js',
    //'test_download.js'
  ],

  onPrepare: function() {
    jasmine.getEnv().addReporter(
      new jasmine.JUnitXmlReporter('xmloutput', true, true));
  },

  // Options to be passed to Jasmine-node.
  jasmineNodeOpts: {
    showColors: true,
    defaultTimeoutInterval: 120000      // entire spec must complete before this time
  }
};
