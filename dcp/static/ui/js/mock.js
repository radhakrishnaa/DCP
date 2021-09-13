
angular.module('cfgPortalWrap', ['cfgPortal', 'ngMockE2E'])
.run( function( $httpBackend ) {
  db = {
    hwtype: {
      rows: [
        { id: 1, code: 'XT912', internal_name: 'Spyder', marketing_name: 'Razr' },
        { id: 2, code: 'XT925', internal_name: 'Vanquish', marketing_name: 'Razr HD' },
        { id: 3, code: 'XT926', internal_name: 'Vanquish', marketing_name: 'Razr HD' },
        { id: 4, code: 'MB886', internal_name: 'Dinara', marketing_name: 'Atrix' }
    ]},
    carrier: {
      rows: [
        { id: 1, code: 'Verizon', name: 'Verizon' },
        { id: 2, code: 'ATT', name: 'AT&T' },
        { id: 3, code: 'ChinaMobile', name: 'China Mobile' },
        { id: 4, code: 'Nextcom', name: 'Nextcom>>' }
    ]},
    region: {
      rows: [
        { id: 1, code: 'CN', name: 'China' },
        { id: 2, code: 'US', name: 'United States' }
    ]},
    user: {
      defaults: { editor: false, approver: false, publisher: false, admin: false },
      rows: [
        { id: 1, username: 'mockuser', editor: true, approver: true, publisher: true, admin: true },
        { id: 2, username: 'superbob', editor: true, approver: true, publisher: true, admin: true },
        { id: 3, username: 'bob', editor: true, approver: false },
        { id: 4, username: 'joe123', editor: true }
    ]},
    setting_category: {
      rows: [
        { id: 1, name: 'Standard', comment: '' },
        { id: 2, name: 'Red Button', comment: '' }
    ]},
    setting_def: {
      rows: [
        { id: 1, name: 'blur.service.push.heartbeatTime', category_id: 1,
          display_name: 'Heartbeat', measure: 'ms', datatype: 'int',
          short_help:'The time (in milliseconds) between keep-alive messages sent to the server.' },
        { id: 2, name: 'blur.service.push.heartbeatTimeCarrierSpecific', category_id: 1,
          display_name: 'Carrier Specific Heartbeats', datatype: 'str',
          short_help:'A comma separated list of MCC:MNC:heartBeatTime entries (time in milliseconds).' },
        { id: 3, name: 'blur.service.update.download.offpeak.feature', category_id: 1,
          display_name: 'Offpeak Feature Enabled', datatype: 'bool' },
        { id: 4, name: 'blur.service.update.download.offpeak.start.time', category_id: 1,
          display_name: 'Offpeak Start Time', measure: 'ms', datatype: 'int',
          short_help:'The offpeak start time in milliseconds past midnight GMT.' },
        { id: 5, name: 'blur.service.update.download.offpeak.duration', category_id: 1,
          display_name: 'Offpeak Duration', measure: 'ms', datatype: 'int',
          short_help:'The offpeak duration in milliseconds.' },
        { id: 6, name: 'blur.service.update.download.promotion.time', category_id: 1,
          display_name: 'Promotion Time', measure: 'ms', datatype: 'int',
          short_help:'The promotion time in milliseconds.' },
        { id: 7, name: 'blur.service.upgrade.disallowed_networks', category_id: 1,
          display_name: 'Disallowed Networks', datatype: 'str',
          short_help:'A comma separated list of network types that will not be used for BOTA download. For example, "GPRS,EDGE,HSPA,UMTS".' },
        { id: 8, name: 'redbutton.feature.my.app.somefeature', category_id: 2,
          display_name: 'Toggle Some Feature', datatype: 'str',
          short_help:'Enable (1) or disable (0) "Some Feature" for My App.' },
    ]},
    config_set: {
      calc: function( row ) {
        row.category_name = getRow( db.setting_category, row.category_id ).name;
      },
      rows: [
        { id: 1, category_id: 1 },
        { id: 2, category_id: 1, fallback_id: 1, carrier: 'Verizon', region: 'US' },
        { id: 3, category_id: 1, fallback_id: 2, carrier: 'Verizon', region: 'US', hwtype:'XT912' }
    ]},
    config_version: {
      calc: function( row ) {
        row.last_editor = getRow( db.user, row.last_editor_id ).username;
        row.committer = getRow( db.user, row.committer_id ).username;
        row.approver = getRow( db.user, row.approver_id ).username;
        row.publisher = getRow( db.user, row.publisher_id ).username;
      },
      rows: [
        { id: 1, config_set_id: 1, version_number: 1,
          committer_id: 2, committed: '2013-01-23 10:03:00Z',
          approver_id: 2, approved: '2013-01-23 10:03:00Z' },
        { id: 2, config_set_id: 1, version_number: 2 ,
          last_editor_id: 2, last_edited: '2013-01-24 10:35:00Z',
          committer_id: 2, committed: '2013-01-24 10:41:00Z',
          approver_id: 2, approved: '2013-01-24 10:43:00Z' },
        { id: 3, config_set_id: 2, version_number: 1, fallback_id: 1,
          committer_id: 3, committed: '2013-01-01 12:30:00Z',
          approver_id: 2, approved: '2013-01-01 12:30:00Z' },
        { id: 4, config_set_id: 2, version_number: 2, fallback_id: 2,
          last_editor_id: 3, last_edited: '2013-01-01 12:34:00Z',
          committer_id: 3, committed: '2013-01-01 12:45:00Z',
          approver_id: 2, approved: '2013-01-01 12:50:00Z' },
        { id: 9, config_set_id: 3, version_number: 1, fallback_id: 3,
          committer_id: 2, committed: '2013-01-22 19:12:00Z',
          approver_id: 2, approved: '2013-01-22 19:12:00Z' },
        { id: 5, config_set_id: 3, version_number: 2, fallback_id: 3,
          last_editor_id: 2, last_edited: '2013-01-23 10:00:00Z',
          committer_id: 2, committed: '2013-01-23 10:03:00Z',
          approver_id: 2, approved: '2013-01-23 10:05:00Z',
          publisher_id: 2, published: '2013-01-23 15:27:00Z' },
        { id: 6, config_set_id: 3, version_number: 3, fallback_id: 4,
          last_editor_id: 3, last_edited: '2013-02-01 14:10:00Z',
          committer_id: 2, committed: '2013-02-07 09:45:00Z' },
        { id: 7, config_set_id: 3, version_number: 4, fallback_id: 4,
          last_editor_id: 3, last_edited: '2013-02-10 12:01:00Z',
          committer_id: 3, committed: '2013-02-11 8:50:00Z',
          approver_id: 2, approved: '2013-02-15 11:10:00Z' },
        { id: 8, config_set_id: 3, version_number: 5, fallback_id: 4,
          last_editor_id: 3, last_edited: '2013-02-20 13:20:00Z' },
        { id: 10, config_set_id: 1, version_number: 3 },
        { id: 11, config_set_id: 2, version_number: 3, fallback_id: 2,
          last_editor_id: 3, last_edited: '2013-01-01 12:34:00Z' },
    ]},
    config_version_settings: {
      rows: [
        { id: 1, version_id: 1, settings: {} },
        { id: 2, version_id: 2, settings: {
          'blur.service.push.heartbeatTime': '1680000',
          'blur.service.push.heartbeatTimeCarrierSpecific': '',
          'blur.service.update.download.offpeak.feature': 'false'
        }},
        { id: 10, version_id: 10, settings: {
          'blur.service.push.heartbeatTime': 1680000,
          'blur.service.push.heartbeatTimeCarrierSpecific': '',
          'blur.service.update.download.offpeak.feature': 'false'
        }},
        { id: 3, version_id: 3, settings: {} },
        { id: 4, version_id: 4, settings: {
          'blur.service.upgrade.disallowed_networks': 'GPRS,EDGE'
        }},
        { id: 11, version_id: 11, settings: {
          'blur.service.update.download.offpeak.feature': 'true',
          'blur.service.update.download.offpeak.start.time': '3600000',
          'blur.service.update.download.offpeak.duration': '10800000',
          'blur.service.update.download.promotion.time': '7200000',
          'blur.service.upgrade.disallowed_networks': 'GPRS,EDGE,HSPA'
        }},
        { id: 5, version_id: 5, settings: {} },
        { id: 6, version_id: 6, settings: {} },
        { id: 7, version_id: 7, settings: {
          'blur.service.update.download.offpeak.start.time': '1800000'
        }},
        { id: 8, version_id: 8, settings: {
          'blur.service.update.download.offpeak.start.time': '3600000',
          'blur.service.update.download.offpeak.duration': '7200000',
          'blur.service.push.heartbeatTimeCarrierSpecific': '525:1:1680000,525:3:1680000,525:5:540000,502:12:1680000,502:13:1680000,502:19:1680000,52:16:240000,502:13:960000,515:2:1680000,515:3:1680000,515:5:1680000,452:1:1680000,452:2:1680000,424:2:16800000,424:3:16800000,420:1:16800000,420:3:16800000,420:4:16800000,655:10:16800000,655:1:900000,655:7:900000'
        }}
    ]}
  };

  function getRow( table, id ) {
    for( r in table.rows ) {
      if( table.rows[r].id == id ) {
        return table.rows[r];
      }
    }
    return {};
  }

  for( var t in db ) {
    var table = db[t];
    table.maxId = 0;
    for( var r in table.rows ) {
      if( table.rows[r].id > table.maxId ) {
        table.maxId = table.rows[r].id;
      }
      for( var d in table.defaults ) {
        if( !isDef(table.rows[r][d]) ) {
          table.rows[r][d] = table.defaults[d];
        }
      }
    }
  }

  function wrapPat( pattern ) {
    return '^' + regexesc(apiUrl) + pattern + '\/*(\\?.*)*$'
  }

  var listPat = '\\/([a-z_][a-z_]*)';
  var itemPat = '\\/([a-z_][a-z_]*)\\/([^?\\/]*)';

  var listRegex = new RegExp( wrapPat(listPat) );
  var itemRegex = new RegExp( wrapPat(itemPat) );
  var cfgSettingsRegex = new RegExp( wrapPat(itemPat+'\\/settings') );
  var cfgDiscardRegex = new RegExp( wrapPat(itemPat+'\\/discard') );
  var cfgCommitRegex = new RegExp( wrapPat(itemPat+'\\/commit') );
  var cfgApproveRegex = new RegExp( wrapPat(itemPat+'\\/approve') );
  var cfgPublishRegex = new RegExp( wrapPat(itemPat+'\\/publish') );
  var currUserRegex = new RegExp( wrapPat('\\/currentuser') );

  $httpBackend.whenGET(/\.html$/).passThrough();

  $httpBackend.whenGET(currUserRegex).respond( function( method, url, data ) {
    return [200, db.user.rows[0], {}];
  });

  $httpBackend.whenGET(cfgSettingsRegex).respond( function( method, url, data ) {
    var urlData = cfgSettingsRegex.exec(url);
    var table = urlData[1];
    var id = urlData[2];
    var verRows = db[table].rows;
    var ver = findRow( verRows, {id:id} );
    if( ver ) {
      if( db[table].calc ) {
        db[table].calc( ver );
      }
      ver = copyFields( ver );
      var currVer = ver;
      var currDest = ver;
      while( currVer ) {
        currDest.id = currVer.id;
        var currCfg = findRow( db.config_set.rows, {id:currVer.config_set_id} );
        currDest.config_set_id = currCfg.id;
        currDest.hwtype = currCfg.hwtype;
        currDest.carrier = currCfg.carrier;
        currDest.region = currCfg.region;
        currDest.settings = copyFields( findRow( db.config_version_settings.rows, {version_id:currVer.id} ).settings );
        if( currVer.fallback_id ) {
          currVer = findRow( verRows, {id:currVer.fallback_id} );
          currDest.fallback = {};
          currDest = currDest.fallback;
        }
        else {
          currVer = null;
        }
      }
      return [200, ver, {}];
    }
    return [404, {}, {}];
  });

  $httpBackend.whenPUT(cfgSettingsRegex).respond( function( method, url, data ) {
    var urlData = cfgSettingsRegex.exec(url);
    var id = urlData[2];

    var cfgVer = findRow( db.config_version.rows, {id:id} );
    cfgVer.last_editor_id = 1;
    cfgVer.last_edited = formatDate( new Date() );

    var rows = db.config_version_settings.rows;
    for( var r in rows ) {
      if( rows[r] && rows[r].version_id == id ) {
        rows[r].settings = angular.fromJson(data).settings;
        return [200, {}, {}];
      }
    }
    return [404, {}, {}];
  });

  $httpBackend.whenPUT(cfgDiscardRegex).respond( function( method, url, data ) {
    var urlData = cfgDiscardRegex.exec(url);
    var id = urlData[2];

    var cfgVer = findRow( db.config_version.rows, {id:id} );
    cfgVer.last_editor_id = null;
    cfgVer.last_edited = null;
    var oldVer = findRow( db.config_version.rows, {
      config_set_id: cfgVer.config_set_id,
      version_number: cfgVer.version_number-1 } );

    var verSettings = findRow( db.config_version_settings.rows, { version_id: id } );
    var oldSettings = findRow( db.config_version_settings.rows, { version_id: oldVer.id } );
    if( verSettings ) {
      verSettings.settings = copyFields( oldSettings.settings );
      return [200, {}, {}];
    }

    return [404, {}, {}];
  });

  $httpBackend.whenPUT(cfgCommitRegex).respond( function( method, url, data ) {
    var urlData = cfgCommitRegex.exec(url);
    var id = urlData[2];

    var cfgVer = findRow( db.config_version.rows, {id:id} );
    if( !cfgVer ) {
      return [404, {}, {}];
    }
    var cfgSettings = findRow( db.config_version_settings.rows, {version_id:id} );
    if( !cfgVer ) {
      return [503, {}, {}];
    }

    var newVer = copyFields( cfgVer );
    newVer.id = ++db.config_version.maxId;
    newVer.version_number += 1;
    newVer.last_editor = newVer.last_edited = undefined;
    cfgVer.committer_id = 1;
    cfgVer.committed = formatDate( new Date() );
    db.config_version.rows.push( newVer );

    var newSettings = copyFields( cfgSettings );
    newSettings.id = ++db.config_version_settings.maxId;
    newSettings.version_id = newVer.id;
    db.config_version_settings.rows.push( newSettings );

    return [200, {}, {}];
  });

  $httpBackend.whenPUT(cfgApproveRegex).respond( function( method, url, data ) {
    var urlData = cfgApproveRegex.exec(url);
    var id = urlData[2];

    var cfgVer = findRow( db.config_version.rows, {id:id} );
    if( !cfgVer ) {
      return [404, {}, {}];
    }

    var verRows = db.config_version.rows;
    var preVer = null;
    var preVerNum = -1;
    for( var r in verRows ) {
      if( verRows[r] && verRows[r].config_set_id == cfgVer.config_set_id &&
          verRows[r].approved && verRows[r].version_number > preVerNum ) {
        preVer = verRows[r];
        preVerNum = preVer.version_number;
      }
    }
    if( preVer ) {
      for( var r in verRows ) {
        if( verRows[r] && !verRows[r].committed && verRows[r].fallback_id == preVer.id ) {
          verRows[r].fallback_id = cfgVer.id;
        }
      }
    }
    cfgVer.approver_id = 1;
    cfgVer.approved = formatDate( new Date() );

    return [200, {}, {}];
  });

  $httpBackend.whenPUT(cfgPublishRegex).respond( function( method, url, data ) {
    var urlData = cfgPublishRegex.exec(url);
    var id = urlData[2];

    var cfgVer = findRow( db.config_version.rows, {id:id} );
    if( !cfgVer ) {
      return [404, {}, {}];
    }

    cfgVer.publisher_id = 1;
    cfgVer.published = formatDate( new Date() );

    return [200, {}, {}];
  });

  $httpBackend.whenGET(listRegex).respond( function( method, url, data ) {
    //console.log( 'QUERY: ' + url );
    var urlData = listRegex.exec(url);
    var table = urlData[1];
    if( table ) {
      var params = parseUrlParams( url );
      var result = [];
      var rows = db[table].rows;
      for( var r in rows ) {
        if( rows[r] && matchesFilter( rows[r], params ) ) {
          if( db[table].calc ) {
            db[table].calc( rows[r] );
          }
          result.push( rows[r] );
        }
      }
      return [200, result, {}];
    }
    return [404, {}, {}];
  });
   
  $httpBackend.whenGET(itemRegex).respond( function( method, url, data ) {
    var urlData = itemRegex.exec(url);
    var table = urlData[1];
    var id = urlData[2];
    var rows = db[table].rows;
    for( var r in rows ) {
      if( rows[r] && rows[r].id == id ) {
        if( db[table].calc ) {
          db[table].calc( rows[r] );
        }
        return [200, rows[r], {}];
      }
    }
    return [404, {}, {}];
  });

  function addRow( table, values ) {
    var item = {};
    var defaults = db[table].defaults;
    for( k in defaults ) {
      item[k] = defaults[k];
    }
    for( var k in values ) {
      item[k] = values[k];
    }
    item.id = ++db[table].maxId;
    if( db[table].calc ) {
      db[table].calc( item );
    }
    db[table].rows.push( item );
    if( table == 'config_set' ) {
      var verRows = db.config_version.rows;
      var verFallback = { version_number: -1 };
      for( var r in verRows ) {
        if( verRows[r].config_set_id == item.fallback_id && verRows[r].approved ) {
          if( verRows[r].version_number > verFallback.version_number ) {
            verFallback = verRows[r];
          }
        }
      }
      var ver1 = { config_set_id: item.id, fallback_id: verFallback.id, version_number: 1 };
      ver1.committer_id = 1;
      ver1.committed = formatDate( new Date() );
      ver1.approver_id = 1;
      ver1.approved = formatDate( new Date() );
      ver1 = addRow( 'config_version', ver1 );
      addRow( 'config_version_settings', { version_id:ver1.id, settings: {} } );
      var ver2 = { config_set_id: item.id, fallback_id: verFallback.id, version_number: 2 };
      ver2 = addRow( 'config_version', ver2 );
      addRow( 'config_version_settings', { version_id:ver2.id, settings: {} } );
    }
    return item;
  }

  $httpBackend.whenPOST(listRegex).respond( function (method, url, data ) {
    //alert( 'NEW: ' + url );
    var urlData = listRegex.exec(url);
    var table = urlData[1];
    if( table ) {
      var values = angular.fromJson( data );
      var item = addRow( table, values );
      return [200, item, {}];
    }
    return [404, {}, {}];
  });

  $httpBackend.whenPUT(itemRegex).respond( function( method, url, data ) {
    //alert( 'SAVE: ' + url );
    var urlData = itemRegex.exec(url);
    var table = urlData[1];
    var id = urlData[2];
    var rows = db[table].rows;
    for( var r in rows ) {
      if( rows[r] && rows[r].id == id ) {
        rows[r] = angular.fromJson(data);
        return [200, rows[r], {}];
      }
    }
    return [404, {}, {}];
  });

  $httpBackend.whenDELETE(itemRegex).respond( function( method, url, data ) {
    var urlData = itemRegex.exec(url);
    var table = urlData[1];
    var id = urlData[2];
    var rows = db[table].rows
    for( var r in rows ) {
      if( rows[r] && rows[r].id == id ) {
        rows[r] = null;
        return [200, rows[r], {}];
      }
    }
    return [404, {}, {}];
  });

});


function matchesFilter( hash, filter )
{
  for( var f in filter ) if(has(filter,f))
  {
    var filterparts = f.split( '.', 2 );
    var op = filterparts[0];
    var k = filterparts[1];
    var val = hash[k];
    var fval = filter[f];
    //alert( '[' + op + '|' + k + '|' + val + '|' + fval + ']' );
    if( typeof val === 'number' ) {
      if( op == 'like' || op == 'nlike' ) {
        val = val.toString();
      }
      else {
        fval = parseFloat( fval );
      }
    }
    switch( op ) {
      case 'eq':
        if( val != fval )
          return false;
        break;
      case 'ne':
        if( val == fval )
          return false;
        break;
      case 'gt':
        if( val <= fval )
          return false;
        break;
      case 'lt':
        if( val >= fval )
          return false;
        break;
      case 'ge':
        if( val < fval )
          return false;
        break;
      case 'le':
        if( val > fval )
          return false;
        break;
      case 'like':
        if( isNil(val) || val.indexOf(fval) < 0 )
          return false;
        break;
      case 'nlike':
        if( !isNil(val) && val.indexOf(fval) >= 0 )
          return false;
        break;
      case 'nul':
        if( toBool(fval) != isNil(val) )
          return false;
        break;
    }
  }
  return true;
}

function parseUrlParams( url, result )
{
    if( isNil(url) )
        url = window.location.href;
    if( isNil(result) )
        result = {};

    var params = url.split( /[?&]/ );
    for( var p=0; p < params.length; ++p )
    {
        var name_val = params[p].split( '=', 2 );
        if( name_val.length == 2 )
        {
            var name = name_val[0].replace(/\+/g, ' ');  // Why does decodeURIComponent not handle this?
            name = decodeURIComponent( name );
            var val = name_val[1].replace(/\+/g, ' ');  // Why does decodeURIComponent not handle this?
            val = decodeURIComponent( val );
            result[name] = val;
        }
    }
    return result;
}

function formatDate( date ) {
  return date.getUTCFullYear() + '-' + padLeft( date.getUTCMonth()+1, 2, '0' ) + '-' +
    padLeft( date.getUTCDate(), 2, '0' ) + ' ' + padLeft( date.getUTCHours(), 2, '0' ) + ':' +
    padLeft( date.getUTCMinutes(), 2, '0' ) + ':' + padLeft( date.getUTCSeconds(), 2, '0' ) + 'Z';
}


