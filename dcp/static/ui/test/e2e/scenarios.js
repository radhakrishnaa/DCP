'use strict';

/* http://docs.angularjs.org/guide/dev_guide.e2e-testing */

describe('config portal', function() {
  var SKIPCLEAN = false;


  beforeEach(function() {
    browser().navigateTo('../../index.html');
  });

  it('should automatically redirect to / when location hash/fragment is empty', function() {
    expect(browser().location().url()).toBe("/");
  });


  describe('home', function() {

    beforeEach(function() {
      browser().navigateTo('#/');
    });


    it('should render home when user navigates to /', function() {
      expect(element('[ng-view] h1:visible:first').text()).
        toContain('Device Configuration Portal');
    });

    it('should have links with the first one pointing to devicetype configs', function() {
      expect(element('[ng-view] li a:visible:first').attr('href')).
        toEqual('#/cfg_devicetype/list');
    });

  });

  describe('fulltest', function() {

    beforeEach(function() {
      browser().navigateTo('#/');
    });


    it('should complete the full range of admin and config activites', function() {
      var helper = new Helper(this);

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Create a Setting Category.' );

      helper.gotoListPage('setting_category');

      helper.forNew().click();

      helper.forTextField( 'name' ).enter( 'E2E Test Category' );
      helper.forTextField( 'comment' ).enter( 'A temporary category created as part of automated end-to-end testing.' );
      helper.forApply().click();
      helper.forErrorMsg().assertAbsent();

      helper.assertListPage();

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Create a Setting Definition.' );

      helper.gotoListPage('setting_def');

      helper.forNew().click();

      helper.forTextField( 'name' ).enter( 'test.e2e.setting01' );
      helper.forSelectField( 'category_id' ).option( 'E2E Test Category' );
      helper.forTextField( 'datatype' ).enter( 'string' );
      helper.forTextField( 'display_name' ).enter( 'Test Setting 01' );
      helper.forTextField( 'short_help' ).enter( 'Temporary setting 1, created as part of automated end-to-end testing.' );
      helper.forApply().click();
      helper.forErrorMsg().assertAbsent();

      helper.assertListPage();

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Create another Setting Definition.' );

      helper.gotoListPage('setting_def');

      helper.forNew().click();

      helper.forTextField( 'name' ).enter( 'test.e2e.setting02' );
      helper.forSelectField( 'category_id' ).option( 'E2E Test Category' );
      helper.forTextField( 'datatype' ).enter( 'string' );
      helper.forTextField( 'display_name' ).enter( 'Test Setting 02' );
      helper.forTextField( 'short_help' ).enter( 'Temporary setting 2, created as part of automated end-to-end testing.' );
      helper.forApply().click();
      helper.forErrorMsg().assertAbsent();

      helper.assertListPage();

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Create another Setting Definition (a boolean).' );

      helper.gotoListPage('setting_def');

      helper.forNew().click();

      helper.forTextField( 'name' ).enter( 'test.e2e.setting03' );
      helper.forSelectField( 'category_id' ).option( 'E2E Test Category' );
      helper.forTextField( 'datatype' ).enter( 'bool' );
      helper.forTextField( 'display_name' ).enter( 'Test Setting 03' );
      helper.forTextField( 'short_help' ).enter( 'Temporary setting 3 (a boolean), created as part of automated end-to-end testing.' );
      helper.forApply().click();
      helper.forErrorMsg().assertAbsent();

      helper.assertListPage();

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Create a HW Type.' );

      helper.gotoListPage('hwtype');

      helper.forNew().click();

      helper.forTextField( 'code' ).enter( 'e2e_TEST' );
      helper.forTextField( 'internal_name' ).enter( 'pseudophone' );
      helper.forTextField( 'internal_name' ).enter( 'FakeFone' );
      helper.forApply().click();
      helper.forErrorMsg().assertAbsent();

      helper.assertListPage();

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Create a Carrier.' );

      helper.gotoListPage('carrier');

      helper.forNew().click();

      helper.forTextField( 'code' ).enter( 'CarrierE2E' );
      helper.forTextField( 'name' ).enter( 'E2E Test Carrier' );
      helper.forApply().click();
      helper.forErrorMsg().assertAbsent();

      helper.assertListPage();

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Create a Region.' );

      helper.gotoListPage('region');

      helper.forNew().click();

      helper.forTextField( 'code' ).enter( 'TE' );
      helper.forTextField( 'name' ).enter( 'Test Region' );
      helper.forApply().click();
      helper.forErrorMsg().assertAbsent();

      helper.assertListPage();

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Create a Global Config Set.' );

      helper.gotoListPage('cfg_global');

      helper.forNew().click();

      helper.forSelectField( 'category_id' ).option( 'E2E Test Category' );
      helper.forTextField( 'comment' ).enter( 'A temporary global config created as part of automated end-to-end testing.' );
      helper.forApply().click();
      helper.forErrorMsg().assertAbsent();

      helper.assertDetailPage( 'Global Defaults (E2E Test Category)' );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Create a Carrier Config Set.' );

      helper.gotoListPage('cfg_carrier');

      helper.forNew().click();

      var carrierCfgName = 'CarrierE2E.TE';

      helper.forSelectField( 'category_id' ).option( 'E2E Test Category' );
      helper.forSelectField( 'fallback_id' ).option( 'Global Defaults' );
      helper.forSelectField( 'carrier' ).option( 'CarrierE2E' );
      helper.forSelectField( 'region' ).option( 'TE' );
      helper.forTextField( 'comment' ).enter( 'A temporary carrier config created as part of automated end-to-end testing.' );
      helper.forApply().click();
      helper.forErrorMsg().assertAbsent();

      helper.assertDetailPage( 'CarrierE2E.TE (E2E Test Category)' );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Create a DeviceType Config Set.' );

      helper.gotoListPage('cfg_devicetype');

      helper.forNew().click();

      var devicetypeCfgName = 'e2e_TEST.CarrierE2E.TE';

      helper.forSelectField( 'category_id' ).option( 'E2E Test Category' );
      helper.forSelectField( 'fallback_id' ).option( 'CarrierE2E.TE' );
      helper.forSelectField( 'hwtype' ).option( 'e2e_TEST' );
      helper.forTextField( 'comment' ).enter( 'A temporary devicetype config created as part of automated end-to-end testing.' );
      helper.forApply().click();
      helper.forErrorMsg().assertAbsent();

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Verify the initial versions are correct.' );

      helper.assertDetailPage( devicetypeCfgName+' (E2E Test Category)' );

      helper.forVersion( null, {tag:'uncommitted'} ).assertPresent();
      helper.forVersion( 1, {tag:'approved',onlySelected:true} ).assertPresent();

      helper.assertApproved( 1, VERSION_LATEST_COMMITTED );

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( '' );

      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_NOVALUE );

      helper.forVersion( null, {tag:'uncommitted'} ).click();
      helper.assertUncommitted( VERSION_UNCHANGED );

      helper.forVersion( 1 ).click();
      helper.assertApproved( 1, VERSION_LATEST_COMMITTED );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Make some changes to the devicetype settings.' );

      helper.forVersionEdit().click();

      helper.forOverrideCheckbox( 'test.e2e.setting01' ).expectVal().toEqual( false );

      helper.forTextField( 'test.e2e.setting01' ).enter( 'Devicetype value one' );
      helper.forTextField( 'test.e2e.setting02' ).enter( 'Test value two' );
      helper.forSelectField( 'test.e2e.setting03' ).option( 'on' );

      helper.forOverrideCheckbox( 'test.e2e.setting02' ).click();

      helper.forTextField( 'test.e2e.setting01' ).expectVal().toEqual( 'Devicetype value one' );
      helper.forTextField( 'test.e2e.setting02' ).expectVal().toEqual( '' );
      helper.forSelectField( 'test.e2e.setting03' ).expectVal().toEqual( 'on' );
      helper.forTextField( 'test.e2e.setting04' ).assertAbsent();

      helper.forOverrideCheckbox( 'test.e2e.setting01' ).expectVal().toEqual( true );
      helper.forOverrideCheckbox( 'test.e2e.setting02' ).expectVal().toEqual( false );
      helper.forOverrideCheckbox( 'test.e2e.setting03' ).expectVal().toEqual( true );

      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_SPECIFIC, devicetypeCfgName );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, devicetypeCfgName );

      helper.forApply().click();

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Verify that the devicetype setting changes show up correctly.' );

      helper.forVersion( null, {tag:'uncommitted edits',onlySelected:true} ).assertPresent();
      helper.forVersion( 2 ).assertAbsent();
      helper.forVersion( 1, {tag:'approved'} ).assertPresent();

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( 'Devicetype value one' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( 'on' );

      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_SPECIFIC, devicetypeCfgName );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, devicetypeCfgName );

      helper.assertUncommitted( VERSION_EDITED );

      helper.forVersion( 1, {tag:'approved'} ).click();
      helper.assertApproved( 1, VERSION_LATEST_COMMITTED );

      helper.forVersion( null, {tag:'uncommitted edits'} ).click();
      helper.assertUncommitted( VERSION_EDITED );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Commit the devicetype changes.' );

      helper.forVersionCommit().click();

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( 'Devicetype value one' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( 'on' );

      helper.forApply().click();

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Verify the committed changes.' );

      helper.forVersion( null, {tag:'uncommitted'} ).assertPresent();
      helper.forVersion( 2, {onlySelected:true} ).assertPresent();
      helper.forVersion( 1, {tag:'approved'} ).assertPresent();

      helper.assertCommitted( 2, VERSION_LATEST_COMMITTED );

      helper.forVersion( 1 ).click();

      helper.assertApproved( 1, VERSION_NOT_LATEST );

      helper.forVersion( null, {tag:'uncommitted'} ).click();

      helper.assertUncommitted( VERSION_UNCHANGED );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Go to the global config set and commit some changes.' );

      helper.gotoListPage('cfg_global');
      helper.forListItem( ['E2E Test Category'] ).click();

      helper.assertApproved( 1, VERSION_LATEST_COMMITTED );

      helper.forVersionEdit().click();

      helper.forTextField( 'test.e2e.setting02' ).enter( 'Global value two' );

      helper.forTextField( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forTextField( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSelectField( 'test.e2e.setting03' ).expectVal().toEqual( '' );

      helper.forOverrideCheckbox( 'test.e2e.setting01' ).expectVal().toEqual( false );
      helper.forOverrideCheckbox( 'test.e2e.setting02' ).expectVal().toEqual( true );
      helper.forOverrideCheckbox( 'test.e2e.setting03' ).expectVal().toEqual( false );

      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting02', null, '' );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_NOVALUE );

      helper.forApply().click();

      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting02', null, '' );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_NOVALUE );

      helper.forVersionCommit().click();

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( '' );

      helper.forApply().click();

      helper.forVersion( null, {tag:'uncommitted'} ).assertPresent();
      helper.forVersion( 2, {onlySelected:true} ).assertPresent();
      helper.forVersion( 1, {tag:'approved'} ).assertPresent();

      helper.assertCommitted( 2, VERSION_LATEST_COMMITTED );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Verify that unapproved global changes do not show up in the carrier config set.' );

      helper.gotoListPage('cfg_carrier');
      helper.forListItem( ['E2E Test Category', 'CarrierE2E', 'TE'] ).click();

      helper.forVersion( null, {tag:'uncommitted'} ).assertPresent();
      helper.forVersion( 1, {tag:'approved',onlySelected:true} ).assertPresent();

      helper.assertApproved( 1, VERSION_LATEST_COMMITTED );

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( '' );

      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_NOVALUE );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Approve the previously committed global config set version.' );

      helper.gotoListPage('cfg_global');
      helper.forListItem( ['E2E Test Category'] ).click();

      helper.forVersion( null, {tag:'uncommitted'} ).assertPresent();
      helper.forVersion( 2, {onlySelected:true} ).assertPresent();
      helper.forVersion( 1, {tag:'approved'} ).assertPresent();

      helper.forVersionApprove().click();

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( '' );

      helper.forApply().click();

      helper.forVersion( null, {tag:'uncommitted'} ).assertPresent();
      helper.forVersion( 2, {tag:'approved',onlySelected:true} ).assertPresent();
      helper.forVersion( 1, {tag:'approved'} ).assertPresent();

      helper.assertApproved( 2, VERSION_LATEST_COMMITTED );

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( '' );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Verify that approved global changes show up in the carrier config set.' );

      helper.gotoListPage('cfg_carrier');
      helper.forListItem( ['E2E Test Category', 'CarrierE2E', 'TE'] ).click();

      helper.forVersion( null, {tag:'uncommitted',onlySelected:true} ).assertPresent();
      helper.forVersion( 1, {tag:'approved'} ).assertPresent();

      helper.assertUncommitted( VERSION_PARENT_CHANGED );

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( '' );

      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_GLOBAL );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_NOVALUE );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Commit some changes to the carrier config set.' );

      helper.print( '==== Edit the settings' );
      helper.forVersionEdit().click();

      helper.print( '==== Select the value "off" for setting03' );
      helper.forSelectField( 'test.e2e.setting03' ).option( 'off' );

      helper.print( '==== Verify the setting values' );
      helper.forTextField( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forTextField( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSelectField( 'test.e2e.setting03' ).expectVal().toEqual( 'off' );

      helper.print( '==== Verify the override checkboxes' );
      helper.forOverrideCheckbox( 'test.e2e.setting01' ).expectVal().toEqual( false );
      helper.forOverrideCheckbox( 'test.e2e.setting02' ).expectVal().toEqual( false );
      helper.forOverrideCheckbox( 'test.e2e.setting03' ).expectVal().toEqual( true );

      helper.print( '==== Verify the setting source tags' );
      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_GLOBAL );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, carrierCfgName );

      helper.print( '==== Check the override checkbox for setting02' );
      helper.forOverrideCheckbox( 'test.e2e.setting02' ).click();

      helper.print( '==== Verify the setting values' );
      helper.forTextField( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forTextField( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSelectField( 'test.e2e.setting03' ).expectVal().toEqual( 'off' );

      helper.print( '==== Verify the override checkboxes' );
      helper.forOverrideCheckbox( 'test.e2e.setting01' ).expectVal().toEqual( false );
      helper.forOverrideCheckbox( 'test.e2e.setting02' ).expectVal().toEqual( true );
      helper.forOverrideCheckbox( 'test.e2e.setting03' ).expectVal().toEqual( true );

      helper.print( '==== Verify the setting source tags' );
      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_SPECIFIC, carrierCfgName );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, carrierCfgName );

      helper.print( '==== Enter a new value for setting02' );
      helper.forTextField( 'test.e2e.setting02' ).enter( 'Temporary carrier value two' );
      helper.forTextField( 'test.e2e.setting02' ).expectVal().toEqual( 'Temporary carrier value two' );
      helper.forOverrideCheckbox( 'test.e2e.setting02' ).expectVal().toEqual( true );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_SPECIFIC, carrierCfgName );

      helper.print( '==== Uncheck the override checkbox for setting02' );
      helper.forOverrideCheckbox( 'test.e2e.setting02' ).click();

      helper.print( '==== Verify the setting values' );
      helper.forTextField( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forTextField( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSelectField( 'test.e2e.setting03' ).expectVal().toEqual( 'off' );

      helper.print( '==== Verify the override checkboxes' );
      helper.forOverrideCheckbox( 'test.e2e.setting01' ).expectVal().toEqual( false );
      helper.forOverrideCheckbox( 'test.e2e.setting02' ).expectVal().toEqual( false );
      helper.forOverrideCheckbox( 'test.e2e.setting03' ).expectVal().toEqual( true );

      helper.print( '==== Verify the setting source tags' );
      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_GLOBAL );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, carrierCfgName );

      helper.print( '==== Apply the setting changes' );
      helper.forApply().click();

      helper.print( '==== Verify the setting source tags' );
      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_GLOBAL );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, carrierCfgName );

      helper.print( '==== Begin to commit the version' );
      helper.forVersionCommit().click();

      helper.print( '==== Verify the setting values' );
      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( 'off' );

      helper.print( '==== Verify the setting source tags' );
      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_GLOBAL );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, carrierCfgName );

      helper.print( '==== Confirm the commit' );
      helper.forApply().click();

      helper.print( '==== Verify the available versions' );
      helper.forVersion( null, {tag:'uncommitted'} ).assertPresent();
      helper.forVersion( 2, {onlySelected:true} ).assertPresent();
      helper.forVersion( 1, {tag:'approved'} ).assertPresent();

      helper.print( '==== Verify the selected version' );
      helper.assertCommitted( 2, VERSION_LATEST_COMMITTED );

      helper.print( '==== Verify the setting values' );
      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( 'off' );

      helper.print( '==== Verify the setting source tags' );
      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_GLOBAL );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, carrierCfgName );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Verify that unapproved carrier changes (including approved global changes) do not show up in the devicetype config set.' );

      helper.gotoListPage('cfg_devicetype');
      helper.forListItem( ['E2E Test Category', 'CarrierE2E.TE', 'e2e_TEST'] ).click();

      helper.forVersion( null, {tag:'uncommitted'} ).assertPresent();
      helper.forVersion( 2, {onlySelected:true} ).assertPresent();
      helper.forVersion( 1, {tag:'approved'} ).assertPresent();

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( 'Devicetype value one' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( 'on' );

      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_SPECIFIC, devicetypeCfgName );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, devicetypeCfgName );

      helper.assertCommitted( 2, VERSION_LATEST_COMMITTED );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Approve the previously committed carrier config set version.' );

      helper.gotoListPage('cfg_carrier');
      helper.forListItem( ['E2E Test Category', 'CarrierE2E', 'TE'] ).click();

      helper.forVersion( null, {tag:'uncommitted'} ).assertPresent();
      helper.forVersion( 2, {onlySelected:true} ).assertPresent();
      helper.forVersion( 1, {tag:'approved'} ).assertPresent();

      helper.forVersionApprove().click();

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( 'off' );

      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_GLOBAL );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, carrierCfgName );

      helper.forApply().click();

      helper.forVersion( null, {tag:'uncommitted'} ).assertPresent();
      helper.forVersion( 2, {tag:'approved',onlySelected:true} ).assertPresent();
      helper.forVersion( 1, {tag:'approved'} ).assertPresent();

      helper.assertApproved( 2, VERSION_LATEST_COMMITTED );

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( 'off' );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Verify that approved carrier changes (including global changes) show up in the devicetype config set.' );

      helper.gotoListPage('cfg_devicetype');
      helper.forListItem( ['E2E Test Category', 'CarrierE2E.TE', 'e2e_TEST'] ).click();

      helper.forVersion( null, {tag:'uncommitted',onlySelected:true} ).assertPresent();
      helper.forVersion( 2, {} ).assertPresent();
      helper.forVersion( 1, {tag:'approved'} ).assertPresent();

      helper.assertUncommitted( VERSION_PARENT_CHANGED );

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( 'Devicetype value one' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( 'on' );

      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_SPECIFIC, devicetypeCfgName );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_GLOBAL );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, devicetypeCfgName );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Edit the devicetype settings and check that override behaviors work.' );

      helper.print( '==== Edit the settings' );
      helper.forVersionEdit().click();

      helper.forTextField( 'test.e2e.setting01' ).expectVal().toEqual( 'Devicetype value one' );
      helper.forTextField( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSelectField( 'test.e2e.setting03' ).expectVal().toEqual( 'on' );

      helper.forOverrideCheckbox( 'test.e2e.setting01' ).expectVal().toEqual( true );
      helper.forOverrideCheckbox( 'test.e2e.setting02' ).expectVal().toEqual( false );
      helper.forOverrideCheckbox( 'test.e2e.setting03' ).expectVal().toEqual( true );

      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_SPECIFIC, devicetypeCfgName );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_GLOBAL );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, devicetypeCfgName );

      helper.print( '==== Uncheck the override checkbox for setting03' );
      helper.forOverrideCheckbox( 'test.e2e.setting03' ).click();
      helper.forOverrideCheckbox( 'test.e2e.setting03' ).expectVal().toEqual( false );
      helper.forSelectField( 'test.e2e.setting03' ).expectVal().toEqual( 'off' );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_INHERIT, carrierCfgName );

      helper.print( '==== Check the override checkbox for setting03' );
      helper.forOverrideCheckbox( 'test.e2e.setting03' ).click();
      helper.forOverrideCheckbox( 'test.e2e.setting03' ).expectVal().toEqual( true );
      helper.forSelectField( 'test.e2e.setting03' ).expectVal().toEqual( 'on' );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, devicetypeCfgName );

      helper.print( '==== Uncheck the override checkbox for setting03 again' );
      helper.forOverrideCheckbox( 'test.e2e.setting03' ).click();

      helper.print( '==== Uncheck the override checkbox for setting01' );
      helper.forOverrideCheckbox( 'test.e2e.setting01' ).click();
      helper.forOverrideCheckbox( 'test.e2e.setting01' ).expectVal().toEqual( false );
      helper.forTextField( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );

      helper.print( '==== Enter a new value for setting01' );
      helper.forTextField( 'test.e2e.setting01' ).enter( 'New devicetype value one' );
      helper.forOverrideCheckbox( 'test.e2e.setting01' ).expectVal().toEqual( true );
      helper.forTextField( 'test.e2e.setting01' ).expectVal().toEqual( 'New devicetype value one' );
      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_SPECIFIC, devicetypeCfgName );

      helper.print( '==== Uncheck the override checkbox for setting01' );
      helper.forOverrideCheckbox( 'test.e2e.setting01' ).click();
      helper.forOverrideCheckbox( 'test.e2e.setting01' ).expectVal().toEqual( false );
      helper.forTextField( 'test.e2e.setting01' ).expectVal().toEqual( '' );
      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_NOVALUE );

      helper.print( '==== Check the override checkbox for setting01' );
      helper.forOverrideCheckbox( 'test.e2e.setting01' ).click();
      helper.forOverrideCheckbox( 'test.e2e.setting01' ).expectVal().toEqual( true );
      helper.forTextField( 'test.e2e.setting01' ).expectVal().toEqual( 'New devicetype value one' );
      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_SPECIFIC, devicetypeCfgName );

      helper.print( '==== Enter an unchanged value for setting02' );
      helper.forTextField( 'test.e2e.setting02' ).enter( 'Global value two' );
      helper.forOverrideCheckbox( 'test.e2e.setting02' ).expectVal().toEqual( false );
      helper.forTextField( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_GLOBAL );

      helper.print( '==== Force an unchanged override for setting02' );
      helper.forOverrideCheckbox( 'test.e2e.setting02' ).click();
      helper.forOverrideCheckbox( 'test.e2e.setting02' ).expectVal().toEqual( true );
      helper.forTextField( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_SPECIFIC, devicetypeCfgName );

      helper.print( '==== Apply the setting changes' );
      helper.forApply().click();

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Verify the results of editing the devicetype settings.' );

      helper.forVersion( null, {tag:'uncommitted edits',onlySelected:true} ).assertPresent();
      helper.forVersion( 2, {} ).assertPresent();
      helper.forVersion( 1, {tag:'approved'} ).assertPresent();

      helper.assertUncommitted( VERSION_EDITED );

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( 'New devicetype value one' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( 'off' );

      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_SPECIFIC, devicetypeCfgName );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_SPECIFIC, devicetypeCfgName );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_INHERIT, carrierCfgName );

      // ==================================================================
      helper.print( '==================================================' );
      helper.print( 'Discard the devicetype edits and check that it reverts correctly.' );

      helper.setConfirmResult( true );
      helper.forVersionDiscard().click();
      helper.expectConfirm().toEqual( 'Discard uncommitted changes?' );

      helper.forVersion( null, {tag:'uncommitted',onlySelected:true} ).assertPresent();
      helper.forVersion( 2, {} ).assertPresent();
      helper.forVersion( 1, {tag:'approved'} ).assertPresent();

      helper.assertUncommitted( VERSION_PARENT_CHANGED );

      helper.forSettingDisplay( 'test.e2e.setting01' ).expectVal().toEqual( 'Devicetype value one' );
      helper.forSettingDisplay( 'test.e2e.setting02' ).expectVal().toEqual( 'Global value two' );
      helper.forSettingDisplay( 'test.e2e.setting03' ).expectVal().toEqual( 'on' );

      helper.assertSettingTag( 'test.e2e.setting01', VALTAG_SPECIFIC, devicetypeCfgName );
      helper.assertSettingTag( 'test.e2e.setting02', VALTAG_GLOBAL );
      helper.assertSettingTag( 'test.e2e.setting03', VALTAG_SPECIFIC, devicetypeCfgName );

    });

    afterEach(function() {
      var helper = new Helper(this);

      //
      // Clean-up
      //

      if(SKIPCLEAN) return;

      //pause();

      helper.deleteItem( 'setting_category', 'E2E Test Category', {expectConfirm:'Setting Category'} );
      helper.deleteItem( 'hwtype', 'e2e_TEST', {expectConfirm:'HW Type'} );
      helper.deleteItem( 'carrier', 'CarrierE2E', {expectConfirm:'Carrier'} );
      helper.deleteItem( 'region', 'TE', {expectConfirm:'Region'} );

    });

  });

});
