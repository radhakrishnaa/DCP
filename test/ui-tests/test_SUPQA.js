var log = require('loglevel');
log.setLevel('info');

 //var SUP_URL = 'http://localhost:8080';
 var SUP_URL = 'http://sup-qa.appspot.com'
var WEBDRIVER_WAIT_TIMEOUT = 60000;

var CONFIG = {
    supUrl: 'http://sup-qa.appspot.com',
    //supUrl: 'http://localhost:8080',
    loginId: 'ssudhaka@motorola.com',
    loginPassword: 'Cricket!23'
};

//var packg = '/Users/ssudhaka/Suba/git_repo/sustaining-tools/gdicfg/test/ui-tests/Automation/delta-ota-Blur_Version.98.6.0-98.6.1.XT907.Blurdev.en.US.zip'

function getConfig(cloudset) {
    var fs = require('fs');
    var file = __dirname + '/default_params.txt';

    cloudset = cloudset.toLowerCase();
    fs.readFile(file, 'utf8', function (err, data) {
        if (err) {
            log.error(err);
            return;
        }
        data = JSON.parse(data);
        if (cloudset in data) {
            log.dir(data[cloudset]);
        } else {
            log.error("No configs found for cloudset '" + cloudset + "'");
        }
    });
}
describe('SUPQA Sanity Tests', function() {

    //getConfig('QA300');

    var ptor = protractor.getInstance();
    var driver = ptor.driver;
    var findById = function (id) {
        return driver.findElement(protractor.By.id(id));
    };

    // Wait long enough to avoid NoSuchElementError
    driver.manage().timeouts().implicitlyWait(WEBDRIVER_WAIT_TIMEOUT);
    
    // Increase Protractor page sync timeout
    driver.manage().timeouts().setScriptTimeout(60000);
    
    var desc; 
    
   it('Do SSO login before running the actual tests', function() {
        log.info('Do SSO login before running the actual tests');
        driver.get(CONFIG.supUrl);
        findById('Email').sendKeys(CONFIG.loginId);
        findById('Passwd').sendKeys(CONFIG.loginPassword);
        findById('signIn').click();
        
    });
  
   it('Should be in the paths page after logging in', function() {
        log.info('Should be in the paths page after logging in');
        browser.get(SUP_URL +'/upgrades#/paths');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('/upgrades#/paths');
        }); 
      });  
        
   it('Should navigate to dogfood when clicked', function()  {
      log.info('Should navigate to dogfood when clicked'); 
      ptor.findElement(protractor.By.css('.dropdown-toggle')).click();
      ptor.findElement(protractor.By.linkText('Dogfood')).click();
      ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('/upgrades#/pathsdogfood');
        });
      });    
    
    // The following script will click on Add a new package dropdown on Dogfood
    
   it('Should click on Add a new package drop down', function() {
        log.info('Should click on Add a new package');
        ptor.findElement(protractor.By.css('.btn.dropdown-toggle')).click();
       // ptor.findElement(protractor.By.css('.btn.btn-link')).click();
       // ptor.findElement(protractor.By.linkText('Upload from Your Computer')).click();
        ptor.findElement(protractor.By.css('.btn.btn-link:nth-child(1)')).click();
        //ptor.findElement(protractor.By.css('.table.table-condensed')).isDisplayed();
        
    });
    
   ///Create a folder under ui-test and copy the OTA files(s) there. In my example below, I have created a folder called "Automation" under ui-tests. 
   it('Click on browse and select packages', function() {
        log.info('Click on browse and select packages');
        //ptor.findElement(protractor.By.css('.ng-isolate-scope')).click();
        ptor.findElement(protractor.By.xpath('//input[@type = "file"]')).click();
        ptor.findElement(protractor.By.xpath('//input[@type = "file"]')).sendKeys('/Users/ssudhaka/Suba/git_repo/sustaining-tools/gdicfg/test/ui-tests/Automation/delta-ota-Blur_Version.98.6.0-98.6.1.XT907.Blurdev.en.US.zip');
        waits(10000);

        }); 
        
   it('Should click on UploadNow', function(){
            log.info('It should click on Upload now');
        ptor.findElement(protractor.By.css('.btn.ng-scope')).click();
          expect(ptor.getCurrentUrl()).toContain('upgrades#/pathsdogfood/edit/');
          // asserting
        element.all(by.tagName('h1')).then(function(h1) {
         expect(h1[0].getText()).toBe('Manage an Upgrade Path (Dogfood)');
     });    
   }); 
   
   it('Should click on edit', function(){
         log.info('It should click on edit');
       ptor.findElement(protractor.By.xpath('//input[@type = "submit" and @value = "Edit"]')).click();
       waits(10000);
       ptor.findElement(protractor.By.linkText('Polling Schedule')).click();
       waits(10000);
    });  
      
  /* it('It should click on the hidden Add Schedule', function() {
        var hiddenElement = driver.findElement(protractor.By.xpath('html/body/div[1]/div[3]/accordion/div/div[1]/div/div/div[2]/div/div/div/div/button'));
        driver.executeScript("arguments[0].click()", hiddenElement).then(function() {
            expect(arguments[0].getText()).toBe('Add new schedule'); 
      });
    }); */
    
          
          
   /* it('Should click on the Add schedule', function() {
          log.info('Should click on the Add Schedule');
       var scheduleBtn = element.all(by.className('btn'));
       scheduleBtn.then(function(btn) {
         expect(btn[0].getText()).toBe('Add new schedule');
        });
       scheduleBtn.click();
      });    */
      
      it('Should click on the Add schedule', function() {
         log.info('Should click on Add Schedule');
         var items = element.all(by.className('btn'));
    for (var i = 0; i < items.length; i++) {
       if (items[i].getAttribute("Add new schedule") === "0") {
           items[i].click();
    }
   }    
   });   
   
  
   
           
      
});  

