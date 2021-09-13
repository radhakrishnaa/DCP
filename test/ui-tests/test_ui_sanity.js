
var log = require('../protractor/node_modules/loglevel');
log.setLevel('info');

//var SUP_URL = 'http://localhost:8080';
var SUP_URL = 'http://icws-ssota-qa.blurdev.com'
var WEBDRIVER_WAIT_TIMEOUT = 60000;

var CONFIG = {
    supUrl: 'http://icws-ssota-qa.blurdev.com',
    //supUrl: 'http://localhost:8080',
    loginId: 'ota.testuser001@gmail.com',
    loginPassword: '8^KaQhQ5'
};


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


describe('SUP UI Sanity Tests', function() {

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

    // -----------------------------------------------------------------------------------
    //  Helper functions
    // -----------------------------------------------------------------------------------
    
    function uploadPackageA() {
        browser.get(SUP_URL + '/upgrades#/paths');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('/upgrades#/paths');
        });
        element(by.id('uploadImportPkg')).click();
        element(by.id('copyJenkinsArtifactory')).click();
        element(by.id('myFileURL')).sendKeys('http://8.35.197.229:8080/userContent/allpackages/delta-ota-Blur_Version.910.0.0-910.0.1.XT907.Blurdev.en.US.zip');
        element(by.id('myUserName')).sendKeys('test2014');
        element(by.id('myPassword')).sendKeys('test2014');
        //source
        element(by.xpath('//div[4]/form/table/tbody/tr/td[3]/input')).sendKeys('Blur_Version.910.0.0.XT907.Blurdev.en.US');
        //target
        element(by.xpath('//div[4]/form/table/tbody/tr[2]/td[3]/input')).sendKeys('Blur_Version.910.0.1.XT907.Blurdev.en.US');
        //fingerprint
        element(by.xpath('//div[4]/form/table/tbody/tr[3]/td[3]/input')).sendKeys('motorola/XT907_blurdev/test:4.1.2/9.8.1Q_51/900:userdebug/test-keys');
        //hwtype
        element(by.xpath('//div[4]/form/table/tbody/tr[5]/td[3]/input')).sendKeys('XT907');
        //carrier
        element(by.xpath('//div[4]/form/table/tbody/tr[6]/td[3]/input')).sendKeys('Blurdev');
        //region
        element(by.xpath('//div[4]/form/table/tbody/tr[7]/td[3]/input')).sendKeys('US');
        element(by.id('uploadBtn')).click();  
    }

    function uploadPackageB() {
        browser.get(SUP_URL + '/upgrades#/paths');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('/upgrades#/paths');
        });
        element(by.id('uploadImportPkg')).click();
        element(by.id('copyJenkinsArtifactory')).click();
        element(by.id('myFileURL')).sendKeys('http://8.35.197.229:8080/userContent/allpackages/delta-ota-Blur_Version.98.0.0-98.0.1.XT907.Blurdev.en.US.zip');
        element(by.id('myUserName')).sendKeys('test2014');
        element(by.id('myPassword')).sendKeys('test2014');
        //source
        element(by.xpath('//div[4]/form/table/tbody/tr/td[3]/input')).sendKeys('Blur_Version.98.0.0.XT907.Blurdev.en.US');
        //target
        element(by.xpath('//div[4]/form/table/tbody/tr[2]/td[3]/input')).sendKeys('Blur_Version.98.0.1.XT907.Blurdev.en.US');
        //fingerprint
        element(by.xpath('//div[4]/form/table/tbody/tr[3]/td[3]/input')).sendKeys('motorola/XT907_blurdev/test:4.1.2/9.8.1Q_51/800:userdebug/test-keys');
        //hwtype
        element(by.xpath('//div[4]/form/table/tbody/tr[5]/td[3]/input')).sendKeys('XT907');
        //carrier
        element(by.xpath('//div[4]/form/table/tbody/tr[6]/td[3]/input')).sendKeys('Blurdev');
        //region
        element(by.xpath('//div[4]/form/table/tbody/tr[7]/td[3]/input')).sendKeys('US');
        element(by.id('uploadBtn')).click();  
    }

    function uploadPackageC() {
        browser.get(SUP_URL + '/upgrades#/paths');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('/upgrades#/paths');
        });
        element(by.id('uploadImportPkg')).click();
        element(by.id('uploadFromComputer')).click();
        //choose file from your computer
        element(by.xpath('//div[2]/div/input')).sendKeys('/Users/nshukla/Downloads/delta-ota-Blur_Version.98.6.0-98.6.1.XT907.Blurdev.en.US.zip');
        //source
        element(by.xpath('//td[3]/input')).sendKeys('Blur_Version.98.6.0.XT907.Blurdev.en.US');
        //target
        element(by.xpath('//tr[2]/td[3]/input')).sendKeys('Blur_Version.98.6.1.XT907.Blurdev.en.US');
        //fingerprint
        element(by.xpath('//tr[3]/td[3]/input')).sendKeys('motorola/XT907_blurdev/test:4.1.2/9.8.1Q_51/800:userdebug/test-keys');
        //hwtype
        element(by.xpath('//tr[5]/td[3]/input')).sendKeys('XT907');
        //carrier
        element(by.xpath('//tr[6]/td[3]/input')).sendKeys('Blurdev');
        //region
        element(by.xpath('//tr[7]/td[3]/input')).sendKeys('US');
       // element(by.id('myGCSCheckbox')).click();
        element(by.id('myUploadButton')).click();     
    }

    function deletePackage() {
        element(by.id('myDeleteBtn')).click();
        element(by.xpath('//button[2]')).click();
    }
    
    function removeList() {
        element(by.id('searchIcon')).sendKeys('fgh');
        element(by.id('myActionDrpdown')).click();
        element(by.id('myRemoveList')).click();
    }


    // -----------------------------------------------------------------------------------
    //  Testcases
    // -----------------------------------------------------------------------------------

    it('Do SSO login before running the actual tests', function() {
        log.info('Do SSO login before running the actual tests');
        driver.get(CONFIG.supUrl);
        findById('Email').sendKeys(CONFIG.loginId);
        findById('Passwd').sendKeys(CONFIG.loginPassword);
        findById('signIn').click();
      
        // Do the CAS workaround thing... replace the https URL with http twice
        driver.wait(function() {
            return driver.getTitle().then(function(title) {
                return (/is not available/.test(title)) ? title : false;
            });
        }).then(function(title) {
            var url = title.replace('https:','http:', 1).replace(' is not available','');
            log.debug("Redirecting to " + url);
            driver.get(url);
            driver.wait(function() {
                return driver.getTitle().then(function(title) {
                    return (/is not available/.test(title)) ? title : false;
                });
            }).then(function(title) {
                url = title.replace('https:','http:', 1).replace(' is not available','');
                log.debug("Redirecting2 to " + url);
                driver.get(url);                
                ptor.waitForAngular();
                expect(ptor.getCurrentUrl()).toContain('/upgrades#/paths');
            });
        });

    });
    
    it('should be in the paths page after logging in', function() {
        log.info('should be in the paths page after logging in');
        browser.get(SUP_URL +'/upgrades#/paths');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('/upgrades#/paths');
        });
    });

    it('should find the "Upload/Import a Package" button', function() {
        log.info('should find the "Upload/Import a Package" button');
        var btn = $('#uploadImportPkg');
        expect(btn.getText()).toEqual('Upload/Import a Package');
    });

    it('should display at least one plan (may fail for a new environment)', function() {
        log.info('should get the source version of the first SUP');
        var paths = element.all(by.repeater('path in paths').column('path.upgradePath.sourceVersion'));        
        paths.then(function(arr) {
            arr[0].getText().then(function(srcVersion) {
                expect(srcVersion).toContain('Blur_Version');
            });
        });
    });
    
    /*
    it('should enumerate all the SUPs', function() {
        log.info('should enumerate all the SUPs');
        var pathUrls = [];
        var pathFields = [];
        element.all(by.repeater('path in paths')).then(function(paths) {
            paths.forEach(function(path) {
                path.getAttribute('onclick').then(function(onclickHref) {
                    onclickHref = onclickHref.replace('document.location.href=', '');
                    pathUrls.push(onclickHref);
                });       
            });
            paths.forEach(function(path) {
                path.getText().then(function(str) {
                    pathFields.push(str.split(' '));
                    
                });       
            });
        }).then(function() {
            log.log("1st SUP onclick URL is: " + pathUrls[0]);
            log.log("\n1st SUP fields: " + pathFields[0]);
        });
    });
    */
    
    it('should be able to edit a randomly-selected SUP', function() {
        log.info('should be able to edit a randomly-selected SUP');
        function getValue(elemId, results) {
            element(by.id(elemId)).getAttribute('value').then(function(val) { 
                results[elemId] = val; 
            });
        }
        element.all(by.repeater('path in paths')).then(function(paths) {
            var pathUrl = null;
            
            // pathSummary will contain the row entries of the randomly selected path. Example:
            //   'Blur_Version.19.0.494.obake_verizon.Verizon.en.US Blur_Version.19.0.500.obake_verizon.Verizon.en.US obake_verizon US Verizon RUNNING PM'
            var pathSummary = null;
            
            // pathMetaFields will contain key-value pairs from the Edit page. Example:
            //  {"targetVersion":"Blur_Version.19.0.500.obake_verizon.Verizon.en.US",
            //   "sourceVersion":"Blur_Version.19.0.494.obake_verizon.Verizon.en.US",
            //   "hwType":"obake_verizon","carrier":"Verizon","region":"US"}
            var pathMetaFields = {};
                
            var params = ['sourceVersion'];     // these are now optional: 'hwType', 'carrier', 'region'];
                                                //  @todo: add check for optional match criteria
            var idx = Math.floor(Math.random()*paths.length);
            paths[idx].then(function(path) {
                log.info("Randomly selected SUP index is " + idx);
                path.getAttribute('onclick').then(function(onclickHref) {
                    pathUrl = onclickHref.replace('document.location.href=', '');
                });
                path.getText().then(function(text) {
                    pathSummary = text;
                });
                path.click().then(function() {
                    /*for (var i=0; i < params.length; i++) {
                        var p = params[i];
                        log.log("i=" + i + ", p=" + p);
                        element(by.id(params[i])).getAttribute('value').then(function(x) {
                             pathMetaFields[params[i]] = x;
                             log.log('i=' + i + ' pathMetaFields[' + params[i] + '] = ' + x);
                        });
                    }*/
                    element(by.id('targetVersion')).getText().then(function(x) { pathMetaFields['targetVersion'] = x; });
                    params.forEach(function(p) { getValue(p, pathMetaFields); } );
                }).then(function() {
                    log.debug("pathMetaFields=" + JSON.stringify(pathMetaFields));
                    log.debug("pathSummaryFields=" + pathSummary);
                    summFields = pathSummary.split(' ');
                    expect(summFields[0]).toBe(pathMetaFields['sourceVersion']);
                    expect(summFields[1]).toBe(pathMetaFields['targetVersion']);
                    //expect(summFields[2]).toBe(pathMetaFields['hwType']);
                    //expect(summFields[3]).toBe(pathMetaFields['region']);
                    //expect(summFields[4]).toBe(pathMetaFields['carrier']);
                });
            });     
        });
    });

    it('should find a path using the Search box', function() {
        log.info('should find a path using the Search box');
        browser.get(SUP_URL + '/upgrades#/paths');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('/upgrades#/paths');
        });
        element(by.id('searchIcon')).sendKeys('Verizon');
        var paths = element.all(by.repeater('path in paths').column('path.upgradePath.sourceVersion'));        
        paths.then(function(arr) {
            if (paths.length > 0) {
                arr[0].getText().then(function(srcVersion) {
                    log.log("1st Filtered path is: " + srcVersion);
                    expect(srcVersion).toContain('Verizon');
                });
            }
        });
            
    });
    
    it('should upload a package', function() {
        log.info('should upload a package');
        uploadPackageA();
        deletePackage();
    });    

/*    
    it('should not upload duplicate source package', function() {    
        uploadPackageA();
        console.log("edit");
        element(by.xpath('//input[7]')).click(); 
        
        waits(10000);
        console.log("sourceupdate");
        element(by.id('sourceVersion')).clear();
        element(by.id('sourceVersion')).sendKeys('Blur_Version.910.0.0.XT907.Blurdev.en.US');
        waits(5000);
        console.log("modifying carrier");
        element(by.xpath('//td[3]/button')).clear();
        element(by.xpath('//td[3]/button')).sendKeys('Blurdev');	
        waits(10000);
        console.log("modifying hardware type");
        element(by.xpath('//td[3]/button')).clear();
        element(by.xpath('//td[3]/button')).sendKeys('XT907');
        waits(10000);
        console.log("modifying region");
        element(by.xpath('//td[3]/button')).clear();
        element(by.xpath('//td[3]/button')).sendKeys('US');
        waits(10000);
        element(by.id('mySaveBtn')).click();
        waits(5000);
        expect(element(by.xpath('//*[@id="wrap"]/div[2]/div/div/span')).getText()).toEqual('Save failed! Duplicate upgrade path found.');
  }); 

    it('should search source and target', function() {
        element(by.id('searchIcon')).sendKeys('Blur_Version.910.0.1.XT907.Blurdev.en.US');
        var paths = element.all(by.repeater('path in paths').column('path.upgradePath.sourceVersion'));        
        paths.then(function(arr) {
            arr[0].getText().then(function(srcVersion) {
                console.log("1st Filtered path is: " + srcVersion);
                expect(srcVersion).toContain('Blur_Version.910.0.0.XT907.Blurdev.en.US');
            });
        });
    });
    
    it('should edit,save,cancel,delete a package', function() { 
    uploadPackageC();
       
       // waits(10000);
        console.log("edit");
        element(by.id('myEditBtn')).click().then(function() {
        
        
       // waits(10000);
        console.log("region update");
            
    });
        element(by.xpath('//tr[5]/td[2]/input')).sendKeys('abc').then(function() {
        
        console.log("save");
            
    });
        element(by.id('mySaveBtn')).click().then(function() {
        console.log("cancel");
            
    });
        expect(element(by.xpath('//tr[5]/td[2]/input')).getAttribute('value')).toEqual('USabc');
        element(by.id('myEditBtn')).click();
        element(by.xpath('//tr[3]/td[2]/input')).sendKeys('Blurdevabc');
        element(by.id('myCancelBtn')).click().then(function() {
        //waits(10000);
         
        console.log("delete");
        });
        element(by.id('myDeleteBtn')).click();
        element(by.xpath('//button[2]')).click();
        
       // waits(5000);
    
     }); 
     
   it('should not upload a new package', function() {
   uploadPackageB();
   expect(element(by.xpath('/html/body/div/div[2]/div/div/span')).getText()).toEqual('This SUP already exists.');   
    });
    
   it('should parse and upload', function() {
      browser.get(SUP_URL + '/upgrades#/paths');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('/upgrades#/paths');
        });
        element(by.id('uploadImportPkg')).click();
        element(by.id('copyJenkinsArtifactory')).click();
        element(by.id('myFileURL')).sendKeys('http://8.35.197.229:8080/userContent/allpackages/delta-ota-Blur_Version.14.0.470-14.0.588.falcon_umts.T-Mobile.en.US.zip');
        element(by.id('myUserName')).sendKeys('test2014');
        element(by.id('myPassword')).sendKeys('test2014');
        element(by.id('myParseCheckbox')).click();
        element(by.id('uploadBtn')).click(); 
        waits(60000);   
    });
    
   it('should upload a list', function() {
        browser.driver.manage().timeouts().setScriptTimeout(120000);
        browser.get(SUP_URL + '/upgrades#/lists');
        ptor.getCurrentUrl().then(function(url) {
    	expect(ptor.getCurrentUrl()).toContain('http://icws-ssota-qa.blurdev.com/upgrades#/lists');
    	});
    	element(by.xpath('//li[6]/a')).click();
    
	    element(by.id('myUploadListDrpdown')).click();
    	element(by.id('uploadFromComputer')).click();
    	console.log("uploading a list");
    	element(by.name('listNameField')).sendKeys('fgh');
    	element(by.id('chooseFiles')).sendKeys('/Users/nshukla/Documents/IMEI.rtf');
    	element(by.id('uploadButton')).click();
    	waits(10000);
    	//need to add assertion
    	removeList();
    }); 
    
   it('should be able to add new list target and check for upgrade ', function() {
        uploadPackageC(); 
        element(by.id('myEditBtn')).click();
        element(by.id('myLists')).click();
        element(by.id('myAddNewListsTarget')).click();
        element(by.xpath('//*[@id="wrap"]/div[3]/accordion/div/div[3]/div/div[2]/div/div/accordion/div/div[1]/div/div[1]/a')).click();
        element(by.xpath('//*[@id="wrap"]/div[3]/accordion/div/div[3]/div/div[2]/div/div/accordion/div/div/div/div[2]/div/form/div[2]/div/input')).sendKeys('fgh');
        element(by.id('myAdd')).click();
        element(by.id('mySaveBtn')).click();   
        element(by.id('myListMatch')).click();
        element(by.id('myImeiAndSerialno')).sendKeys('990002025532381');
        element(by.id('myCheckBtn')).click(); 
        //need to add assertion
        deletePackage();  
    });
    
    
it('should be able to add,remove criteria on upgrade path page', function() {
      browser.get(SUP_URL + '/upgrades#/paths');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('/upgrades#/paths');
    });
        element(by.id('uploadImportPkg')).click();
        element(by.id('uploadFromComputer')).click();
        element(by.xpath('//div[2]/div/input')).sendKeys('/Users/nshukla/Downloads/delta-ota-Blur_Version.98.6.0-98.6.1.XT907.Blurdev.en.US.zip');
        element(by.xpath('//td[3]/input')).sendKeys('Blur_Version.98.6.0.XT907.Blurdev.en.US');
        element(by.xpath('//tr[2]/td[3]/input')).sendKeys('Blur_Version.98.6.1.XT907.Blurdev.en.US'); 
        //remove criteria region 
        console.log("remove region");    
        element(by.xpath('//div[4]/form/table/tbody/tr[7]/td[4]/button')).click();
        element(by.id('myCriteriaList')).click();
        //console.log();
        //expect(element(by.css('select option[value="3"]'))).Equalto('androidCarrier');
        
        //element(by.xpath('//*[@id="myCriteriaList"]/option[4]/text()')).click();
        
        waits(20000);
        
        //element(by.id('myCriteriaList')).click();
        console.log("adding criteria");
        element(by.css('select option[value="3"]')).click();
        
        waits(30000);
        
        element(by.id('myAddCriteria')).click();
        //android carrier
        element(by.xpath('//div[4]/form/table/tbody/tr[7]/td[3]/input')).sendKeys('Verizon');
        //upload
       // expect(element(by.name('supeditor')).getAttribute('class')).toMatch('ng-binding');
        element(by.id('myUploadButton')).click(); 
        waits(120000);               
    }); 
  it('should retrieve upgrade logs for imei', function() {
      browser.get(SUP_URL + '/upgrades#/events');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('http://icws-ssota-qa.blurdev.com/upgrades#/events');
  });  
      element(by.id('inputSerialNumber')).sendKeys('990002009978154');
      element(by.id('inputSubmitButton')).click();  
      //need to add assertion   
  }); 
  
  it('should upload list as exclusive and not adding to master list ', function() {
      browser.get(SUP_URL + '/upgrades#/lists');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('http://icws-ssota-qa.blurdev.com/upgrades#/lists');
  });  
      element(by.id('myUploadListDrpdown')).click();
      element(by.id('uploadFromComputer')).click();  
      element(by.xpath('//div[2]/input')).sendKeys('imeitest');
      element(by.id('myExclusiveBtn')).click();   
      element(by.id('chooseFiles')).sendKeys('/Users/nshukla/Documents/testimei.rtf'); 
      element(by.id('uploadButton')).click();
      //need to add assertion   
  }); 
  
  it('should upload list as type exclusive and adding to master black list ', function() {
        browser.get(SUP_URL + '/upgrades#/lists');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('http://icws-ssota-qa.blurdev.com/upgrades#/lists');
        });  
        element(by.id('myUploadListDrpdown')).click();
        element(by.id('uploadFromComputer')).click();  
        element(by.xpath('//div[2]/input')).sendKeys('imeitest');
        element(by.id('myExclusiveBtn')).click();   
        element(by.id('myAddToMasterCheckBox')).click();
        //Change the choose File
        element(by.id('chooseFiles')).sendKeys('/Users/nshukla/Documents/testimei.rtf'); 
        element(by.id('uploadButton')).click();
        expect(element(by.id('myRemoveDeviceListFromMaster')).getText()).toEqual('Remove list from Master Blacklist');    
    }); 
   
    it('should remove list from masterlist ', function() {
      browser.driver.manage().timeouts().setScriptTimeout(120000);
      browser.get(SUP_URL + '/upgrades#/lists');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('http://icws-ssota-qa.blurdev.com/upgrades#/lists');
  
     });  
      element(by.id('searchIcon')).sendKeys('testimei');
      element(by.id('myActionDrpdown')).click();
      element(by.id('myRemoveList')).click();   
      expect(element(by.id('myAddDeviceListToMaster')).getText()).toEqual('Add list to Master Blacklist');  
 
    }); 
    
    it('should upload list as type inclusive', function() {
        browser.driver.manage().timeouts().setScriptTimeout(140000);
        browser.get(SUP_URL + '/upgrades#/lists');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('http://icws-ssota-qa.blurdev.com/upgrades#/lists');
        });  
        element(by.id('myUploadListDrpdown')).click();
        element(by.id('uploadFromComputer')).click();  
        element(by.xpath('//div[2]/input')).sendKeys('imeitest');
        element(by.id('myInclusiveBtn')).click();  
        //Change the choose File
        element(by.id('chooseFiles')).sendKeys('/Users/nshukla/Documents/testimei.rtf'); 
        element(by.id('uploadButton')).click();
        //need to add assertion   
    });
     
    it('should replace old list with new list ', function() {
      browser.get(SUP_URL + '/upgrades#/lists');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('/upgrades#/lists');
        });
        element(by.id('myUploadListDrpdown')).click();
        element(by.id('uploadFromComputer')).click();
        element(by.xpath('//div[2]/input')).sendKeys('imei0318-1');
        element(by.id('chooseFiles')).sendKeys('/Users/nshukla/Documents/IMEI.rtf');
        element(by.id('uploadButton')).click();
        element(by.id('searchIcon')).sendKeys('imei0318-1');
        element(by.id('myActionDrpdown')).click();
        element(by.id('myReplaceListEntries')).click();
        element(by.xpath('//tbody[2]/tr[2]/td/div/div/input')).sendKeys('/Users/nshukla/Documents/IMEI2.rtf');
        element(by.xpath('//td/div/div/button')).click();
        element(by.id('myActionDrpdown')).click();
        element(by.xpath('//td[5]/div/ul/li/a'c)).click();
        waits(5000);
        expect(element(by.xpath('/html/body/pre')).getText()).toEqual('990002009978154 HELVETICA;} NOTEWORTHY-LIGHT;\F1\FSWISS\FCHARSET0 \ \CF0 \DEFTAB720 \F0\FS30 \F1\FS24 \MARGL1440\MARGR1440\VIEWW10800\VIEWH8400\VIEWKIND0 \PARD\PARDEFTAB720\SL300 \PARD\TX720\TX1440\TX2160\TX2880\TX3600\TX4320\TX5040\TX5760\TX6480\TX7200\TX7920\TX8640\PARDEFTAB720\PARDIRNATURAL {\COLORTBL;\RED255\GREEN255\BLUE255;} {\FONTTBL\F0\FNIL\FCHARSET0 {\RTF1\ANSI\ANSICPG1252\COCOARTF1187\COCOASUBRTF400 }');  
    });
    
    it('do replace list entries choose file and cancel ', function() {
      browser.get(SUP_URL + '/upgrades#/lists');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('/upgrades#/lists');
        });
        element(by.id('searchIcon')).sendKeys('imei0318-1');
        element(by.id('myActionDrpdown')).click();
        element(by.id('myReplaceListEntries')).click();
        element(by.xpath('//tbody[2]/tr[2]/td/div/div/input')).sendKeys('/Users/nshukla/Documents/IMEI.rtf');
        element(by.xpath('//tbody[2]/tr[2]/td/div/div/button[2]')).click();
        //need to add assertion
    });
    
    it('should check list id ', function() {
      browser.get(SUP_URL + '/upgrades#/lists');
        ptor.getCurrentUrl().then(function(url) { 
            expect(ptor.getCurrentUrl()).toContain('/upgrades#/lists');
        });
        element(by.id('searchIcon')).sendKeys('imei0318-1');
        element(by.id('myActionDrpdown')).click();
        element(by.id('myReplaceListEntries')).click();
        element(by.xpath('//td[5]/div/ul/li/a')).click();
        expect 
        element(by.xpath('//tbody[2]/tr[2]/td/div/div/input')).sendKeys('/Users/nshukla/Documents/IMEI.rtf');
        element(by.xpath('//tbody[2]/tr[2]/td/div/div/button[2]')).click();
        //need to add assertion
    });
    
     it('should be able to edit metadata values', function() {
        uploadPackageC(); 
        element(by.id('myEditBtn')).click();
        element(by.xpath('//div/a')).click();
        element(by.id('myUpgradeWkflowHeading')).click();
        element(by.xpath('//div[2]/div/table/tbody/tr/td[2]/input')).click();
        element(by.xpath('//table[2]/tbody/tr/td[2]/input')).click();
        element(by.xpath('//tr[2]/td[2]/input')).click();
        element(by.xpath('//table[2]/tbody/tr[3]/td[2]/input')).click();
        element(by.xpath('//table[2]/tbody/tr[3]/td[2]/input')).click();
        element(by.xpath('//table[2]/tbody/tr[4]/td[2]/input')).click();
        element(by.id('mySaveBtn')).click();
        expect(element(by.xpath('//span')).toContain('metadata has changed');
        deletePackage();  
    });
    
    it('should not be able to edit metadata values', function() {
        uploadPackageC(); 
        element(by.id('myEditBtn')).click();
        element(by.xpath('//div/a')).click();
        element(by.id('myUpgradeWkflowHeading')).click();
        element(by.css('select option[value="2"]')).click();
        expect(element(by.id('myWifiChkbx')).isEnabled()).toBe('false.');
        deletePackage();  
    });
    
    it('should not be able to edit metadata values', function() {
        uploadPackageC(); 
        element(by.id('myEditBtn')).click();
        element(by.xpath('//div/a')).click();
        element(by.id('myUpgradeWkflowHeading')).click();
        element(by.css('select option[value="0"]')).click();
        element(by.xpath('//table[2]/tbody/tr[4]/td[2]/input')).click();
        expect(element(by.i('myWifiChkbx')).isEnabled()).toBe('false.');
        deletePackage();  
    });
*/

 });   