'use strict';

/* http://docs.angularjs.org/guide/dev_guide.e2e-testing */

describe('Portal', function() {

  beforeEach(function() {
    browser().navigateTo('http://localhost:8080/');
  });


  it('should automatically redirect to /upgrades#/paths when location hash/fragment is empty', function() {
    expect(browser().location().url()).toBe("/upgrades#/paths");
  });


  describe('Lists', function() {

    beforeEach(function() {
      browser().navigateTo('upgrades#/lists');
    });


    it('should display device lists when we naviagte to /upgrades#/lists', function() {
      expect(element('[ng-view] h1:first').text()).
        toMatch(/Device Lists/);
    });

  });


  describe('view2', function() {

    beforeEach(function() {
      browser().navigateTo('#/view2');
    });


    it('should render view2 when user navigates to /view2', function() {
      expect(element('[ng-view] p:first').text()).
        toMatch(/partial for view 2/);
    });

  });
});
