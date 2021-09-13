
// TODO: Give error if someone tries to access a devicetype config as though it were a carrier config, etc.

inputTypes = { bool:'checkbox' };

dispValues = { bool: {'true':'X','false':''} };
/**
 * A class representing definition for a single field/ in table.
 * @param initData data that you want to initialize field with. Name value pair.
 *    Initial content of new field object is clone of init data.
 */
function Field(initData) {
  for( var k in initData ) {
    this[k] = initData[k];
  }
}
/**
 * This is function on field class to tell about the field if it is ref or text.
 * It identifies the basic informaiton about the input field (if it is dropdown,
 * text or some thing else) so that UI can render this field accordingly.
 */
Field.prototype.inputType = function() {
  if( this.ref ) {
    return 'ref';
  }
  return inputTypes[this.type] || 'text';
};

/**
 * Display data for a field. Each field handles its display value. It can get
 * it from some other table or it may be based on some special logic. For
 * example if it is reference we have to lookup some other table.
 */
Field.prototype.dispVal = function(item) {
  var val = item[this.name];
  if( isNil(val) ) {
    return val;
  }
  var dispValue = lookup( dispValues, [this.type, val.toString()] );
  if( dispValue !== undefined )
    val = dispValue;
  return val;
};

/**
 * Legitimate values allowed for a field. Gives you a list of values from
 * referenced table.
 */
Field.prototype.valList = function() {
  return BasicTable.query({ '_table': this.ref });
};

/**
 * Defines whether to show field on a given page.
 * {mode} is something like 'view' or 'edit'. {page} is an
 * optional more specific value like 'list'. Rightnow page is only used for
 * list view.
 */
Field.prototype.showFor = function( mode, page ) {
  page = page || mode;
  if( this.hide )
    return false;
  if( this.hideFor && this.hideFor[page] )
    return false;
  return true;
};

/**
 * Which column you want to uniquely identify for lookup in database. This has
 * to match the API call. Whatever column API supports same column should be
 * used. For example: configset table finds the carrier information by doing
 * lookup using the "code" column.
 */
Field.prototype.getRefCol = function() {
  return this.refCol || 'id';
};

tableDefs = {

  extra_key : {
      dispName: 'Extra Key',
      itemName: function(d){return d.code},
      fieldList: [
          new Field({ name : 'code' , disp: 'Extra key code', lock: 1, req: 1}),
          new Field({ name : 'name' , disp: 'Extra key name'}),
          new Field({ name : 'comment' , disp: 'Comment'})
      ]
  },

  extra_value : {
      dispName: 'Extra Value',
      itemName: function(d){return d.name},
      fieldList: [
          new Field({ name:'extra_key_id',
                      disp:'Extra Key',
                      lock:1,
                      req:1,
                      filterKey:'like.extra_key_id.name',
                      ref:'extra_key' }),
          new Field({ name:'value', disp: 'Value'}),
          new Field({ name:'name', disp: 'Name'}),
          new Field({ name:'comment', disp: 'Comment'})
      ]
  },

  hwtype: { dispName: 'HW Type', itemName: function(d){ return d.code },
    fieldList: [
      new Field({ name:'code', disp:'Code', lock:1, req:1 }),
      new Field({ name:'internal_name', disp:'Internal Name' }),
      new Field({ name:'marketing_name', disp:'Marketing Name' }),
      new Field({ name:'comment', disp:'Comment' })
    ]
  },

  carrier: { dispName: 'Carrier', itemName: function(d){ return d.code },
    fieldList: [
      // Removing lock so that code can be eidted.
      //new Field({ name:'code', disp:'Code', lock:1, req:1 }),
      new Field({ name:'code', disp:'Code', req:1 }),
      new Field({ name:'name', disp:'Name' }),
      new Field({ name:'comment', disp:'Comment' }),
      new Field({ name:'old_code', disp:'Old Code' })
    ]
  },

  region: { dispName: 'Region', itemName: function(d){ return d.code },
    fieldList: [
      new Field({ name:'code', disp:'Country Code', lock:1, req:1 }),
      new Field({ name:'name', disp:'Name' }),
      new Field({ name:'comment', disp:'Comment' })
    ]
  },

  user: { dispName: 'User', itemName: function(d){ return d.username },
    fieldList: [
      new Field({ name:'username', disp:'Username', lock:1, req:1 }),
      new Field({ name:'email', disp:'Email Address' }),
      new Field({ name:'display_name', disp:'Display Name' }),
      new Field({ name:'editor', disp:'Editor', type:'bool' }),
      new Field({ name:'approver', disp:'Approver', type:'bool' }),
      new Field({ name:'publisher', disp:'Publisher', type:'bool' }),
      new Field({ name:'admin', disp:'Admin', type:'bool' }),
      new Field({ name:'manager', disp:'Manager', type:'bool' }),
    ]
  },

  setting_category: { dispName: 'Setting Category', itemName: function(d){ return d.name },
    fieldList: [
      new Field({ name:'name', disp:'Name', lock:1, req:1 }),
      new Field({ name:'comment', disp:'Comment' })
    ]
  },

  setting_def: { dispName: 'Setting Definition', itemName: function(d){ return d.name },
    fieldList: [
      new Field({ name:'category_id', disp:'Category', lock:1, req:1,
        filterKey:'like.category_id.name', ref:'setting_category' }),
      new Field({ name:'name', disp:'Name', lock:1, req:1 }),
      new Field({ name:'group', disp:'Group' }),
      new Field({ name:'order', disp:'Ordering Number', type:'int' }),
      new Field({ name:'datatype', disp:'Data Type', req:1 }),
      new Field({ name:'rules', disp:'Rules' }),
      new Field({ name:'display_name', disp:'Display Name' }),
      new Field({ name:'short_help', disp:'Short Help' })
    ]
  },

  cloud_env: { dispName: 'Cloud Environment',
    itemName: function(d){ return d.short_name },
    fieldList: [
      new Field({ name:'order', disp:'Ordering Number', type:'int' }),
      new Field({ name:'short_name', disp:'Short Name', req:1 }),
      new Field({ name:'display_name', disp:'Display Name', req:1 }),
      new Field({ name:'network_name', disp:'Network Name', req:1 }),
      new Field({ name:'env_type', disp:'Environment Type', req:1 }),
      new Field({ name:'comment', disp:'Comment' })
    ]
  },

  env_transform: { dispName: 'Environment Transform',
    itemName: function(d){ return 'Transform[' + d.id + ']' },
    fieldList: [
      new Field({ name:'order', disp:'Ordering Number', req:1, type:'int' }),
      new Field({ name:'env_pat', disp:'Env Regex', req:1, val:'^(qa|sdc).*' }),
      new Field({ name:'extra_level_pat', disp:'ExtraKey.ExtraValueName Regex', req:1, val:'.*' }),
      new Field({ name:'hwtype_pat', disp:'HW Type Regex', req:1, val:'.*' }),
      new Field({ name:'carrier_region_pat', disp:'Carrier.Region Regex', req:1, val:'.*' }),
      new Field({ name:'setting_name_pat', disp:'Setting Name Regex', req:1 }),
      new Field({ name:'value_pat', disp:'Value Replace Regex', req:1 }),
      new Field({ name:'value_sub', disp:'Value Replacement' }),
      new Field({ name:'comment', disp:'Comment' })
    ]
  },

  config_set: {
      dispName: 'Config Set',
      itemName: function( d, noCategory ) {
        if( !d ) {
            return '';
        }
        var name = 'Global Defaults';
        if( d.carrier || d.region )
            name = d.carrier + '.' + d.region;
        if( d.hwtype )
            name = d.hwtype + '.' + name;
        if( d.extra_value) {
            name = d.extra_key + ':' + d.extra_value + '.' + name;
        } else if( d.delta_name ) {
            name = d.delta_name;
        }
        if( noCategory ) {
            return name;
        }
        return name + ' (' + (d.category_name||d.category_id) + ')';
      },
    fieldList: [
      new Field({ name:'category_id', disp:'Category', lock:1, req:1, ref:'setting_category' }),
      new Field({ name:'extra_value', disp:'Extra Value', lock:1, ref:'extra_value', refCol:'value', nullDisp:'-- none --'}),
      new Field({ name:'hwtype', disp:'HW Type', lock:1, ref:'hwtype', refCol:'code', nullDisp:'*' }),
      new Field({ name:'carrier', disp:'Carrier', lock:1, ref:'carrier', refCol:'code', nullDisp:'*' }),
      new Field({ name:'region', disp:'Region', lock:1, ref:'region', refCol:'code', nullDisp:'*' }),
      new Field({ name:'fallback_id', disp:'Parent Config', lock:1, ref:'config_set', nullDisp:'-- none --' }),
      new Field({ name:'comment', disp:'Comment' }),
      new Field({ name:'delta_name', disp:'Delta Name' })
    ]
  },

  // A config superset gives a way to create all the necessary config sets
  // for a given hwtype+carrier+region and extra level. The concept is not used outside of
  // that creation process. The following section defines the parts of the
  // config superset that follow normal rules. The more specific behavior
  // is in CfgSupersetCtrl.
  cfg_superset: { table: 'config_set', dispName: 'Instantiate All Configs for a Devicetype',
    itemName: function( d, noCategory ) {
      return tableDefs.config_set.itemName( d, noCategory );
    },

    itemDesc: function(d) {
      return 'This page allows you to create the necessary config sets ' +
        'for a devicetype all at once. This includes the config sets ' +
        'for each category as well as parent (carrier) config sets ' +
        'where needed. You can also specify which clouds to publish ' +
        'the initial settings to.';
    },

    fieldList: [
      new Field({ name:'extra_key', disp:'Extra Key', lock:1, ref:'extra_key', refCol:'code', nullDisp:'-- none --'}),
      new Field({ name:'extra_value_id', disp: 'Extra Value Name', lock:1, ref:'extra_value', refCol:'id', filterKey:'like.extra_value_id.name', nullDisp:'-- none --',
       filterRef: function(item, list){
            var result = [];
            for (i in list) {
                if (list[i].extra_key_code == item.extra_key) {
                    result.push(list[i]);
                }
            }
            return result;
        }
      }),
      new Field({ name:'hwtype', disp:'HW Type', lock:1, ref:'hwtype', refCol:'code', nullDisp:'-- none --' }),
      new Field({ name:'carrier', disp:'Carrier', lock:1, ref:'carrier', refCol:'code', nullDisp:'-- none --' }),
      new Field({ name:'region', disp:'Region', lock:1, ref:'region', refCol:'code', nullDisp:'-- none --' }),
      new Field({ name:'comment', disp:'Comment' })
    ]
  },

  cfg_global: { table: 'config_set', dispName: 'Global Config', dispPrefix: 'Config',
    itemName: function(d) {
      return 'Global Defaults (' + (d.category_name || d.category_id) + ')';
    },
    itemTip: function(d) {
        return 'This config set holds default values for the "'
            + d.category_name + '" settings category.';
    },
    filter: { 'nul.hwtype': 1, 'nul.carrier': 1, 'nul.region': 1, 'nul.delta_name':1 },
    fieldList: [
      new Field({ name:'category_id', disp:'Category', lock:1, req:1,
        filterKey:'like.category_id.name', ref:'setting_category' }),
      new Field({ name:'comment', disp:'Comment' })
    ]
  },

  cfg_carrier: { table: 'config_set', dispName: 'Carrier Config', dispPrefix: 'Config',
    itemName: function(d) {
        return d.carrier + '.' + d.region + ' (' + (d.category_name || d.category_id) + ')';
    },
    itemTip: function(d) {
        return 'This config set holds "' + d.category_name +
            '" settings for the carrier "' +
            d.carrier + '.' + d.region + '".';
    },
    filter: { 'nul.hwtype': 1, 'nul.carrier': 0, 'nul.region': 0, 'nul.delta_name':1 },
    prepForSave: function( item, tables ) {
      var parent = findRow( tables.cfg_global, {id:item.fallback_id} );
      if( item.category_id != parent.category_id ) {
        return "The specified Category and Parent Config category do not match.";
      }
    },
    fieldList: [
      new Field({ name:'category_id', disp:'Category', lock:1, req:1,
        filterKey:'like.category_id.name', ref:'setting_category' }),
      new Field({ name:'carrier', disp:'Carrier', lock:1, req:1, ref:'carrier', refCol:'code' }),
      new Field({ name:'region', disp:'Region', lock:1, req:1, ref:'region', refCol:'code' }),
      new Field({ name:'fallback_id', disp:'Parent Config', lock:1, req:1, hideFor:{list:1},
        ref:'cfg_global',
        filterRef: function( item, list ) {
          var result = [];
          for( i in list ) {
            if( list[i].category_id == item.category_id ) {
              result.push( list[i] );
            }
          }
          return result;
        }
        }),
      new Field({ name:'comment', disp:'Comment' })
    ]
  },

  cfg_delta: { table: 'config_set', dispName: 'Delta Config', dispPrefix: 'Config',
    itemName: function(d) {
        return d.delta_name + ' (' + (d.category_name || d.category_id) + ')';
    },
    itemTip: function(d) {
        return 'This config set holds ' + d.category_name +
            ' settings for the delta config ' +
            d.delta_name + '.';
    },
    filter: { 'nul.hwtype': 1, 'nul.carrier': 1, 'nul.region': 1, 'nul.delta_name': 0 },
    prepForSave: function( item, tables ) {
      var parent = findRow( tables.cfg_global, {id:item.fallback_id} );
      if( item.category_id != parent.category_id ) {
        return "The specified Category and Parent Config category do not match.";
      }
    },
    fieldList: [
      new Field({ name:'category_id', disp:'Category', lock:1, req:1,
        filterKey:'like.category_id.name', ref:'setting_category' }),
      new Field({name: 'delta_name', disp:'Delta Config', req:1}),
      //new Field({ name:'delta', disp:'Delta', lock:1, req:1, ref:'delta', refCol:'name' }),
      new Field({ name:'fallback_id', disp:'Parent Config', lock:1, req:1, hideFor:{list:1},
        ref:'cfg_global',
        filterRef: function( item, list ) {
          var result = [];
          for( i in list ) {
            if( list[i].category_id == item.category_id ) {
              result.push( list[i] );
            }
          }
          return result;
        }
        }),
      new Field({ name:'comment', disp:'Comment' })
    ]
  },

  cfg_devicetype: { table: 'config_set', dispName: 'DeviceType Config', dispPrefix: 'Config',
    canPublish: true,

    itemName: function(d) {
        name = '';
        if (d.extra_value) {
            name += d.extra_key + ':' + d.extra_value + '.';
        }
        name += d.hwtype + '.' + d.carrier + '.' + d.region + ' (' + d.category_name + ')';
        return name;
    },

    itemTip: function(d) {
        return 'This config set holds "' + d.category_name + '" settings for the devicetype "' + d.hwtype + '.' + d.carrier + '.' + d.region + '".';
    },

    filter: { 'nul.hwtype': 0, 'nul.carrier': 0, 'nul.region': 0 },

    prepForSave: function( item, tables ) {
      var parent = findRow( tables.config_set, {id:item.fallback_id} );
      if( item.category_id != parent.category_id ) {
        return "The specified Category and Parent Config category do not match.";
      }
      if (!parent.delta_name) {
        item.carrier = parent.carrier;
        item.region = parent.region;
      }
    },

    fieldList: [
      new Field({ name:'category_id', disp:'Category', lock:1, req:1,filterKey:'like.category_id.name', ref:'setting_category' }),
      new Field({ name:'hwtype', disp:'HW Type', lock:1, req:1, ref:'hwtype', refCol:'code' }),
      new Field({ name:'carrier', disp:'Carrier', lock:1, ref:'carrier', refCol:'code' }),
      new Field({ name:'region', disp:'Region', lock:1, ref:'region', refCol:'code' }),
      new Field({ name:'extra_key', disp:'Extra Key', lock:1, ref:'extra_key', refCol:'code', filterKey:'like.extra_key', nullDisp:'-- none --'}),

      new Field({ name:'extra_value_id', disp: 'Extra Value Name', lock:1, ref:'extra_value', refCol:'id', filterKey:'like.extra_value_id.name', nullDisp:'-- none --',
       filterRef: function(item, list){
            var result = [];
            for (i in list) {
                if (list[i].extra_key_code == item.extra_key) {
                    result.push(list[i]);
                }
            }
            return result;
        }
      }),

      new Field({ name:'fallback_id', disp:'Parent Config', lock:0, req:1, hideFor:{list:1},
          ref:'config_set',
          filterRef: function( item, list ) {
            var result = [];
            if(item.category_id) {
              this.nullDisp = 'filtering..';
              for( i in list ) {
                if((list[i].category_id == item.category_id ) && ((list[i].delta_name) || (!list[i].hwtype && list[i].carrier)) ) {
                  result.push( list[i] );
                }
              }
            }
            if (result.length > 0) {
               this.nullDisp = null;
            }
            return result;
          }
      }),

      new Field({ name:'comment', disp:'Comment' })
    ]
  },

  config_version: { dispName: 'Config Version',
    itemName: function(d) {
      return 'Config[' + d.config_set_id + '] v' + d.version_number;
    },
    versionName: function(d) {
      var result = 'v.' + d.version_number;
      if( !d.committed ) {
        result = 'uncommitted' + ( d.last_edited ? ' edits' : '' );
      }
      else if( d.published ) {
        result += ' - published';
      }
      else if( d.approved ) {
        result += ' - approved';
      }
      return result + '\u00A0';
    },
    fieldList: [
      new Field({ name:'config_set_id', disp:'Config Set', lock:1, req:1, ref:'config_set' }),
      new Field({ name:'fallback_id', disp:'Fallback', ref:'config_version', nullDisp:'-- none --' }),
      new Field({ name:'version_number', disp:'Version Number', lock:1, req:1, type:'int' }),
      new Field({ name:'comment', disp:'Comment' }),
      new Field({ name:'last_edited', disp:'Last\u00A0Edit At', nullDisp:'-- none --' }),
      new Field({ name:'last_editor', disp:'Last\u00A0Edit By', ref:'user', refCol:'username', nullDisp:'-- none --' }),
      new Field({ name:'committed', disp:'Commit At', nullDisp:'-- none --' }),
      new Field({ name:'committer', disp:'Commit By', ref:'user', refCol:'username', nullDisp:'-- none --' }),
      new Field({ name:'approved', disp:'Approve At', nullDisp:'-- none --' }),
      new Field({ name:'approver', disp:'Approve By', ref:'user', refCol:'username', nullDisp:'-- none --' }),
      new Field({ name:'published', disp:'Publish At', nullDisp:'-- none --' }),
      new Field({ name:'publisher', disp:'Publish By', ref:'user', refCol:'username', nullDisp:'-- none --' })
    ]
  }

}

for( var t in tableDefs ) {
  var tableDef = tableDefs[t];
  tableDef.fieldMap = {};
  for( var f in tableDef.fieldList ) {
    var field = tableDef.fieldList[f];
    tableDef.fieldMap[field.name] = field;
  }
}
