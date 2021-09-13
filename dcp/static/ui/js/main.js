angular.module('cfgPortal', ['restApi']).
  config(function($routeProvider) {
    $routeProvider.
      when('/', {controller:HomeCtrl, templateUrl:'static/ui/views/home.html'}).
      when('/livequery', {controller:LiveQueryCtrl, templateUrl:'static/ui/views/livequery.html'}).
      when('/cfgreport', {controller:CfgReportCtrl, templateUrl:'static/ui/views/cfgreport.html'}).
      when('/cfgimport', {controller:CfgImportCtrl, templateUrl:'static/ui/views/cfgimport.html'}).
      when('/cfg_superset/new', {controller:CfgSupersetCtrl, templateUrl:'static/ui/views/item.html'}).
      when('/cfg_superset/:junk', {redirectTo:'/cfg_superset/new'}).
      when('/cfg_:cfgtable/view/:id', {controller:CfgSetCtrl, templateUrl:'static/ui/views/item.html'}).
      when('/cfg_:cfgtable/settings/:id', {controller:SettingEditCtrl, templateUrl:'static/ui/views/settings_edit.html'}).
      when('/cfg_:cfgtable/commit/:id', {controller:CommitCtrl, templateUrl:'static/ui/views/settings_review.html'}).
      when('/cfg_:cfgtable/approve/:id', {controller:ApproveCtrl, templateUrl:'static/ui/views/settings_review.html'}).
      when('/cfg_:cfgtable/publish/:id', {controller:PublishCtrl, templateUrl:'static/ui/views/settings_review.html'}).
      when('/cfg_:cfgtable/revert/:id', {controller:RevertCtrl, templateUrl:'static/ui/views/settings_review.html'}).
      when('/cfg_:cfgtable/testpublish/:id', {controller:TestPublishCtrl, templateUrl:'static/ui/views/settings_review.html'}).
      when('/cfg_:cfgtable/propagate/:id', {controller:PropagateCtrl, templateUrl:'static/ui/views/settings_review.html'}).
      when('/:table/list', {controller:ListCtrl, templateUrl:'static/ui/views/list.html'}).
      when('/:table/new', {controller:NewCtrl, templateUrl:'static/ui/views/item.html'}).
      when('/:table/new/:id', {controller:NewCtrl, templateUrl:'static/ui/views/item.html'}).
      when('/:table/view/:id', {controller:ItemCtrl, templateUrl:'static/ui/views/item.html'}).
      when('/:table/edit/:id', {controller:EditCtrl, templateUrl:'static/ui/views/item.html'}).
      when('/bulkupdate/search', {controller:BulkUpdateCtrl, templateUrl:'static/ui/views/bulkupdate.html'}).
      when('/bulkupdate/settings', {controller:BulkUpdateCtrl, templateUrl:'static/ui/views/bulkupdate.html'}).
      otherwise({redirectTo:'/'});
  });

apiUrl = '../../api';

fakeWait = 5000;

modeEnum = {
  'view': 0,
  'edit': 1,
  'new': 2
};

animToggle = false;

var filterApplied = false;
// tmpItem is used to pass local data to the next page for an item that
// will be displayed there. This allows partial page rendering prior to
// completing the server call to get the most up-to-date data.
function setTmpItem( item ) {
  window.tmpItem = item;
}

//
function setSubmitted( elem, flag ) {
  angular.element(elem).scope().$apply( function($scope){
    $scope.setSubmitted(true);
  } );
}

function setTitle( text ) {
  document.getElementsByTagName('title')[0].innerHTML = 'DCP: ' + text;
}

/**
 * Used to query the table when the result of query is only a single value.
 * @param model a BasicTable object.
 * @param params
 * @param success success callback
 * @param error error callback
 */
function queryOne( model, params, success, error ) {
  if( params.id ) {
    model.get( params, success, function(){error(0)} );
  }
  else {
    model.query( params, function(items){
      if( items.length == 1 ) {
        success(items[0]);
      }
      else {
        error(items.length);
      }
    }, function(){error(0);} );
  }
}

//Determine config table based on the item.
function getCfgTable(item) {
  if( item.hwtype ) {
    return 'cfg_devicetype';
  } else if( item.carrier ) {
    return 'cfg_carrier';
  } else if( item.delta ) {
    return 'cfg_delta';
  } else {
    return 'cfg_global';
  }
}

////////////////////////////////////////////////////////////
//
function RootCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  var self = this;
  setTitle( 'GDI Device Configuration Portal' );
  this.numPending = 0;
  $rootScope.shortError = '';
  $rootScope.currUser = $rootScope.currUser || {};

  /**
   * Determine the current logged in user.
   */
  BasicTable.read({ '_table': 'currentuser' },
    function(item) { $rootScope.currUser = item; },
    function() { $rootScope.currUser = {}; }
  );

  $scope.choose = choose;

  $rootScope.reload = function() {
    location.reload();
  };

  //Forcing the browser to start the anmation always at the start
  $scope.setState = function( newState ) {
    $scope.animToggle = animToggle = !animToggle;
    return $scope.state = newState;
  };

  $scope.waiting = function() {
    return $scope.state != 'ready' && !$rootScope.shortError;
  };

  $scope.refreshStatus = function() {
    var elem = document.getElementById( 'working' );
    elem.className = elem.className.replace( / hide$/, '' );
    if( self.numPending <= 0 || $rootScope.shortError ) {
      elem.className = elem.className + ' hide';
    }
  };

  $scope.setShortError = function( message ) {
    $rootScope.shortError = message;
    $scope.refreshStatus();
  }

  $scope.incrPendingNow = function() {
    self.numPending += 1; $scope.refreshStatus();
  };

  $scope.decrPendingNow = function() {
    self.numPending -= 1; $scope.refreshStatus();
  };

  $scope.incrPending = function( delay ) {
    if( self.numPending > 0 ) {
      delay = 0;
    }
    else if( isNil(delay) ) {
      delay = 400;
    }
    setTimeout( $scope.incrPendingNow, delay );
  };

  //show working message not immediately but wait for delay before showing.
  $scope.decrPending = function( delay ) {
    if( self.numPending <= 0 ) {
      delay = 0;
    }
    else if( isNil(delay) ) {
      delay = 400;
    }
    setTimeout( $scope.decrPendingNow, delay );
  };

  $scope.openRoute = function( path, search ) {
    $location.path( path );
    $location.search( search || '' );
  };

  $scope.goBack = function() {
    $window.history.back();
  };

  //Make the row as clikable in the list view. But still allow text selection by
  //ignoring double clicks and drags.
  $scope.handleAsLink = function( $event, path, search ) {
    // Don't process the second click on a double click. clickPending is
    // true when waiting for a potential second click of a double-click.
    if( self.clickPending ) {
      self.clickPending = false;
      return;
    }
    self.clickStarted = false;
    self.clickPending = true;
    var deltaX = Math.abs( $event.screenX - self.clickStartX );
    var deltaY = Math.abs( $event.screenY - self.clickStartY );
    //console.log( distance );
    $timeout( function() {
      // If clickStarted is true, then a second mouse-down occurred, so
      // the click that kicked this off is really just the first in a
      // double-click sequence. If so, then we should not open the link
      // and should leave clickPending unchanged so that the second click
      // in the double-click will also be negated.
      if( self.clickStarted ) {
        // Since clickPending might have already blocked the mouse-up event
        // of a second click, reset clickStarted here. If the mouse-up
        // event is yet to come, then this is unnecesary but won't hurt.
        self.clickStarted = false;
      }
      else {
        self.clickPending = false;
        if( deltaX < 4 && deltaY < 4 ) {
          $scope.openRoute( path, search );
        }
      }
    }, 200 );
  };

  //works with handleAsLink().
  $scope.clickStart = function( $event ) {
    self.clickStarted = true;
    self.clickStartX = $event.screenX;
    self.clickStartY = $event.screenY;
  };

  $scope.blankRegex = new RegExp( '^[ \t]*$' );
  $scope.nonBlankRegex = new RegExp( '.*[^ \t].*' );
  $scope.nonBlank = function( val ) {
    val = isNil(val) ? '' : val.toString();
    if( $scope.nonBlankRegex.test(val) ) {
      return val;
    }
    return val + '\u00A0';
  };

  $scope.regex = function( pattern, flags ) {
    return new RegExp( pattern, flags );
  };

  $scope.formatAsName = function( str ) {
    return formatAsName( str );
  };

  //Status area is the section of the bottom of the page that shows things like
  //error message and result of operation like: config created successfully.
  this.clearStatusArea = function() {
    $scope.statusType = null;
    $scope.statusTitle = null;
    $scope.statusDesc = null;
    $scope.statusDetails = null;
  };

  //It gets put up in status area
  this.showSuccess = function( title, message ) {
    self.clearStatusArea();
    $timeout( function() {
      $scope.blipError = true;
      $timeout( function() { $scope.blipError = false; }, 500 );
    }, 100 );
    $scope.statusType = 'success';
    $scope.statusTitle = title;
    $scope.statusDesc = message;
  };

  //It is an error message that gets shown up in status area. It formats the
  //error messages nicely.
  this.showErrorResponse = function( args ) {
    $scope.decrPending();
    self.clearStatusArea();
    $timeout( function() {
      $scope.blipError = true;
      $timeout( function() { $scope.blipError = false; }, 500 );
    }, 100 );
    $scope.statusType = 'error';
    if( args.status ) {
      $scope.statusTitle = 'Error ' + args.status + ':';
    }
    else {
      $scope.statusTitle = 'Error:';
    }
    $scope.statusDetails = {};
    if( isA( args.data, 'String' ) ) {
      line = args.data;
      if( line[0] == '"' && line[line.length-1] == '"' ) {
        line = angular.fromJson( line );
      }
      $scope.statusDetails['Details'] = [line];
    }
    else {
      for( var d in args.data ) {
        var field = $scope.tableDef ? $scope.tableDef.fieldMap[d] : null;
        var label = ( field && field.disp ) || d;
        var lines = args.data[d];
        if( !isA( lines, 'Array' ) ) {
          lines = [lines];
        }
        $scope.statusDetails[label] = lines;
      }
    }
    //console.log( angular.toJson(arguments,true) );
    $scope.setState( 'ready' );
  };

  //Regex to split the value to pieces to that they can line wrap even when they
  //don't have whitespace.
  var valSplitRegex = /([^a-zA-Z0-9 ]+)/;
  $scope.splitVal = function( val ) {
    if( val.split ) {
      return val.split( valSplitRegex );
    }
    return [val];
  };

  //Gives list of items.
  this.query = function( params, successCB, errorCB ) {
    $scope.incrPending();
    return BasicTable.list( params,
      function(item) {
        $scope.decrPending();
        if( successCB ) successCB();
      },
      function(item) {
        $scope.setShortError( 'failed to query ' + params._table + ' list' );
        if( errorCB ) errorCB();
      }
    );
  };
}


////////////////////////////////////////////////////////////
//Used for Home Page
function HomeCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  RootCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  var self = this;

  $scope.sections = [
    { heading: 'Config Sets',
      tables: [
        { name:'cfg_devicetype', dispName:'DeviceType Level \u00A0(hwtype.carrier.region)' },
        { name:'cfg_carrier', dispName:'Carrier Level \u00A0(carrier.region)' },
        { name:'cfg_global', dispName:'Global Defaults' },
        { name:'cfg_delta', dispName:'Delta Config' }
        ],
      manager: [
        { route:'#/cfg_superset/new', dispName:'Instantiate All Configs for a Devicetype' },
        { route:'#/cfgreport', dispName:'Config Versions Report' },
        { route:'#/bulkupdate/search', dispName:'Bulk Update' }
        ]
    },
    { heading: 'Other Data',
      tables: [
        { name:'extra_key', dispName: 'Extra Key'},
        { name:'extra_value', dispName: 'Extra Value'},
        { name:'hwtype', dispName:'HW Type' },
        { name:'carrier', dispName:'Carrier' },
        { name:'region', dispName:'Region' },
        { name:'setting_def', dispName:'Setting Definition' },
        { name:'setting_category', dispName:'Setting Category' },
        { name:'cloud_env', dispName:'Cloud Environment' },
        { name:'env_transform', dispName:'Environment Transform' },
        { name:'user', dispName:'User' }
        ] }
  ];
  $scope.tableDefs = tableDefs;

  $scope.heading = function( tableInfo ) {
    if( tableInfo.dispName ) {
      return tableInfo.dispName;
    }
    return tableDefs[tableInfo.name||tableInfo].dispName;
  }

  $scope.tablePath = function( tableInfo ) {
    return tableInfo.name || tableInfo;
  }
}

////////////////////////////////////////////////////////////
//
function CommonCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  RootCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  var self = this;

  $scope.setState( 'loading' );
  $scope.mode = 'view';
  $scope.tableDefs = tableDefs;
  if (!$scope.table) {
    $scope.table = $routeParams.table;
  }
  $scope.tableDef = tableDefs[ $scope.table ];

  if( ! $scope.tableDef ) {
    $scope.error = 'table';
    $scope.errorTitle = 'Unknown table "' + $scope.table + '"';
    return $scope.error;
  }

  // Ref tables is used to load the data from the database.

  $scope.refTables = {};
  //Used to do foreign key lookup to some other table.
  $scope.refTable = function( field, newVal ) {
    // TODO: IE (version 8) does not update selection lists when the
    // result of this changes and has issues if the result is an empty
    // list. Is it just an incompatibility between IE and Angular?
    var result = $scope.refTables[field.ref];
    if( $scope.item && field.filterRef ) {
      result = field.filterRef( $scope.item, result );
    }
    return result;
  };

  //Takes name from schema.js and gives you the API name of the table. Ex:
  //cfg_devicetype=config_set
  $scope.tableName = tableName = function( tableAlias ) {
    tableAlias = tableAlias || $scope.table;
    return tableDefs[tableAlias].table || tableAlias;
  };
  // console.log("tableName- " + tableName);

  $scope.refsLoadedCB = function(success) {
  };

  //To be used for querying data from Reference tables.
  function queryRefTable( tableAlias ) {
    var params = { '_table': tableName(tableAlias) };
    copyFields( $scope.tableDefs[tableAlias].filter, params );
    $scope.incrPending();
    $scope.refTables[tableAlias] = BasicTable.list(params,
      function(items) {
        $scope.decrPending();
        var tableDef = $scope.tableDefs[tableAlias];
        items.sort( function(a,b) {
          var valA = (tableDef.itemName(a) || '');
          var valB = (tableDef.itemName(b) || '');
          return compareNoCase(valA,valB) || compare(valA,valB);
        } );
        $scope.refsLoadedCB(true);
      },
      function() {
        $scope.setShortError( 'failed to query table reference' );
        $scope.decrPending();
        $scope.refsLoadedCB(false);
      }
      );
  }

  //$timeout( function() {
  if( !$scope.skipRefLookup ) {
    for( var f in $scope.tableDef.fieldList ) {
      var field = $scope.tableDef.fieldList[f];
      if( field.ref && field.showFor($scope.mode,$scope.pageType) ) {
        if( ! $scope.refTables[field.ref] ) {
          queryRefTable( field.ref );
        }
      }
    }
  }
  //}, 1000 );

  /**
   * Obtain the display value for the field as defined in the schema.
   * item is the row and field is the column.
   */
  $scope.dispVal = function( item, field ) {
    if( !field.ref ) {
      return field.dispVal(item);
    }
    if( isNil(item) ) {
      return null;
    }
    var refVal = item[field.name];
    if( isNil(refVal) ) {
      return null;
    }
    var refTableDef = tableDefs[field.ref];
    // TODO: The refTable() function does dynamic filtering in some cases.
    // Consider whether it is better to directly access the unfiltered
    // table here (mainly for performance).
    var refTable = $scope.refTable(field);
    var refDisp = null;
    for( var i in refTable ) {
      if( refTable[i][field.refCol||'id'] == refVal ) {
        refDisp = refTableDef.itemName( refTable[i] );
        break;
      }
    }
    if( isNil(refDisp) ) {
      refDisp = refVal;
    }
    return refDisp;
  };

  $scope.hash = function() {
    var hash = {};
    for( var i = 0; i < arguments.length-1; i+=2 ) {
      hash[arguments[i]] = arguments[i+1];
    }
    return hash;
  };
}


////////////////////////////////////////////////////////////
//
function ListCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  CommonCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  var self = this;

  $scope.pageType = 'list';
  $scope.colFilters = [];
  $scope.offset = parseInt( $routeParams.offset || 0 );
  $scope.maxOptions = ["20", "100", "500", "1000"];
  $scope.max = parseInt( $routeParams.max || 20 );
  if($scope.max < 5) {
    $location.search('max', 5);
    return;
  }
  if($scope.offset < 0) {
    $location.search('offset', 0);
    return;
  }
  $scope.maxSelected = '' + $scope.max;

  $scope.updateMax = function() {
    $location.search( 'max', $scope.maxSelected );
    $location.search( 'offset', 0 );
  };

  $scope.updateOffset = function( offset ) {
    $location.search( 'offset', offset );
  };

  $scope.refsLoadedCB = function(success) {
    if( success ) {
      for( var i in $scope.items ) {
        var item = $scope.items[i];
        var dispVals = {};
        for( var f in $scope.tableDef.fieldList ) {
          var field = $scope.tableDef.fieldList[f];
          dispVals[field.name] = $scope.dispVal( item, field );
        }
        item._dispVals = dispVals;
      }
    }
  };

  var params = copyFields( $location.search() );
  params.max = $scope.max;
  params['_table'] = tableName();
  copyFields( $scope.tableDef.filter, params );
  $scope.incrPending(100);

  $scope.isCurrentPage = function(pageNumber) {
    var offset = $scope.offset;
    var max = $scope.max;

    var curPage = Math.ceil( offset / max ) + 1;
    if (curPage == pageNumber) {
        return true;
    } else {
        return false;
    }
  };

  normalizeSequence = function( min, max, numArray ) {
    var resultArray = [];
    var prevNum = min - 1;
    for( var i=0; i < numArray.length; ++i ) {
        var num = numArray[i];
        if( num > prevNum && num <= max ) {
            resultArray.push( num );
            prevNum = num;
        }
    }
    return resultArray;
  };

  getPageNumbers = function() {
    offset = $scope.offset;
    max = $scope.max;
    var total = $scope.count;
    var page = Math.ceil( offset / max ) + 1;
    var maxpage;
    // If we are beyond what should be the last page, then just set
    // the maxpage to the current page so that the normal maxpage
    // calculation does not need to deal with that edge case.
    if( offset > total ) {
        maxpage = page;
    }
    else {
        // If the offset is at a partial page (not divisible by max),
        // then that can result in an extra page (since the first and
        // second page will overlap). To handle this, calculate the
        // max page by adding the remaining pages to the current page
        // instead of just using Math.ceil(total/max).
        maxpage = Math.ceil( (total-offset) / max ) + page - 1;
    }

    // A list of page numbers to display. Includes the first, last,
    // current, two next, two previous, ahead 10, and back 10. The
    // normalizeSequence function removes entries that are
    // duplicates or out of range.
    var pageArray = normalizeSequence( 1, maxpage, [1, page - 10, page - 2, page - 1, page,
            page + 1, page + 2, page + 10, maxpage ]);
    if( pageArray.length == 0 || page > pageArray[pageArray.length-1] ) {
        pageArray.push( page );
    }

    return pageArray;
  };

  $scope.items = BasicTable.list( params,
    function() {
      $scope.refsLoadedCB(true);
      $scope.setState( 'ready' );
      setTitle( $scope.tableDef.dispName + ' List' );
      $scope.decrPending(500);
    },
    function() {
      $scope.decrPending();
      $scope.setShortError( 'failed to query table' );
    }
  );

  params['action'] = 'count';
  $scope.incrPending();
  BasicTable.read(params,
    function(item) {
      $scope.decrPending();
      $scope.count = item.count;
     //Verifying if the offset is within the range. If not set it to right value using location.search.
     if($scope.offset > $scope.count) {
        var temp = $scope.count - $scope.max;
        //location.search will cause the page to reload with the new value of the offset.
        $location.search('offset', temp);
      }
      $scope.pageNumbers = getPageNumbers();
    },
    self.errorCallback
  );

  $scope.applyFilter = function() {
    $location.search( 'offset', 0 );
    for( var fieldName in $scope.colFilters ) {
      var colFilter = $scope.colFilters[fieldName];
      $location.search( $scope.filterKey(fieldName), colFilter || null );
    }
  };

  $scope.clearFilter = function() {
    $location.search( 'offset', 0 );
    for( var fieldName in $scope.colFilters ) {
      $location.search( $scope.filterKey(fieldName), null );
    }
  }

  $scope.filterKey = function( fieldName ) {
    var field = $scope.tableDef.fieldMap[fieldName];
    if( field.filterKey === false ||
        ( field.ref && !field.refCol && !field.filterKey ) ) {
      return null;
    }
    return field.filterKey || 'like.' + fieldName;
  }

  for( var f in $scope.tableDef.fieldList ) {
    var fieldName = $scope.tableDef.fieldList[f].name;
    var filterKey = $scope.filterKey(fieldName);
    if( filterKey ) {
      $scope.colFilters[fieldName] = $routeParams[ $scope.filterKey(fieldName) ];
    }
  }

}


////////////////////////////////////////////////////////////
//
function ItemCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  var error = CommonCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  var self = this;

  if( error ) {
    return error;
  }

  $scope.id = $routeParams.id;
  $scope.itemName = null;
  if( window.tmpItem ) {
    $scope.itemName = $scope.tableDef.itemName(window.tmpItem);
    window.tmpItem = undefined;
  }

  $scope.moreNew = false;

  $scope.getTitlePrefix = function() {
    var result = $scope.tableDef.dispPrefix;
    if( !result || !$scope.itemName ) {
      result = $scope.tableDef.dispName;
    }
    return result;
  };

  $scope.getCancelRoute = function() {
    return '#/' + $scope.table + '/' +
      ( $scope.id ? 'view/'+$scope.id : 'list' );
  };

  this.afterQuery = function(item) {};

  if( $routeParams.id ) {
    var idParts = $routeParams.id.split( '=', 2 );
    var params = { '_table': tableName() };
    var keyName = 'id';
    var keyValue = idParts[0];
    if( idParts.length > 1 ) {
      keyName = idParts[0];
      keyValue = idParts[1];
      params['eq.'+keyName] = keyValue;
    }
    else {
      params.id = keyValue;
    }
    $scope.incrPending();
    queryOne( BasicTable, params,
      function(item) {
        $scope.decrPending();
        $scope.id = item.id;
        $scope.item = new BasicTable(item);
        // Although an ID can be passed when opening the "new" page, that
        // should only give inital values for the form fields. We do not
        // want the new item to have that same ID or itemName.
        if( $scope.mode == 'new' ) {
          $scope.item.id = null;
        }
        else {
          $scope.itemName = $scope.tableDef.itemName(item);
        }
        if ($scope.item && $scope.item.extra_value) {
          $scope.item.extra = $scope.item.extra_key + ':' + $scope.item.extra_value;
        }
        setTitle( $scope.getTitlePrefix() + ': ' + ($scope.itemName || '') );
        $scope.setState( 'ready' );

        self.afterQuery( item );
      },
      function( count ) {
        $scope.decrPending();
        var prefix = 'id=';
        $scope.error = 'id';
        if( count == 0 ) {
          $scope.errorTitle = 'No item in "' + $scope.table +
              '" table with ' + keyName + '=' + keyValue;
        }
        else {
          $scope.errorTitle = 'Multiple matches in "' + $scope.table +
              '" table with ' + keyName + '=' + keyValue;
        }
        $scope.setState( 'ready' );
        setTitle( 'Error: ' + $scope.errorTitle );
      }
    );
  }
  else {
    var item = {};
    for( var i in $scope.tableDef.fieldList ) {
      var field = $scope.tableDef.fieldList[i];
      item[field.name] = field.val;
    }
    $scope.item = new BasicTable(item);
    $scope.setState( 'ready' );
    setTitle( $scope.getTitlePrefix() + ': ' );
  }

  $scope.findRow = findRow;

  $scope.locked = function( field ) {
    return $scope.state == 'loading' || (field.lock >= modeEnum[$scope.mode] );
  };

  $scope.setSubmitted = function( flag ) {
    $scope.submitted = flag;
  };

  /**
   * This method will be used to valid the form
   */
  self.updateParams = function( params ) {

      /** This rule verify if user selected the extra key but not selected extra_value*/
      if(params._table === 'config_set') {
          if(params.hasOwnProperty('extra_key') && params.hasOwnProperty('extra_value_id')) {
              if(params.extra_key && isNil(params.extra_value_id)) {
                  throw 'When the extra key is selected, It is necessary select extra value';
              }
          }
      }

  };

  $scope.save = function() {
    $scope.setState( 'working' );
    $scope.setSubmitted( true );
    self.clearStatusArea();
    $scope.item._table = tableName();

    $scope.incrPending();

    //$timeout( function() {
    var prepError = null;
    if( $scope.tableDef.prepForSave ) {
      prepError = $scope.tableDef.prepForSave( $scope.item, $scope.refTables );
    }
    if( prepError ) {
      self.showErrorResponse( { status: 'Validating', data: prepError } );
      return;
    }

    var params = copyFields( $scope.item );
    try {
      self.updateParams( params );
    }
    catch( e ) {
      self.showErrorResponse( { status: 'Validating', data: e } );
      return;
    }

    BasicTable.write( params,
      function(item) {
        $scope.decrPending();
        $scope.setState( 'ready' );
        if( $scope.moreNew ) {
          self.showSuccess( 'Success:', 'Created "' + $scope.tableDef.itemName(item) + '".' );
        }
        else {
          if( $scope.table == 'cfg_superset' ) {
            $scope.openRoute( '/' );
          }
          else if( $scope.mode == 'edit' || tableName() == 'config_set' ) {
            setTmpItem( $scope.item );
            $scope.openRoute( '/' + $scope.table + '/view/' + item.id );
          }
          else {
            $scope.openRoute( '/' + $scope.table + '/list' );
          }
        }
      },
      self.showErrorResponse
    );
    //}, fakeWait ); fakeWait = 500;
  };

  $scope.remove = function() {
    if( $window.confirm( 'Delete ' + $scope.tableDef.dispName + ' "' + $scope.tableDef.itemName($scope.item) + '"?' ) ) {
      self.clearStatusArea();
      $scope.item._table = tableName();
      $scope.incrPending();
      BasicTable.destroy($scope.item,
        function(item) {
          $scope.decrPending();
          $scope.openRoute( '/' + $scope.table + '/list' );
        },
        self.showErrorResponse
      );
    }
  };

}


////////////////////////////////////////////////////////////
//
function CfgSetCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  $routeParams.table = 'cfg_' + $routeParams.cfgtable;
  $scope.vars = { verId: null };
  var error = ItemCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  var self = this;

  if( error ) {
    return error;
  }

  if ($rootScope.settings_mismatch) {
    $scope.settings_mismatch = $rootScope.settings_mismatch
    $scope.settings_mismatch_values = $rootScope.settings_mismatch_values
    $scope.settings_mismatch_list = $rootScope.settings_mismatch_list
//    for (key in settings_mismatch_values) {
//      $scope.settings_mismatch_values[key] = $rootScope.settings_mismatch_values[key]
//    }
    $rootScope.settings_mismatch_values = {}
    $rootScope.settings_mismatch_list = []
    $rootScope.settings_mismatch = ''
  }
  $scope.extraContent = 'static/ui/views/cfgset_detail.html';

  this.afterQuery = function(item) {
    getVersions( item.id );
    getSettingDefs();
  };

  function getSettingDefs() {
    if( tableName() != 'config_set' ) {
      $scope.cfgData = {};
      return;
    }
    var params = { _table: 'setting_def', 'eq.category_id': $scope.item.category_id };
    $scope.incrPending();
    BasicTable.list( params,
      function(items) {
        $scope.decrPending();
        $scope.help = {};
        $scope.settingDefs = items;

        // TODO: Right now getSettings() is called both after getting the
        // setting defs and after getting the versions. This is done to
        // make sure the settings get correctly updated, but it could be
        // done more effeciently.
        $scope.getSettings();
        //console.log( 'SETTING-DEFS: ' + angular.toJson(items,true) );
      },
      function() {
        $scope.decrPending();
        $scope.setShortError( 'failed to query setting definitions' );
        $scope.settingDefs = [];
      }
    );
  }

  //Value of checkbox, if it is checked or not.
  $scope.editPicks = {};
  //Value of the field edited by user.
  $scope.editVals = {};

  $scope.pickChanged = function( settingName ) {
    if( $scope.editPicks[settingName] ) {
      $scope.editVals[settingName] = $scope.cfgData.settings[settingName] || '';
    }
    else {
      $scope.cfgData.settings[settingName] = $scope.editVals[settingName];
      $scope.editVals[settingName] = $scope.getSettingVal( settingName );
    }
  };

  $scope.valChanged = function( settingName ) {
    if( !$scope.editPicks[settingName] ) {
      $scope.cfgData.settings[settingName] = $scope.editVals[settingName];
      $scope.editPicks[settingName] = true;
    }
  };

  $scope.verChanged = function() {
    $scope.getSettings();
  };

  $scope.getSettings = function() {
    if( !$scope.vars.verId || !$scope.settingDefs ) {
      return;
    }
    var params = { _table: 'config_version', id: $scope.vars.verId, _action:'settings' };
    $scope.incrPending();
    BasicTable.read( params,
      function(item) {
        $scope.decrPending();
        $scope.cfgData = item;
        if( $scope.mode == 'settingEdit' ) {
          $scope.editPicks = {};
          for( var s in $scope.settingDefs ) {
            var settingName = $scope.settingDefs[s].name;
            if( isNil( $scope.cfgData.settings[settingName] ) ) {
              $scope.editPicks[settingName] = false;
              $scope.editVals[settingName] = $scope.getSettingVal( settingName );
              $scope.cfgData.settings[settingName] = $scope.editVals[settingName];
            }
            else {
              $scope.editPicks[settingName] = true;
              $scope.editVals[settingName] = $scope.cfgData.settings[settingName];
            }
          }
         }
      },
      function() {
        $scope.decrPending();
        $scope.setShortError( 'failed to query setting values' );
        $scope.cfgData = {};
      }
    );
  };

  function getVersions( configSetId ) {
    if( !$scope.versions && tableName() == 'config_set' ) {
      var verParams = { _table: 'config_version', 'eq.config_set_id': configSetId };
      $scope.incrPending();
      BasicTable.list( verParams,
        function(items) {
          $scope.decrPending();
          $scope.versions = items;
          $scope.versions.sort( function(a,b){ return b.version_number-a.version_number } );
          var currVer = null;

          if( $location.search().vnum ) {
            if ($scope.revert) {
              currVer = findRow( $scope.versions, { version_number: $scope.getVersionToBeReverted('published').version_number} );
              $location.search('vnum', currVer.version_number)
            } else {
              currVer = findRow( $scope.versions, { version_number: $location.search().vnum } );
            }
          }
          if( !currVer ) {
            currVer = $scope.versions[0];
            //if we are at the uncommited version.
            if( $scope.mode == 'view' && !currVer.last_edited && !currVer.committed ) {
              if( currVer.fallback_id != $scope.versions[1].fallback_id ) {
                currVer.parentChanged = true;
              }
              else {
                //Setting the current version to latest uncommited version.
                currVer = $scope.versions[1];
                //$scope.versions.shift();
              }
            }
          }
          $scope.vars.verId = currVer.id;
          $scope.getSettings();
        },
        function() {
          $scope.decrPending();
          $scope.setShortError( 'failed to query versions' );
        }
      );
    }
  }

  $scope.ver = function( verId ) {
    return findRow( $scope.versions, { id: verId } );
  };

  $scope.getLatestVer = function( stateField ) {
    for( v in $scope.versions ) {
      if( $scope.versions[v][stateField] ) {
        return $scope.versions[v];
      }
    }
  };

  /**
   * Return the Count of the number of versions in specific state.
   */
  $scope.getVersionsCount = function( stateField ) {
    var count = 0;
    for( v in $scope.versions ) {
      if( $scope.versions[v][stateField] ) {
        count ++;
        }
      }
    return count;
    };

 /**
  * includeTgt: Determines if we can perform the operation on the given version if
  * it is same as the latest version of the config set in the tgtState.
  * For example for republish, reqstate=tgtstate. Hence it is ok to have the latest
  * version in tgtstate to be same as version in reqstae. Similarly for revert,
  * latest version in reqState can be moved to latest version in tgtState.
  */
  $scope.verComplies = function( version, reqState, tgtState, includeTgt ) {
    if( reqState && !version[reqState] ) {
      return false;
    }
    if( tgtState ) {
      if( tgtState == 'published' && !$scope.tableDef.canPublish ) {
        return false;
      }
      if (tgtState == 'approved' && reqState == 'published') {
        //If there are less than 2 published version or if user is not publisher. Then we want to hide revert.
        if (!$scope.tableDef.canPublish || ($scope.getVersionsCount('published') < 2)) {
          return false;
        }
       //Allow revert only from last published version.
        var lastPublished = $scope.getLatestVer( 'published' );
        if (lastPublished.version_number == version.version_number) {
          return true;
        } else {
          return false;
        }
      }
      var last = $scope.getLatestVer( tgtState );
      if( last && version.version_number < last.version_number ) {
        return false;
      }
      //We can publish the last approved version.
      if( last && !includeTgt && version.version_number == last.version_number ) {
        return false;
      }
    }
    return true;
  };

  $scope.getSettingVal = function( settingName ) {
    var currCfg = $scope.cfgData;
    if( !currCfg ) {
      return null;
    }
    if( $scope.mode == 'settingEdit' ) {
      if( $scope.editPicks[settingName] ) {
        return $scope.editVals;
      }
      currCfg = currCfg.fallback;
    }
    while( currCfg ) {
      if( isDef( currCfg.settings[settingName] ) ) {
        return currCfg.settings[settingName];
      }
      currCfg = currCfg.fallback;
    }
    return null;
  };

  $scope.getSettingSrc = function( settingName ) {
    var currCfg = $scope.cfgData;
    if( !currCfg ) {
      return null;
    }
    if( $scope.mode == 'settingEdit' ) {
      if( $scope.editPicks[settingName] ) {
        return tableDefs.config_set.itemName( currCfg, true );
      }
      currCfg = currCfg.fallback;
    }
    while( currCfg ) {
      if( isDef( currCfg.settings[settingName] ) ) {
        return tableDefs.config_set.itemName( currCfg, true );
      }
      currCfg = currCfg.fallback;
    }
  };

  $scope.settingLevel = function( settingName ) {
    if( !$scope.getSettingSrc(settingName) ) {
      return -1;
    }
    if( !$scope.cfgData || !$scope.cfgData.fallback ) {
      return 0;
    }
    if( $scope.mode == 'settingEdit' ) {
      return $scope.editPicks[settingName] ? 2 : 1;
    }
    return isDef( $scope.cfgData.settings[settingName] ) ? 2 : 1;
  };

  $scope.hasRole = function( role ) {
    result = $rootScope.currUser[role];
    if( !$scope.item || !$scope.item.region ) {
      result = result && $rootScope.currUser.admin;
    }
    return result;
  };

  $scope.discardSettings = function() {
    if( !$window.confirm( 'Discard uncommitted changes?' ) ) {
      return;
    }
    $scope.setState( 'working' );
    $scope.setSubmitted( true );
    self.clearStatusArea();
    var params = { _table: 'config_version', id: $scope.versions[0].id,
        _action: 'discard' };

    $scope.incrPending();
    BasicTable.write( params,
      function(item) {
        $scope.decrPending();
        $scope.versions = undefined;
        getVersions( $scope.id );
        $scope.setState( 'ready' );
      },
      self.showErrorResponse
    );
  };

  $scope.editFresh = function() {
    if( $scope.versions[0].last_edited ) {
      if( !$window.confirm( 'You chose to edit while viewing a committed ' +
          'version. However, uncommitted changes already exist.\n\n' +
          'Continue to edit the uncommitted version.' + '\n  ... or ...\n' +
          'Cancel and discard the uncommitted changes before editing.' ) ) {
        return;
      }
    }
    setTmpItem( $scope.item );
    $scope.openRoute( '/' + $scope.table + '/settings/' + $scope.item.id );
  };

  $scope.saveSettings = function() {
    $scope.setState( 'working' );
    $scope.setSubmitted( true );
    self.clearStatusArea();
    var params = { _table: 'config_version', id: $scope.cfgData.id, comment: $scope.cfgData.comment, _action: 'settings', settings: {} };
    for( var s in $scope.settingDefs ) {
      var settingName = $scope.settingDefs[s].name;
      if( $scope.editPicks[settingName] ) {
        params.settings[settingName] = $scope.editVals[settingName]
      }
    }

    $scope.incrPending();
    BasicTable.write( params,
      function(item) {
        $scope.decrPending();
        $scope.setState( 'ready' );
        setTmpItem( $scope.item );
        $scope.openRoute( '/' + $scope.table + '/view/' + $scope.item.id );
      },
      self.showErrorResponse
    );
  };

  self.applySuccess = function(item) {
    $scope.decrPending();
    $scope.setState( 'ready' );
    setTmpItem( $scope.item );
    if (item.settings_mismatch) {
      console.log('setting_mismatch- ' + item.settings_mismatch)
      $rootScope.settings_mismatch = item.settings_mismatch
      settings_mismatch_keys =  item.settings_mismatch.split(",")
//      for (var key in settings_mismatch_keys) {
      $rootScope.settings_mismatch_values = item.settings_mismatch_values
      $rootScope.settings_mismatch_list = item.settings_mismatch_list
//      }
      //$rootScope.settings_mismatch_values = item.settings_mismatch_values
    }
    $scope.openRoute( '/' + $scope.table + '/view/' + $scope.item.id );
  };

  $scope.applyAction = function() {
    $scope.setState( 'working' );
    $scope.setSubmitted( true );
    self.clearStatusArea();
    delete $scope.result;
    var params = copyFields( $scope.cfgData );
    params._table = 'config_version';
    params._action = $scope.mode;
    //We don't need to explicitly specify params.comment=$scope.cfgData.comment because we have called copyFields() before.
    for( var p in $routeParams ) {
        if( p.match(/^pass\..*$/) ) {
            params[p.replace(/^pass\./,'')] = $routeParams[p];
        }
    }
    self.updateParams( params );

    $scope.incrPending();
    BasicTable.write( params,
      self.applySuccess,
      self.showErrorResponse
    );
  };

  $scope.importCheckinSettings = function (productCategory) {
    var productline = productCategory.split("(", 2);
    var params = {
        _table: 'importDataExplorerSettings',
        productline: productline[0].trim()
    };
    $scope.incrPending();
    BasicTable.read(params,
        function(item) {
        $scope.decrPending();
        data_explorer_settings = item.settings;
        for (var key in data_explorer_settings) {
            $scope.editVals[key] = data_explorer_settings[key];
            $scope.editPicks[key] = true;
          }
     },
     self.showErrorResponse
    );
  };

  $scope.showImportButton = function (itemName, tableName) {
    if (( $scope.tableDef.itemName(window.tmpItem).indexof('Checkin') > 0) && (tableName == "cfg_delta")) {
      return true;
    }
    return false;
  };

  }


////////////////////////////////////////////////////////////
//
function EditCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  ItemCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  $scope.mode = 'edit';
  $scope.titleAction = 'Edit';
}

////////////////////////////////////////////////////////////
//
function NewCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  ItemCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  $scope.mode = 'new';
  $scope.titleAction = 'New';
  $scope.itemName = null;
}

////////////////////////////////////////////////////////////
//
function SettingEditCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  CfgSetCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  $scope.cfgtable = $routeParams.cfgtable;
  $scope.mode = 'settingEdit';
}

////////////////////////////////////////////////////////////
//
function CommitCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  CfgSetCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  $scope.mode = 'commit';
  $scope.verb = 'Commit';
}

////////////////////////////////////////////////////////////
//
function ApproveCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  CfgSetCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  $scope.mode = 'approve';
  $scope.verb = 'Approve';
}

////////////////////////////////////////////////////////////
//
function PublishCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  CfgSetCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  $scope.mode = 'publish';
  $scope.verb = 'Publish' + ( $routeParams['pass.dryrun'] === '1' ? ' (Dry-Run)' : '' );
}

//Revert back to last published version
function RevertCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  $scope.revert = true;
  CfgSetCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );

  $scope.getVersionToBeReverted = function( stateField ) {
    var latestVersions = new Array();
    for( v in $scope.versions ) {
      if( $scope.versions[v][stateField] ) {
        latestVersions.push($scope.versions[v]);
        if (latestVersions.length == 2) {
          return latestVersions[1];
        }
      }
    }
  };
  $scope.mode = 'revert';
  $scope.verb = 'Revert to' + ( $routeParams['pass.dryrun'] === '1' ? ' (Dry-Run)' : '' );

}

////////////////////////////////////////////////////////////
//
function TestPublishCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  CfgSetCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  $scope.mode = 'testpublish';
  $scope.verb = 'Publish for Test' + ( $routeParams['pass.dryrun'] === '1' ? ' (Dry-Run)' : '' );

  $scope.cloud_list = this.query(
    { _table: 'cloud_env', 'ne.env_type': 'prod' } );

  this.updateParams = function( params ) {
    if( $scope.testhw_enabled )
      params.hwsuffix = '_' + $scope.testhw + '_TEST';
    if( $scope.testcloud_enabled )
      params.env = $scope.testcloud;
  };
}

////////////////////////////////////////////////////////////
//
function PropagateCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  CfgSetCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );

  $scope.mode = 'propagate';
  $scope.verb = 'Propagate';

  $scope.cloud_choices = {};

  //Populate the cloud list to include production as well if you are an admin.
  if ($rootScope.currUser.publisher) {
    $scope.cloud_list = this.query({_table: 'cloud_env'});
  } else {
    $scope.cloud_list = this.query({ _table: 'cloud_env', 'ne.env_type': 'prod'});
  }

  $scope.levels = [1,2]
  $scope.level = 2
  $scope.showLevels = false
  if ($routeParams.cfgtable == 'global')
    $scope.showLevels = true

  this.updateParams = function( params ) {
    params.commitdepth = $scope.commit_enabled ? $scope.level : -1;
    params.approvedepth = $scope.approve_enabled ? $scope.level : -1;
    params.publish_envs = [];
    for( env in $scope.cloud_choices ) {
        if( $scope.cloud_choices[env] ) {
            params.publish_envs.push( env );
        }
    }
  };


  this.applySuccess = function(item) {
    $scope.decrPending();
    $scope.setState( 'ready' );
    $scope.result = item;
  };

  $scope.getCfgTable = getCfgTable;
}

////////////////////////////////////////////////////////////
//
function CfgSupersetCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  $routeParams.table = 'cfg_superset';
  NewCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  $scope.titleAction = null;
  var self = this;

  $scope.category_choices = {};
  $scope.category_list = this.query(
    { _table: 'setting_category' } );

  $scope.cloud_choices = {};
  $scope.cloud_list = this.query(
    { _table: 'cloud_env', 'ne.env_type': 'prod' } );

  self.addFallbacks = function( params ) {
    if( !params.region ) {
      return;
    }
    params.fallback = {};
    if( params.hwtype ) {
      params.fallback.carrier = params.carrier;
      params.fallback.region = params.region;
    }
    self.addFallbacks( params.fallback );
  };

  self.updateParams = function( params ) {

    if(params.extra_key && isNil(params.extra_value_id)) {
      throw 'When the extra key is selected, It is necessary select extra value';
    }
    if( params.extra_value_id && !(params.hwtype && params.carrier && params.region)) {
        throw 'If extra value is specified, hwtype, carrier and region must also be specified.'
    }
    if( params.hwtype && !(params.carrier && params.region) ) {
      throw 'If hwtype is specified, carrier and region must also be specified.';
    }
    if( !params.carrier != !params.region ) {
      throw 'If carrier is specified, region must be specified and vice versa.';
    }

    self.addFallbacks( params );
    params.category_id_list = [];
    for( categ in $scope.category_choices ) {
        if( $scope.category_choices[categ] ) {
            params.category_id_list.push( categ );
        }
    }
    if( params.category_id_list.length == 0 ) {
      throw 'At least one settings category must be specified.';
    }
    params.publish_envs = [];
    for( env in $scope.cloud_choices ) {
        if( $scope.cloud_choices[env] ) {
            params.publish_envs.push( env );
        }
    }
  };

  $scope.getCancelRoute = function() {
    return '#/';
  };
}

////////////////////////////////////////////////////////////
//
function LiveQueryCtrl($scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable) {
  RootCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );

  $scope.hwtype = $location.search().hwtype;
  $scope.region = $location.search().region;
  $scope.carrier = $location.search().carrier;
  $scope.extra = $location.search().extra;

  $scope.envs = ['prod', 'sdc200', 'qa300'];
  $scope.envModel = $rootScope.currUser.cloud;
  if (!$scope.envModel) {
    $scope.envModel = $scope.envs[0];
  }
  var params = {
    _table: 'livequery',
    hwtype: $scope.hwtype,
    region: $scope.region,
    carrier: $scope.carrier,
    extra: $scope.extra,
    env: $scope.envModel
  };
  $scope.envChanged = function(envname) {
    $scope.incrPending();
    params = {
      _table: 'livequery',
      hwtype: $scope.hwtype,
      region: $scope.region,
      carrier: $scope.carrier,
      extra: $scope.extra,
      env: $scope.envModel
    };
    BasicTable.read(params,
      function(item) {
        $scope.decrPending();
        $scope.setState( 'ready' );
        $scope.liveSettings = item.settings;
      },
      self.showErrorResponse
    );
  };
  $scope.incrPending();
  BasicTable.read(params,
    function(item) {
      $scope.decrPending();
      $scope.setState( 'ready' );
      $scope.liveSettings = item.settings;
    },
    self.showErrorResponse
  );
}

////////////////////////////////////////////////////////////
//
function CfgReportCtrl($scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable) {
  RootCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );

  $scope.tableDefs = tableDefs;

  setTitle( 'Config Versions Report' );

  $scope.incrPending();
  BasicTable.list( { _table: 'cfgreport' },
    function(results) {
      $scope.decrPending();
      $scope.setState( 'ready' );
      // To avoid extra checks later, if a version is not
      // published/etc, give it an empty object value.
      for( var r in results ) {
        results[r].committed = results[r].committed || {};
        results[r].approved = results[r].approved || {};
        results[r].published = results[r].published || {};
      }
      $scope.results = results;
      $scope.updateFilter();
    },
    self.showErrorResponse
  );

  $scope.getCfgTable = getCfgTable;

  // Is the approved version different from the committed version.
  $scope.approvedDiff = function( result ) {
    return result.approved.ver != result.committed.ver;
  };

  // Is the published version different from the approved version.
  // (Returns false unless the config set is one that can be published.)
  $scope.publishedDiff = function( result ) {
    return result.hwtype && result.published.ver != result.approved.ver;
  };

  // Update $scope.filteredResults to be $scope.results except
  // with the current filter applied.
  $scope.updateFilter = function() {
    $scope.incrPendingNow();
    $timeout( function() {
      $scope.filteredResults = [];
      for( var r in $scope.results ) {
        var result = $scope.results[r];
        if( (!$scope.showApprDiffs && !$scope.showPubDiffs) ||
            ($scope.showApprDiffs && $scope.approvedDiff(result)) ||
            ($scope.showPubDiffs && $scope.publishedDiff(result)) ) {
          $scope.filteredResults.push( result );
        }
      }
      $scope.decrPending();
    }, 100 );
  };
}

////////////////////////////////////////////////////////////
//
function CfgImportCtrl( $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  RootCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );
  var self = this;
  $scope.state = 'ready'

  $scope.importCfg = function() {
    $scope.incrPending();
    $scope.setState( 'working' );
    self.clearStatusArea();
    $scope.resultdata = null;
    var params = { _table: 'cfgimport' };
    BasicTable.save(params,
      function(item) {
        $scope.decrPending();
        $scope.resultdata = item;
        $scope.setState( 'ready' );
      },
      self.showErrorResponse
    );
  };
}

function BulkUpdateCtrl($scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable ) {
  $scope.table = 'cfg_devicetype';
  $scope.tableDef = tableDefs[ 'cfg_devicetype' ];
  $scope.skipRefLookup = true;
  var error = CommonCtrl.call( this, $scope, $rootScope, $window, $location, $routeParams, $timeout, BasicTable );

  $scope.tableDef = {fieldList: [
                                 new Field({ name:'extra_key', disp:'Extra Key', lock:1, ref:'extra_key', refCol:'code'}),
                                 new Field({ name:'extra_value', disp:'Extra Value', lock:1, ref:'extra_value', refCol:'id', filterKey:'like.extra_value_id.value'}),
                                 new Field({ name:'extra_value_name', disp:'Extra Value Name', lock:1, ref:'extra_value', refCol:'id', filterKey:'like.extra_value_id.name'}),
                                 new Field({ name:'hwtype', disp:'HW Type', lock:1, req:1, ref:'hwtype', refCol:'code' }),
                                 new Field({ name:'carrier', disp:'Carrier', lock:1, ref:'carrier', refCol:'code', hideFor:{'new':1,edit:1} }),
                                 new Field({ name:'region', disp:'Region', lock:1, ref:'region', refCol:'code' , hideFor:{'new':1,edit:1} }),
                                 new Field({ name:'category_id', disp:'Category', lock:1, req:1,
                                   filterKey:'like.category_id.name', ref:'setting_category', hideFor:{list:1} }),
                               ]};
  $scope.tableDef.fieldMap = {};
  $scope.tableDef.filter = {'nul.hwtype': 0, 'nul.carrier': 0, 'nul.region': 0 };

  for( var f in $scope.tableDef.fieldList ) {
    var field = $scope.tableDef.fieldList[f];
    $scope.tableDef.fieldMap[field.name] = field;
  }

  $scope.colFilters = [];
  var self = this;
  $scope.verb = 'Update'
  $scope.cbk = {};

  $scope.fieldName = [];
  $scope.fieldValue = [];
  $scope.categories = ['Admin', 'Checkin', 'Core'];

  $scope.existingValue = {};
  $scope.updatedValue = {};
  $scope.settingSelected = {};
  $scope.categorySelected = $routeParams["like.category_id.name"] || "Core";
  $scope.settingPicks = {};
  $scope.removeValue = {};
  if (!$scope.categorySelected) {
    $scope.categorySelected = "Core";
  }
  var configSetIds = [];
  //Keep the setting categories so that it can be used.
  getSettingCategories();


  if ($routeParams['like.category_id.name']) {
    //Obtain the setting definitions.
    getSettingDefs();

    configSetIds = [];
    //obtain the filters from the url in params so that device list can be retrieved.
  //  var params = copyFields($location.search());
    var params = $location.search();
    params['_table'] = tableName($scope.table);

    copyFields( $scope.tableDef.filter, params );
    $scope.incrPending();
    $scope.items = BasicTable.list( params,
       function() {
         $scope.refsLoadedCB(true);
         $scope.setState( 'ready' );
         setTitle( $scope.tableDef.dispName + ' List' );
         $scope.decrPending(500);
       },
       function() {
         $scope.decrPending();
         $scope.setShortError( 'failed to query table' );
       }
     );

    $scope.mode="bulkupdate";
  }

  $scope.valueChanged = function(settingName) {
    $scope.settingPicks[settingName] = Boolean(
        $scope.existingValue[settingName] || $scope.updatedValue[settingName]
        || $scope.removeValue[settingName]);
  }

  /**
   * Call this callback to obtain the display value for the field of an item.
   */
  $scope.refsLoadedCB = function(success) {
    if( success ) {
      for( var i in $scope.items ) {
        var item = $scope.items[i];
        var dispVals = {};
        for( var f in $scope.tableDef.fieldList ) {
          var field = $scope.tableDef.fieldList[f];
            dispVals[field.name] = $scope.dispVal( item, field );
        }
        item._dispVals = dispVals;
      }
    }
  };

  $scope.applyFilter = function() {
    for( var fieldName in $scope.colFilters ) {
      var colFilter = $scope.colFilters[fieldName];
      $location.search( $scope.filterKey(fieldName), colFilter || null );
    }
    $location.search($scope.filterKey('category_id'), $scope.categorySelected);
    filterApplied = true;
  };

  $scope.categoryChanged = function(categoryName) {
    //var categoryId = $scope.settingCategoriesId[categoryName];
    getSettingDefs();
    $scope.applyFilter();
  };
  $scope.clearFilter = function() {
    $location.search( 'offset', 0 );
    for( var fieldName in $scope.colFilters ) {
      $location.search( $scope.filterKey(fieldName), null );
    }
    filterApplied = false;
  };

  $scope.filterKey = function( fieldName ) {
    var field = $scope.tableDef.fieldMap[fieldName];
    if( field.filterKey === false ||
        ( field.ref && !field.refCol && !field.filterKey ) ) {
      return null;
    }
    return field.filterKey || 'like.' + fieldName;
  };

  for( var f in $scope.tableDef.fieldList ) {
    var fieldName = $scope.tableDef.fieldList[f].name;
    var filterKey = $scope.filterKey(fieldName);
    if( filterKey ) {
      $scope.colFilters[fieldName] = $routeParams[ $scope.filterKey(fieldName) ];
    }
  }

  $scope.cloud_choices = {};
  //Populate the cloud list to include production as well if you have publisher access.
  if ($rootScope.currUser.publisher) {
    $scope.cloud_list = this.query({_table: 'cloud_env'});
  } else {
    $scope.cloud_list = this.query({ _table: 'cloud_env', 'ne.env_type': 'prod'});
  }

  $scope.setSubmitted = function( flag ) {
    $scope.submitted = flag;
  };

  function getSettingCategories() {
    var params = { _table: 'setting_category' };
    $scope.incrPending();
    $scope.settingCategoriesName = [];
    $scope.settingCategoriesId = {};
    BasicTable.list( params,
      function(items) {
        $scope.decrPending();
        $scope.settingCategories = items;
        for (var d in $scope.settingCategories) {
          var category = $scope.settingCategories[d];
          $scope.settingCategoriesName[category.name] = category.name;
          $scope.settingCategoriesId[category.name] = category.id;
        }
      },
      function() {
        $scope.decrPending();
        $scope.setShortError( 'failed to query setting definitions' );
        $scope.settingCategories = [];
      }
    );
  }
  function getSettingDefs() {
    var params = { _table: 'setting_def', 'eq.category_id.name': $scope.categorySelected };
    //var params = { _table: 'setting_def'};
    $scope.incrPending();
    BasicTable.list( params,
      function(items) {
        $scope.settingNames = [];
        $scope.settingValues = [];
        $scope.decrPending();
        $scope.settingDefs = items;
        for (var d in $scope.settingDefs) {
          var def = $scope.settingDefs[d];
          $scope.settingNames[def.name] = def.name;
          $scope.settingNames[def.category_id] = def.id;
        }
      },
      function() {
        $scope.decrPending();
        $scope.setShortError( 'failed to query setting definitions' );
        $scope.settingDefs = [];
      }
    );
    }

  $scope.applyUpdate = function () {
    configSetIds = [];
    for (i in $scope.items ) {
      configSetIds.push($scope.items[i].id);
    }
    var params = { _table: 'bulkupdate', configsets: configSetIds, settings: {}};
    params.commit = $scope.commit_enabled ? 1: 0;
    params.approve = $scope.approve_enabled ? 1: 0;
    params.publish_envs = [];
    for( env in $scope.cloud_choices ) {
        if( $scope.cloud_choices[env] ) {
            params.publish_envs.push( env );
        }
    }
    for( var s in $scope.settingDefs ) {
      var settingName = $scope.settingDefs[s].name;
      if (!$scope.settingPicks[settingName]) continue;
      var existingValue = $scope.existingValue[settingName] || "";
      var updatedValue = $scope.updatedValue[settingName] || "";
      if ($scope.removeValue[settingName]) {
        updatedValue = '*remove*';
      }
      params.settings[settingName] = {"old": existingValue, "new": updatedValue};
    }
    var changed_settings = Object.keys(params.settings).length;
    if (changed_settings > 0 && !params.commit) {
      alert("Settings changes were requested. Please, select the \"Commit\" checkbox.");
      return false;
    }
    if (!params.commit && !params.approve && !params.publish_envs.length) {
      alert("Please, select at least one action to take.");
      return false;
    }
    $scope.incrPending();
    BasicTable.write(
        params,
        function(item) {
          $scope.decrPending();
          $scope.setState('ready');
          $scope.result = item;
//          self.showSuccess( 'Success:', 'Passed params to server.' );

        },
        self.showErrorResponse
    );
  }

  $scope.updatedValueChanged = function(settingName) {
    settings[settingName] = updatedValue[settingName];
  }

  $scope.importCheckinSettings = function () {
    var params = {
        _table: 'importDataExplorerSettings',
        productline: $scope.colFilters['hwtype']
     };
    $scope.incrPending();
    BasicTable.read(params,
        function(item) {
        $scope.decrPending();
        data_explorer_settings = item.settings;
        for (var key in data_explorer_settings) {
            $scope.updatedValue[key] = data_explorer_settings[key];
          }
     },
     self.showErrorResponse
    );
  }
//  $scope.importCheckinSettings = importCheckinSettings($scope.colFilters['hwtype'],  self.showErrorResponse);
}

angular.module('restApi', ['ngResource']).
  factory('BasicTable', function($resource) {
    var Factory = $resource(apiUrl+'/:_table/:id/:_action',
      { _table: '@_table', id: '@id', _action: '@_action', format: 'json' }, {
        update: { method: 'PUT' }
      }
    );

    Factory.noCache = function( fname, item, success, error ) {
      // TODO: For now, this is used to prevent IE from caching ajax
      // responses. However, if we make the server return reasonable
      // "Expires" header values (a time in the past for volatile data,
      // a time in the future for things like committed config settings),
      // then we might improve performance via browser/network caching.
      // Also, consider using some sort of time stamp for the nocache
      // value rather than a random number.
      item.nocache = Math.random();
      return Factory[fname]( item, success, error );
    }

    Factory.write = function( item, success, error ) {
      if( item.id ) {
        return Factory.noCache( 'update', item, success, error );
      }
      else {
        return Factory.noCache( 'save', item, success, error );
      }
    };

    Factory.read = function( item, success, error ) {
      return Factory.noCache( 'get', item, success, error );
    };

    Factory.list = function( item, success, error ) {
      return Factory.noCache( 'query', item, success, error );
    };

    Factory.destroy = function( item, success, error ) {
      return Factory.noCache( 'remove', item, success, error );
    };

    return Factory;
  });

