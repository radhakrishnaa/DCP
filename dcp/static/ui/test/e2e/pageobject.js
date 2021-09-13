
var SPACEPAT = '[ \u00A0]';
var WSPAT = '[\t\n \u00A0]';
var ANYPAT = '[^]';

var VALTAG_NOVALUE = 'novalue';
var VALTAG_GLOBAL = 'global';
var VALTAG_INHERIT = 'inherit';
var VALTAG_SPECIFIC = 'specific';

var VERSION_UNCHANGED = '';
var VERSION_EDITED = 'edited';
var VERSION_PARENT_CHANGED = 'parent';

var VERSION_NOT_LATEST = '';
var VERSION_LATEST_COMMITTED = 'latest';


var Helper = function( scen ) {
  var helper = this;
  this.scen = scen;
  this.currModelName = null;
  this.confirmText = null;
  this.confirmResult = null;

  this.scen.addFutureAction( 'set mock', function($window, $document, done) {
    $window.confirm = function( text ) {
      if( isNil(helper.confirmResult) ) {
        throw 'No result specified for the confirmation dialog asking... ' + text;
      }
      var result = helper.confirmResult;
      helper.confirmResult = null;
      helper.confirmText = text;
      return result;
    };
    done();
  });
};

Helper.prototype.setConfirmResult = function( result ) {
  var helper = this;
  return this.scen.addFuture( 'confirm result', function(done) {
    helper.confirmResult = result;
    helper.confirmText = null;
    done();
  });
};

Helper.prototype.expectConfirm = function() {
  var helper = this;
  return expect(this.scen.addFuture( 'confirm text', function(done) {
    done( null, helper.confirmText );
  }));
};


Helper.prototype.print = function( text ) {
  return expect(this.scen.addFuture( text, function(done) {
    done();
  }));
};


////////////////////////////////////////////////////////////
// List Page

Helper.prototype.setCurrModelName = function( modelName ) {
  this.currModelName = modelName;
};

Helper.prototype.gotoListPage = function( modelName, viaHomeLink ) {
  this.currModelName = modelName;
  var linkUrl = '#/'+this.currModelName+'/list';
  if( viaHomeLink ) {
    expect(element('a:visible:contains('+viaHomeLink+')').attr('href')).
      toEqual(linkUrl);

    element('a:visible:contains('+viaHomeLink+')').click();
  }
  else {
    browser().navigateTo( linkUrl );
  }

  this.assertListPage();
};

Helper.prototype.assertListPage = function() {
  expect(browser().location().path()).
    toEqual( '/'+this.currModelName+'/list' );
};

Helper.prototype.findInList = function( textList, selectorSuffix ) {
  var selector = 'tbody tr:visible';
  for( var t in textList ) {
    selector += ':contains(' + textList[t] + ')';
  }
  selector += selectorSuffix ? selectorSuffix : '';
  return element(selector);
};

Helper.ListItemObj = function( helper, textList ) {
  this.assertCount = function( count ) {
    expect( helper.findInList(textList).count() ).toEqual( count );
  };

  this.assertPresent = function() {
    this.assertCount( 1 );
  };

  this.assertAbsent = function() {
    this.assertCount( 0 );
  };

  this.assertPresence = function( presence ) {
    return presence ? this.assertPresent() : this.assertAbsent();
  }

  this.click = function() {
    this.assertPresent();
    helper.findInList( textList, ' a:first-child' ).click();
  };
};

Helper.prototype.forListItem = function( textArray ) {
  return new Helper.ListItemObj( this, textArray );
};

////////////////////////////////////////////////////////////
// Detail Page

Helper.prototype.assertDetailPage = function( headingText ) {
  expect(browser().location().path()).
    toMatch( '/'+this.currModelName+'/view/[^/]*' );
  expect(element('h1:visible:first').text()).
    toContain( headingText );
};


////////////////////////////////////////////////////////////
// Errors

Helper.ErrorMsgObj = function() {
  this.elem = element('.error_status_area:visible, .errorMsg:visible');

  this.assertPresent = function() {
    expect( this.elem.count() ).toBeGreaterThan( 0 );
  }

  this.assertAbsent = function() {
    expect( this.elem.count() ).toEqual( 0 );
  }

  this.assertPresence = function( presence ) {
    return presence ? this.assertPresent() : this.assertAbsent();
  }
};

Helper.prototype.forErrorMsg = function() {
  return new Helper.ErrorMsgObj();
};

////////////////////////////////////////////////////////////
// Actions (Buttons/Links)

Helper.ActionObj = function( selector, checks ) {
  this.selector = selector;
  this.checks = checks;
  this.elem = element(selector);
};
{
  var proto = Helper.ActionObj.prototype;

  proto.assertAbsent = function() {
    expect( this.elem.count() ).toEqual( 0 );
  };

  proto.assertPresent = function() {
    expect( this.elem.count() ).toEqual( 1 );
    if( !isNil(this.checks.href) ) {
      expect( this.elem.attr('href') ).toEqual( this.checks.href );
    }
    if( !isNil(this.checks.text) ) {
      expect( this.elem.text() ).
        toMatch( '^'+WSPAT+'*' + regexesc(this.checks.text) + WSPAT+'*$' );
    }
  };

  proto.assertPresence = function( presence ) {
    return presence ? this.assertPresent() : this.assertAbsent();
  }

  proto.click = function() {
    this.assertPresent();
    this.elem.click();
  };
}

Helper.prototype.forAction = function( selector, checks ) {
  return new Helper.ActionObj( selector, checks );
};

Helper.prototype.forNew = function() {
  return this.forAction( 'h1 a.link_new:visible', {
    href: '#/'+this.currModelName+'/new'
  } );
};

Helper.prototype.forApply = function() {
  return this.forAction( '.actions input[name=apply]:visible', {} );
};

Helper.prototype.forCancel = function() {
  return this.forAction( '.actions a.cancel:visible', {} );
};

Helper.prototype.forDelete = function() {
  var helper = this;
  var actionObj = this.forAction( 'h1 a.link_del:visible', {
    text: 'Delete'
  } );
  actionObj.superClick = Helper.ActionObj.prototype.click;
  actionObj.click = function( confirmChoice, expectedConfirmText ) {
    helper.setConfirmResult( confirmChoice );
    this.superClick();
    if( expectedConfirmText ) {
      helper.expectConfirm().toContain( expectedConfirmText );
    }
  }
  return actionObj;
};

Helper.prototype.deleteItem = function( modelName, itemName, options ) {
  options = options || {};
  var expectConfirm = options.expectConfirm || '';
  var listRowContent = options.listRowContent || [itemName];

  this.gotoListPage( modelName );
  this.forListItem( listRowContent ).click();
  this.assertDetailPage( itemName );
  this.forDelete().click( true, 'Delete ' + expectConfirm );
  // In addition to catching errors. The following line seems to
  // prevent the Angular E2E system from getting ahead of itself
  // and continuing before the next page is opened.
  this.forErrorMsg().assertAbsent();
};


////////////////////////////////////////////////////////////
// Settings Versions

Helper.prototype.forVersionAction = function( action ) {
  return this.forAction( 'a.ver_'+action+':visible', {} );
};

Helper.prototype.forVersionEdit = function() {
  return this.forVersionAction( 'edit' );
};

Helper.prototype.forVersionCommit = function() {
  return this.forVersionAction( 'commit' );
};

Helper.prototype.forVersionDiscard = function() {
  return this.forVersionAction( 'discard' );
};

Helper.prototype.forVersionApprove = function() {
  return this.forVersionAction( 'approve' );
};

Helper.prototype.forVersionPublish = function() {
  return this.forVersionAction( 'publish' );
};

Helper.prototype.forVersionRepublish = function() {
  return this.forVersionAction( 'republish' );
};

Helper.prototype.forVersionTestPublish = function() {
  return this.forVersionAction( 'testpublish' );
};

Helper.prototype.buildVersionStr = function( vNum, tag ) {
  var verStr = '';
  if( vNum ) {
    verStr += 'v.' + vNum;
  }
  if( tag ) {
    verStr += verStr ? ' - ' : '';
    verStr += tag;
  }
  if( !isNil(tag) ) {
    verStr += '\u00A0';
  }
  return verStr;
}

Helper.prototype.findInVersionList = function( verNum, tag, onlySelected ) {
  var selector = 'select[ng-model="vars.verId"] option';
  if( onlySelected ) {
    selector += ':selected';
  }
  var verStr = this.buildVersionStr( verNum, tag );
  if( verStr ) {
    selector += ':contains(' + verStr + '):last';
  }
  return element(selector);
};

Helper.prototype.VersionObject = function( helper, verNum, options ) {
  options = options || {};
  var tag = options.tag;
  var onlySelected = options.onlySelected;

  this.click = function() {
    helper.findInVersionList( verNum, tag ).click();
  }

  this.assertPresence = function( presence ) {
    var elem = helper.findInVersionList( verNum, tag, onlySelected );
    if( presence ) {
      var matchStr = '^' + regexesc( helper.buildVersionStr( verNum, tag ) );
      matchStr += isNil(tag) ? '.*' : '$';
      expect( elem.text() ).toMatch( matchStr );
    }
    else {
      // TODO: Make this not fail due to false partial matches resulting from :contains().
      expect( elem.count() ).toEqual( 0 );
    }
  }

  this.assertPresent = function() {
    this.assertPresence( true );
  };

  this.assertAbsent = function() {
    this.assertPresence( false );
  };
};

Helper.prototype.forVersion = function( verNum, options ) {
  return new this.VersionObject( this, verNum, options );
}

Helper.prototype.assertVersionTags = function( verNum, tags ) {
  var baseSel = 'ul.version_info li:visible';
  if( verNum ) {
    expect(element(baseSel+':contains(Version '+verNum+')').text()).
      toMatch( '[ \t\n]*Version ' + verNum + '[ \t\n]*' )
  }
  else {
    expect(element(baseSel+':contains(Working Version)').text()).
      toMatch( '[ \t\n]*Working Version[ \t\n]*' )
  }
  var numTags = 0;
  for( var t in tags ) {
    ++numTags;
    var pat = null;
    if( t == 'Last edited' || t == 'Committed' || t == 'Approved' || t == 'Published' ) {
      pat = '[ \t\n]*' + t +
        ' \\d\\d\\d\\d-\\d\\d-\\d\\d \\d\\d:\\d\\d:\\d\\d \\+0000 by ' +
        ( tags[t] || '[^.]+' ) + '\\.[ \t\n]*';
    }
    else {
      pat = '[ \t\n]*' + regexesc(tags[t] || t) + '[ \t\n]*';
    }
    expect( element(baseSel+':contains('+t+')').text() ).
      toMatch( pat );
  }
  expect(element(baseSel).count()).
    toEqual( numTags + 1 )
}

Helper.prototype.assertUncommitted = function( edited ) {
  if( edited ) {
    if( edited == VERSION_PARENT_CHANGED ) {
      this.assertVersionTags( null, {'Parent changed since last commit.':''} );
    }
    else {
      this.assertVersionTags( null, {'Last edited':''} );
    }
  }
  else {
    this.assertVersionTags( null, {'No edits since last commit.':''} );
  }
  this.forVersionEdit().assertPresent();
  this.forVersionCommit().assertPresent();
  this.forVersionDiscard().assertPresence( edited == VERSION_EDITED );
  this.forVersionApprove().assertAbsent();
  this.forVersionPublish().assertAbsent();
  this.forVersionRepublish().assertAbsent();
  this.forVersionTestPublish().assertAbsent();
};

Helper.prototype.assertCommitted = function( expectedVerNum, isLatest ) {
  var publishable = this.currModelName == 'cfg_devicetype';
  this.assertVersionTags( expectedVerNum, {Committed:''} );
  this.forVersionEdit().assertPresence(isLatest);
  this.forVersionCommit().assertAbsent();
  this.forVersionDiscard().assertAbsent();
  this.forVersionApprove().assertPresent();
  this.forVersionPublish().assertAbsent();
  this.forVersionRepublish().assertAbsent();
  this.forVersionTestPublish().assertPresence( publishable );
};

Helper.prototype.assertApproved = function( expectedVerNum, isLatest ) {
  var publishable = this.currModelName == 'cfg_devicetype';
  this.assertVersionTags( expectedVerNum, {Committed:'',Approved:''} );
  this.forVersionEdit().assertPresence(isLatest);
  this.forVersionCommit().assertAbsent();
  this.forVersionDiscard().assertAbsent();
  this.forVersionApprove().assertAbsent();
  this.forVersionPublish().assertPresence( publishable );
  this.forVersionRepublish().assertAbsent();
  this.forVersionTestPublish().assertPresence( publishable );
};

Helper.prototype.assertPublished = function( expectedVerNum, isLatest ) {
  var publishable = this.currModelName == 'cfg_devicetype';
  this.assertVersionTags( expectedVerNum, {Committed:'',Approved:'',Published:''} );
  this.forVersionEdit().assertPresence(isLatest);
  this.forVersionCommit().assertAbsent();
  this.forVersionDiscard().assertAbsent();
  this.forVersionApprove().assertAbsent();
  this.forVersionPublish().assertAbsent();
  this.forVersionRepublish().assertPresence( publishable );
  this.forVersionTestPublish().assertPresence( publishable );
};

////////////////////////////////////////////////////////////
// Input Fields

Helper.InputFieldObj = function( selector, type, name ) {
  this.type = type;
  var baseSelector = '.fields tbody[data-name=' +
    formatAsName(name) + ']' + selector + ':visible';
  this.elem = using(baseSelector).element('input');
  this.input = using(baseSelector).input();
};
{
  var proto = Helper.InputFieldObj.prototype;

  proto.assertPresent = function() {
    expect( this.elem.count() ).toEqual( 1 );
  };

  proto.assertAbsent = function() {
    expect( this.elem.count() ).toEqual( 0 );
  };

  proto.assertPresence = function( presence ) {
    return presence ? this.assertPresent() : this.assertAbsent();
  }

  proto.click = function() {
    this.assertPresent();
    this.elem.click();
  };

  proto.enter = function( val ) {
    this.assertPresent();
    this.input.enter( val );
  };

  proto.val = function() {
    this.assertPresent();
    var futureVal = this.type != 'checkbox' ?
      this.input.val() : this.elem.prop('checked');
    return futureVal;
  };

  proto.expectVal = function() {
    return expect( this.val() );
  };
}

Helper.prototype.forInputField = function( selector, type, name ) {
  return new Helper.InputFieldObj( selector, type, name );
};

Helper.prototype.forTextField = function( name ) {
  return this.forInputField( ' td.valinput', 'text', name );
};

Helper.prototype.forOverrideCheckbox = function( name ) {
  return this.forInputField( ' td.override_check', 'checkbox', name );
};

Helper.SelectFieldObj = function( name ) {
  this.baseSelector = '.fields tbody[data-name=' +
    formatAsName(name) + '] td.valinput:visible';
  this.elem = using(this.baseSelector).element('select');
};
{
  var proto = Helper.SelectFieldObj.prototype;

  proto.assertPresent = function() {
    expect( this.elem.count() ).toEqual( 1 );
  };

  proto.assertAbsent = function() {
    expect( this.elem.count() ).toEqual( 0 );
  };

  proto.assertPresence = function( presence ) {
    return presence ? this.assertPresent() : this.assertAbsent();
  }

  proto.option = function( val ) {
    this.assertPresent();
    using(this.baseSelector).select().option( val );
  };

  proto.val = function() {
    this.assertPresent();
    return using(this.baseSelector).element('select option:selected').text();
  };

  proto.expectVal = function() {
    return expect( this.val() );
  };
}

Helper.prototype.forSelectField = function( name ) {
  return new Helper.SelectFieldObj( name );
};

Helper.prototype.assertSettingTag = function( fieldName, tagType, tagText ) {
  switch( tagType ) {
    case( VALTAG_NOVALUE ):
      tagText = '(no value)';
      break;
    case( VALTAG_GLOBAL ):
      tagText = 'from Global Defaults';
      break;
    case( VALTAG_INHERIT ):
      tagText = 'from ' + tagText;
      break;
    case( VALTAG_SPECIFIC ):
      tagText = tagText + ' specific';
      break;
  }
  expect( element( '.fields tbody[data-name=' +
    formatAsName(fieldName) + '] td.tag:visible' ).text() ).
    toMatch( '^' + WSPAT + '*' + regexesc(tagText) + WSPAT + '*$' );
};

Helper.SettingDisplayObj = function( name ) {
  var baseSelector = '.fields tbody[data-name=' +
    formatAsName(name) + '] .val:visible';
  this.elem = element( baseSelector );
};
{
  var proto = Helper.SettingDisplayObj.prototype;

  proto.assertPresent = function() {
    expect( this.elem.count() ).toEqual( 1 );
  };

  proto.assertAbsent = function() {
    expect( this.elem.count() ).toEqual( 0 );
  };

  proto.assertPresence = function( presence ) {
    return presence ? this.assertPresent() : this.assertAbsent();
  }

  proto.val = function() {
    this.assertPresent();
    return this.elem.text();
  };

  proto.expectVal = function() {
    return expect( this.val() );
  };
}

Helper.prototype.forSettingDisplay = function( name ) {
  return new Helper.SettingDisplayObj( name );
};


