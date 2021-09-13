/**
 * This file consists of code that overrides/replaces code in the angular
 * testing library. It is mostly a copy of the angular code with some changes.
 *
 * IMPORTANT: If the angular testing library is upgraded, then this file
 * might need updates to refelct changes in the angular code.
 */


function int(str) {
  return parseInt(str, 10);
}

var msie = int((/msie (\d+)/.exec(angular.lowercase(navigator.userAgent)) || [])[1]);

/**
 * Usage:
 *    input(name).enter(value) enters value in input with specified name
 *    input(name).check() checks checkbox
 *    input(name).select(value) selects the radio button with specified name/value
 *    input(name).val() returns the value of the input.
 */
angular.scenario.dsl('input', function() {
  var chain = {};
  var supportInputEvent =  'oninput' in document.createElement('div') && msie != 9;
  var candidateElems = function( root, name, val ) {
      var selector = '';
      if( name ) {
        selector = '[ng\\:model="$1"]';
      }
      else {
        selector = '[ng\\:model]';
      }
      if( !isNil(val) ) {
        selector += '[value="$2"]';
      }
      return root.elements( selector, name, val );
  }

  chain.enter = function(value, event) {
    return this.addFutureAction("input '" + this.name + "' enter '" + value + "'", function($window, $document, done) {
      var input = candidateElems($document, this.name).filter(':input');
      input.val(value);
      input.trigger(event || (supportInputEvent ? 'input' : 'change'));
      done();
    });
  };

  chain.check = function() {
    return this.addFutureAction("checkbox '" + this.name + "' toggle", function($window, $document, done) {
      var input = candidateElems($document, this.name).filter(':checkbox');
      input.trigger('click');
      done();
    });
  };

  chain.select = function(value) {
    return this.addFutureAction("radio button '" + this.name + "' toggle '" + value + "'", function($window, $document, done) {
      var input = candidateElems($document, this.name, value).filter(':radio');
      input.trigger('click');
      done();
    });
  };

  chain.val = function() {
    return this.addFutureAction("return input val", function($window, $document, done) {
      var input = candidateElems($document, this.name).filter(':input');
      done(null,input.val());
    });
  };

  return function(name) {
    this.name = name;
    return chain;
  };
});


/**
 * Usage:
 *    select(name).option('value') select one option
 *    select(name).options('value1', 'value2', ...) select options from a multi select
 */
angular.scenario.dsl('select', function() {
  var chain = {};
  var candidateElems = function( root, name, multi ) {
      var selector = 'select';
      if( multi ) {
        selector += '[multiple]';
      }
      if( name ) {
        selector = '[ng\\:model="$1"]';
      }
      else {
        selector = '[ng\\:model]';
      }
      return root.elements( selector, name );
  }

  chain.option = function(value) {
    return this.addFutureAction("select '" + this.name + "' option '" + value + "'", function($window, $document, done) {
      var select = candidateElems($document, this.name);
      var option = select.find('option[value="' + value + '"]');
      if (option.length) {
        select.val(value);
      } else {
        option = select.find('option:contains("' + value + '")');
        if (option.length) {
          select.val(option.val());
        }
      }
      select.trigger('change');
      done();
    });
  };

  chain.options = function() {
    var values = arguments;
    return this.addFutureAction("select '" + this.name + "' options '" + values + "'", function($window, $document, done) {
      var select = candidateElems($document, this.name, true);
      select.val(values);
      select.trigger('change');
      done();
    });
  };

//  chain.val = function() {
//    return this.addFutureAction("return select val", function($window, $document, done) {
//      var select = candidateElems($document, this.name);
//      done(null,select.val());
//    });
//  };

  return function(name) {
    this.name = name;
    return chain;
  };
});


