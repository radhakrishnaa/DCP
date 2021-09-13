var Q = require('q');
var DCP_URL = 'http://ws001-dcp-qa300.ilc.blurdev.com/ui#/'
var DCP_BATCH_UPDATE_URI = 'bulkupdate/search';
var WEBDRIVER_WAIT_TIMEOUT = 240000;

function info(msg){
    console.log('\nINFO: ' + msg);
}

//Beging Testing
describe('DCP Tests', function() {

    var category, hwtype, carrier, region, parentConfig;

    category = 'Admin';
    hwtype = 'hwtype_e2e_test';
    carrier = 'carrier_e2e_test';
    region = '00';
    parentConfigCarrier = 'Global Defaults (Admin)';
    parentConfigHWType = carrier + '.' + region + ' (' + category + ')';

    settingNameToTest = 'blur.service.sync.engine.polling.tolerance.upper';
    settingDefaultValue = '480000';
    settingValueToTestUpdate = '480010';

    existingValueSetting = '[10]';
    newValueSetting = '[11]';
    settingToBeUsedInBuldUpdate = 'blur.service.sync.ws.ssl';

    extraKeyCodeToTest = 'mcc-mnc-test';
    extraKeyNameToTest = 'Retail Test';
    extrakeyCommentToTest = 'Created By E2E Tests';
    extraKeyNameToTestUpdate = 'mcc-mcn-update';

    extraValueToTest = '72401';
    extraValueNameToTest = 'Retus Test';
    extraValueNameToTestUpdate = 'Retus Test Update';
    extraValueCommentToTest = 'Created By E2E Tests';

    settingRegExpToTestEnvironmentTransform = '^blur.service\.sync\.engine\.polling\.tolerance\.lower$';
    settingToTestEnvironmentTransform = 'blur.service.sync.engine.polling.tolerance.lower';
    settingRegExpExistingValueToTestEnvironmentTransform = '^480000$';
    settingValueToReplaceInTestEnvironmentTransform = '480005';

    categoryToBeUsedInInstantiateAllConfig = 'category-test';
    comment = 'Created By E2E Tests';

    var driver = browser.driver;

    var getXpathByOptionText = function(optionText) {
        return '//select/option[text()="' + optionText +'"]';
    };

    var printPageSource = function(){
        browser.getPageSource().then(function(page){info(page)});
    };

    var clickInOptionByText = function(optionText) {
        findByXpath(getXpathByOptionText(optionText)).click();
    }

    var printPageTitle = function(){
        browser.getTitle().then(function(title){info(title)});
    };

    var findById = function (id) {
        return browser.findElement(protractor.By.id(id));
    };

    var findByLinkText = function(text){
        return browser.findElement(protractor.By.linkText(text));
    };

    var findByPartialText = function(text){
        return browser.findElement(protractor.By.partialLinkText(text));
    };

    var findByXpath = function(text){
        return browser.findElement(protractor.By.xpath(text));
    };

    var findByModel = function(text){
        return browser.findElement(protractor.By.model(text));
    };

    var findByName = function(text){
        return browser.findElement(protractor.By.name(text));
    }

    var selectOptionsByOptionNames = function(optionsToBeSelected, comment){
        for (var i = 0; i < optionsToBeSelected.length; ++i){
            findByXpath(getXpathByOptionText(optionsToBeSelected[i])).click();
        }
        setComment(comment);
    };

    var setComment = function() {
        findByName('comment').sendKeys(comment);
    }

    var waitForPage = function(){
        driver.manage().timeouts().setScriptTimeout(WEBDRIVER_WAIT_TIMEOUT);
        driver.manage().timeouts().implicitlyWait(WEBDRIVER_WAIT_TIMEOUT);
    };

    var doAction = function(actionName){
        waitForPage();
        findByLinkText(actionName).click();
        expect(browser.getPageSource()).toContain(actionName);
        waitForPage();
        findByName('apply').click();//click confirm button
    };

    var doPropagate = function(){
        waitForPage();
        findByLinkText('Propagate').click();
        expect(browser.getPageSource()).toContain('Propagate:');
        waitForPage();

        /** Mark the checkbox Commit */
        findByXpath('/html/body/div[4]/div[2]/form/div[3]/div[2]/input').click();
        /** Mark the checkbox Approve */
        findByXpath('/html/body/div[4]/div[2]/form/div[3]/div[3]/input').click();
        /** Mark the checkbox qa300 */
        findByXpath('/html/body/div[4]/div[2]/form/div[3]/div[6]/input').click();
        findByName('apply').click();
    };

    var doEdit = function(settingId, updatedValue){
        waitForPage();
        element.all(by.linkText('Edit')).get(1).click();
        expect(browser.getPageSource()).toContain('Edit Settings for:');
        findById(settingId).clear();
        findById(settingId).sendKeys(updatedValue);
        findByName('apply').click();
    };

    var doDiscard = function(){
        findByLinkText('Discard').click();
        browser.switchTo().alert().accept();
    };

    var createConfigSetByOptionsAndComment = function(optionsToBeSelected, comment){
        waitForPage();
        // open the screen to create config set
        findByLinkText('New').click();

        for (var i = 0; i < optionsToBeSelected.length; ++i){
            findByXpath(getXpathByOptionText(optionsToBeSelected[i])).click();
        }
        findByName('comment').sendKeys(comment);
        findByName('apply').click();
        waitForPage();
    };

    var doDelete = function(){
        findByLinkText('Delete').click();
        browser.switchTo().alert().accept();
    };

    var publishForTest = function(cloudpath, hwTypePath, hwName){
        findByLinkText('Publish for Test').click();
        expect(browser.getPageSource()).toContain('Publish for Test:');
        findByXpath(cloudpath).click();//Choose cloud as QA300
        findByXpath(hwTypePath).sendKeys(hwName);//Choose a test BVS
        findByName('apply').click();//click "Publish for Test" button
    };

    var gotoBulkPage = function(){
        driver.get(DCP_URL + DCP_BATCH_UPDATE_URI);//http://wsdcp01.qa300.blurdev.com/ui#/bulkupdate/search
        waitForPage();
        expect(browser.getPageSource()).toContain('Search');
    };

    var searchItemInBulk = function(fieldXpath, fieldInput){
        findByXpath('/html/body/div[4]/div[2]/form/div/select/option[1]').click(); //admin settings
        findByXpath(fieldXpath).sendKeys(fieldInput);//region input
        findByName('filter').click();
        expect(browser.getPageSource()).toContain('blur.service.sync.ws.ssl');
    };

    var submitChangeInBulk = function(){
        findByXpath('/html/body/div[4]/div[3]/form/div[1]/table/tbody/tr[15]/td[3]/div/input').sendKeys('[10]');
        findByXpath('/html/body/div[4]/div[3]/form/div[1]/table/tbody/tr[15]/td[4]/div/input').sendKeys('[33]');
        findByXpath('/html/body/div[4]/div[3]/form/div[2]/div[2]/input').click(); //commit
        findByXpath('/html/body/div[4]/div[3]/form/div[2]/div[3]/input').click(); //approval
        findByXpath('/html/body/div[4]/div[3]/form/div[2]/div[7]/input').click();//publish to qa300
        findByName('apply').click(); //click update button
        expect(browser.getPageSource()).toContain('Updates Performed');
    };

    var addFilterByField = function(field, value) {
       findById(field).clear();
       findById(field).sendKeys(value);
    }

    var clickInFirstRowByTable = function(tableName) {
       element.all(by.repeater('item in items')).get(0).click();
    }

    var clickInRowFilterByField = function(fieldToFilter, value) {
        addFilterByField(fieldToFilter, value);
        waitForPage();
        assertFilterFoundOneOrMoreValues();
        clickInFirstRowByTable();
    }

    var setExistingValueBySettingName = function(value, settingName) {
        findById(settingName + '_existingValue').sendKeys(value);
    }

    var setNewValueBySettingName = function(value, settingName) {
        findById(settingName + '_newValue').sendKeys(value);
    }

    var assertFilterFoundOneOrMoreValues = function(){
      expect(element.all(by.repeater('item in items')).count()).toBeGreaterThan(0);
    }

    /**==================Pre-condition: SSO login=======================*/
    /** The login is necessary in the first time that run the tests,
     *  before the first login, the sessionid is handle in browser cookie
     */
    it('Pre-Setup: do sso login', function(){
        info('Pre-Setup: SSO login');
        var session = browser.manage().getCookie('sessionid');
        if (session === null || session === undefined) {
            ssoLogin();
        } else {
            driver.get(DCP_URL);
            browser.sleep(3000);
        }

        expect(driver.getTitle()).toContain('GDI Device Configuration Portal');
    });

    /** if it is the first time the tests run, it is necessary manual login */
    var ssoLogin = function(){
        driver.get(DCP_URL);
        browser.sleep(120000);
    };

    describe('Carrier Level Config',function(){
        it('Carrier Level Config - Create', function(){

            info('Case 1: Carrier Level Config - Create');

            findByPartialText('Carrier Level').click();
            expect(browser.getPageSource()).toContain('Carrier Config List');

            //This list representing the value in each one select that will be selected for saving new config set
            var optionsToBeSelected = [category, carrier, region, parentConfigCarrier];

            /** Create the new carrier config set, the list of the xpath will be for setting the group of the select values */
            createConfigSetByOptionsAndComment(optionsToBeSelected,'Created by E2E Tests');
            expect(browser.getPageSource()).toContain(carrier + '.' + region);
        });

        it('Carrier Level Config - Edit existing config setting', function(){
            info('Case 2: Carrier Level Config - Edit existing config setting');

            doEdit(settingNameToTest, settingValueToTestUpdate);
            var sslUpdated = findById(settingNameToTest).getText();

            /** Verify if the value was change */
            expect(sslUpdated).toBe(settingValueToTestUpdate);
        });

        it('Carrier Level Config - Discard Edit', function(){
            info('Case 3: Carrier Level Config - Discard Edit');

            doDiscard();

            var setting = findById(settingNameToTest).getText();

            /** Verify the value is the same before the edit*/
            expect(setting).toBe(settingDefaultValue);
        });

        it('Carrier Level Config - Commit a edit config', function(){

            info('Case 4: Carrier Level Config - Commit a edit config');

            /** Edit setting blur.service.sync.ws.ssl */
            doEdit(settingNameToTest, settingValueToTestUpdate);

            doAction('Commit');

            var settingValue = findById(settingNameToTest).getText();
            expect(settingValue).toBe(settingValueToTestUpdate);
        });

        it('Carrier Level Config - Approvel a config', function(){
            info('Case 5: Carrier Level Config - Approvel a config');
            doAction('Approve');
            expect(browser.getPageSource()).toContain('Config:');
        });

        it('Carrier Level Config - Propagate', function(){
            info('Case 6: Carrier Level Config - Propagate');
            doPropagate();
            expect(browser.getPageSource()).toContain('Updates Performed');
            browser.findElement(protractor.By.className('cancel')).click();
            expect(browser.getPageSource()).toContain('Config:');
        });
    });

    describe('Extra Key and Extra Value',function(){

        info('Extra Key and Extra Value Tests Cases');

        afterEach(function(){
            driver.get(DCP_URL);
        });

        it('Exta key - Create New Extra Key', function(){
            info('Case 1: Extra Key - Create Extra Key');
            driver.get(DCP_URL);

            /** Click in link to open the extra key list page */
            findByPartialText('Extra Key').click();

            /** Verify whether extra key list open */
            var title = findById('list-title');
            expect(title.getText()).toContain('Extra Key List');

            /** Click to create new extra key */
            findByPartialText('New').click();

            /** Put all values in form */
            findByName('code').sendKeys(extraKeyCodeToTest);
            findByName('name').sendKeys(extraKeyNameToTest);
            findByName('comment').sendKeys(extrakeyCommentToTest);

            /** Save */
            findByName('apply').click();
            waitForPage();

            /** Verify new extra key was listed */
            expect(browser.getPageSource()).toContain(extraKeyCodeToTest);
        });

        it('Extra Value - Create New Extra Value', function(){
            info('Case 2: Extra Value - Create Extra Value');

            /** Click in link to open the extra value list page */
            findByPartialText('Extra Value').click();

            /** Verify whether extra key list open */
            var title = findById('list-title');
            expect(title.getText()).toContain('Extra Value List');

            /** Click to create new extra key */
            findByPartialText('New').click();

            /** Put all values in form */
            clickInOptionByText(extraKeyCodeToTest);

            findByName('value').sendKeys(extraValueToTest);
            findByName('name').sendKeys(extraValueNameToTest);
            findByName('comment').sendKeys(extraValueNameToTestUpdate);

            /** Save */
            findByName('apply').click();
            waitForPage();

            /** Verify new extra key was listed */
            expect(browser.getPageSource()).toContain(extraValueToTest);
        });

        it('Extra key and Extra value - Appear in Config Set', function(){

            info('Case 3: Device Level Config - Check Extra Key and Extra value');

            findByPartialText('hwtype.carrier.region').click();

            expect(browser.getPageSource()).toContain('DeviceType Config List');

            findByLinkText('New').click();

            /** Get element option within select that will be extraKeyCodeTest */
            clickInOptionByText(extraKeyCodeToTest);

            /** Get element option within select that will be extraValueNameTest */
            var extra_value = findByXpath(getXpathByOptionText(extraValueNameToTest));

            expect(extra_value.getText()).toBe(extraValueNameToTest);
        });

        it('Extra Key - Update', function(){

            info('Case 4: Extra Key - Update Extra Key');

            /** Click in link to open the extra key list page */
            findByPartialText('Extra Key').click();

            /** Verify whether extra key list open */
            var title = findById('list-title');
            expect(title.getText()).toContain('Extra Key List');

            /** Filter the list and click in the row of the result */
            clickInRowFilterByField('code', extraKeyCodeToTest);

            /**Click in Edit */
            findByPartialText('Edit').click();

            /**Clear the field to be updated */
            findByName('name').clear();

            /** Update field name */
            findByName('name').sendKeys(extraKeyNameToTestUpdate);

            /** Save */
            findByName('apply').click();
            waitForPage();

            /** Verify new extra key was listed */
            expect(browser.getPageSource()).toContain(extraKeyNameToTestUpdate);
        });

        it('Extra Value - Update', function(){
            info('Case 5: Extra Value - Update Extra Value');

            /** Click in link to open the extra value list page */
            findByPartialText('Extra Value').click();

            /** Verify whether extra key list open */
            var title = findById('list-title');
            expect(title.getText()).toContain('Extra Value List');

            clickInRowFilterByField('value',extraValueToTest);

            /** Click to edit*/
            findByPartialText('Edit').click();

            /** Put all values in form */
            findByName('name').clear();
            findByName('name').sendKeys(extraValueNameToTestUpdate);

            /** Save */
            findByName('apply').click();
            waitForPage();

            /** Verify new extra key was listed */
            expect(browser.getPageSource()).toContain(extraValueNameToTestUpdate);
        });
    });

    describe('Device Config Set',function(){
        info('Device Config Set Tests Cases');

        //Go to home
        driver.get(DCP_URL);

        it('Device Level Config - Create a device config set without extra level',function(){

            info('Case 1: Create a device config set without extra level');

            findByPartialText('hwtype.carrier.region').click();

            expect(browser.getPageSource()).toContain('DeviceType Config List');

            //This list representing the value in each one select that will be selected for saving new config set
            var optionsToBeSelected = [category, hwtype, carrier, region, parentConfigHWType];

            // set values for each field and save the config set
            createConfigSetByOptionsAndComment(optionsToBeSelected, 'DCP E2E Tests - create new config set without extra level');

            expect(browser.getPageSource()).toContain('Config:');
        });

        it('Device Level Config - Create a device config set with extra level and with the same values that the exist config set without extra level', function(){
            //Go to home
            driver.get(DCP_URL);

            info('Case 2: Create a device config set with extra level');

            findByPartialText('hwtype.carrier.region').click();

            expect(browser.getPageSource()).toContain('DeviceType Config List');

            //This list representing the value in each one select that will be selected for saving new config set
            var optionsToBeSelected = [category, hwtype, carrier, region, parentConfigHWType, extraKeyCodeToTest, extraValueNameToTestUpdate];

            // set values for each field and save the config set
            createConfigSetByOptionsAndComment(optionsToBeSelected, 'dcp-test create new config set with extra level');

            expect(browser.getPageSource()).toContain('Config:');
        });

        it('Device Level Config - Publish device config set with extra level', function(){

            info('Case 3: Publish');

            doAction('Publish');

            expect(browser.getPageSource()).toContain('Config:');
        });

        it('Device Level Config - Edit device config set with extra level and Publish', function(){

            info('Case 4: Edit and Publish');

            // Change the setting in Device Config Set that was open
            doEdit(settingNameToTest,settingValueToTestUpdate);

            //Commit the version
            doAction('Commit');

            //Approve the version
            doAction('Approve');

            //Publish the version
            doAction('Publish');

            expect(browser.getPageSource()).toContain('Config:');
        });

        it('Device Level Config - Get Live Settings fot device config set that was published', function(){

            info('Case 5: Get Live Settings');

            findByLinkText('Live Settings').click();

            waitForPage();

            clickInOptionByText('qa300');

            waitForPage();

            var setting = findById(settingNameToTest);

            expect(setting.getText()).toContain(settingValueToTestUpdate);

            findByPartialText('OK').click();
        });

        it('Device Level Config - Propagate config', function(){
            info('Case 6: Device Level Config - Propagate config');
            doPropagate();
            expect(browser.getPageSource()).toContain('Updates Performed');
            browser.findElement(protractor.By.className('cancel')).click();
            expect(browser.getPageSource()).toContain('Config:');
        });
    });

    describe('Bulk Update', function(){

        beforeEach(function(){
            driver.get(DCP_URL);
            findByPartialText('Bulk Update').click();
            clickInOptionByText('Admin');
        });

        it('Case 1 - Filter by Extra Key', function() {

            info('Case 1 - Bulk Update Filter by Extra Key');

            /** Add value in filter */
            addFilterByField('extra_key', extraKeyCodeToTest);

            /** Click in search to execute the filter */
            findById("btn_search").click();

            expect(element.all(by.repeater('item in items')).count()).toBeGreaterThan(0);
        });

        it('Case 2 - Filter by Extra Value', function(){

            info('Case 2 - Bulk Update Filter by Extra Value');

            /** Add value in filter */
            addFilterByField('extra_value', extraValueToTest);

            /** Click in search to execute the filter */
            findById("btn_search").click();

            expect(element.all(by.repeater('item in items')).count()).toBeGreaterThan(0);
        });

        it('Case 3 - Filter by Extra Name', function(){

            info('Case 3 - Bulk Update Filter by Extra Name');

            /** Add value in filter */
            addFilterByField('extra_value_name', extraValueNameToTest);

            /** Click in search to execute the filter */
            findById("btn_search").click();

            expect(element.all(by.repeater('item in items')).count()).toBeGreaterThan(0);
        });

        it('Case 4 - Change the setting and Commit and Approve', function(){

            info('Case 4 - Bulk Update Change the setting and Commit and Approve');

            addFilterByField('extra_value', extraValueToTest);

            findById("btn_search").click();

            setExistingValueBySettingName(existingValueSetting,settingToBeUsedInBuldUpdate);
            setNewValueBySettingName(newValueSetting,settingToBeUsedInBuldUpdate);

            /** Mark the checkbox with the actions */
            findByModel('commit_enabled').click();
            findByModel('approve_enabled').click();
            findByName('apply').click();

            /** Verify results table */
            expect(findById('result_edited').getText()).toBe('X');
            expect(findById('result_commit').getText()).toBe('X');
            expect(findById('result_approve').getText()).toBe('X');
        });
    });

    describe('Environment Transform', function(){
        var order = '1000';
        var environmentRegExp = '^(qa).*';

        beforeEach(function(){
            driver.get(DCP_URL);

            /** Click in Environment menu */
            findByPartialText('Environment Transform').click();
        });

        it('Environment Transform - Create', function(){

            /** Click in New */
            findByPartialText('New').click();

            /** Fill the fields */
            /** This transformation will affect the Config set create in before test
             * because of that this test depends on the orther tests
             */
            findByName('order').sendKeys(order);

            findByName('env_pat').clear();
            findByName('env_pat').sendKeys(environmentRegExp);

            /** Create the regexp to match the config set with extra level */
            findByName('extra_level_pat').sendKeys('^' + extraKeyCodeToTest +  '\.' + extraValueNameToTestUpdate +  '$');

            findByName('setting_name_pat').sendKeys(settingRegExpToTestEnvironmentTransform);
            findByName('value_pat').sendKeys(settingRegExpExistingValueToTestEnvironmentTransform);
            findByName('value_sub').sendKeys(settingValueToReplaceInTestEnvironmentTransform);
            findByName('comment').sendKeys('Create by E2E Tests');

            findByName('apply').click();

            expect(findById('list-title').getText()).toContain('Environment Transform List');
        });

        it('Environment Transform - Filter by Extra Level Pat', function(){

            /** Add value in filter, this extra level field is of the combination between extra key code . extra value name
              * because of this we can to pass only the extra key name
              */
            addFilterByField('extra_level_pat', extraKeyCodeToTest);

            /** Click in search to execute the filter */
            findByName('filter').click();

            expect(element.all(by.repeater('item in items')).count()).toBeGreaterThan(0);
        });

        it('Environment Transform - Change the setting based on new transformation created', function(){
            /** back to home */
            driver.get(DCP_URL);

            findByPartialText('hwtype.carrier.region').click();

            clickInRowFilterByField('extra_value_id', extraKeyNameToTestUpdate);

            findByLinkText('Live Settings').click();

            waitForPage();

            clickInOptionByText('qa300');

            waitForPage();

            var setting = findById(settingToTestEnvironmentTransform);

            expect(setting.getText()).toBe(settingValueToReplaceInTestEnvironmentTransform);
        });
    });

    describe('Instantiate All Configs for a Devicetype', function(){

        beforeEach(function(){
          driver.get(DCP_URL);
        });

        it('Create the new category',function(){
          info('Case 1: Instantiate All Configs - Create Category');
          findByPartialText('Setting Category').click();
          findByPartialText('New').click();
          findByName('name').sendKeys(categoryToBeUsedInInstantiateAllConfig);
          findByName('comment').sendKeys(comment);
          findByName('apply').click();

          /** If the page back to list, the operation was with success */
          var title = findById('list-title');
          expect(title.getText()).toContain('Setting Category List');
        });

        it('Create Device config set for new category', function(){

          info('Case 2: Instantiate All Configs - Create Device config set for new category');

          findByPartialText('Instantiate All Configs for a Devicetype').click();

          //This list representing the value in each one select that will be selected for saving new config set
          var optionsToBeSelected = [hwtype, carrier, region, extraKeyCodeToTest, extraValueNameToTestUpdate];

          // Set values for each field
          selectOptionsByOptionNames(optionsToBeSelected, comment);

          findById(categoryToBeUsedInInstantiateAllConfig).click()

          findByName('apply').click();

          findByPartialText('Global Defaults').click();
          addFilterByField('category_id', categoryToBeUsedInInstantiateAllConfig);
          findByName('filter').click();
          assertFilterFoundOneOrMoreValues();

          driver.get(DCP_URL);

          findByPartialText('Carrier Level  (carrier.region)').click();
          addFilterByField('category_id', categoryToBeUsedInInstantiateAllConfig);
          findByName('filter').click();
          assertFilterFoundOneOrMoreValues();

          driver.get(DCP_URL);

          findByPartialText('DeviceType Level  (hwtype.carrier.region)').click();
          addFilterByField('category_id', categoryToBeUsedInInstantiateAllConfig);
          findByName('filter').click();
          assertFilterFoundOneOrMoreValues();
        });

        it('Setting Category - Delete', function(){
          info('Case 3: Instantiate All Configs - Delete Category');
          findByPartialText('Setting Category').click();
          clickInRowFilterByField('name',categoryToBeUsedInInstantiateAllConfig);
          doDelete();
          expect(browser.getPageSource()).not.toContain(categoryToBeUsedInInstantiateAllConfig);
        });
    });

    describe('Delete all objects created', function(){
        beforeEach(function(){
            driver.get(DCP_URL);
        });

        it('Carrier Level Config - Delete', function(){

            info('Case 7: Carrier Level Config - Delete');

            findByPartialText('Carrier Level').click();
            expect(browser.getPageSource()).toContain('Carrier Config List');

            clickInRowFilterByField('carrier', '02SL');

            doDelete();

            expect(browser.getPageSource()).toContain('Carrier Config List');
        });

        it('Device Level Config - Delete config', function(){

            info('Case 7: Device Level Config - Delete config');

            findByPartialText('hwtype.carrier.region').click();
            expect(browser.getPageSource()).toContain('DeviceType Config List');

            clickInRowFilterByField('hwtype','00bulk');

            doDelete();

            expect(browser.getPageSource()).toContain('DeviceType Config List');
        });

        it('Extra Value - Delete', function(){

            info('Case 6: Extra Value - Delete Extra Value');

            /** Click in link to open the extra value list page */
            findByPartialText('Extra Value').click();

            /** Verify whether extra key list open */
            var title = findById('list-title');
            expect(title.getText()).toContain('Extra Value List');

            clickInRowFilterByField('value',extraValueToTest);

            /** Click to edit*/
            doDelete();

            waitForPage();

            /** Verify new extra key was listed */
            expect(browser.getPageSource()).not.toContain(extraValueNameToTestUpdate);
        });

        it('Extra Key - Delete', function(){

            info('Case 7: Extra Key - Delete Extra Key');

            /** Click in link to open the extra key list page */
            findByPartialText('Extra Key').click();

            /** Verify whether extra key list open */
            var title = findById('list-title');
            expect(title.getText()).toContain('Extra Key List');

            /** Click in the last element in table */
            clickInRowFilterByField('code',extraKeyCodeToTest);

            /** Click in button delete and accept the dialog */
            doDelete();

            waitForPage();

            /** Verify new extra key was listed */
            expect(browser.getPageSource()).not.toContain(extraKeyNameToTestUpdate);
        });
    });
});
