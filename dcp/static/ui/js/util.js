

//////////////////////////////////////////////////////////////////////
//// Comparators
////

function isDef( val ) {
    return typeof(val) != 'undefined';
}

function isNil( val ) {
    return typeof(val) == 'undefined' || val === null;
}

function isEmpty( val ) {
    return isNil(val) || val.toString().length == 0;
}

function nonNil( val, fallback ) {
  if( isNil(val) ) {
    return fallback;
  }
  return val;
}

/*
 * Used because Angular does not supports ternary operator.
 */
function choose( cond, trueVal, falseVal ) {
  return cond ? trueVal : falseVal;
}

function compare( val1, val2 ) {
  // If value has a dot we want it to show up first in list as compared to value
  // without .
  if ((val1.indexOf(".") >= 0) && (val2.indexOf(".") < 0)){
    return 1;
  } 
  if ((val2.indexOf(".") >= 0) && (val1.indexOf(".") < 0) ) {
    return -1;
  }
  if( val1 > val2 ) {
    return 1;
  }
  if( val2 > val1 ) {
    return -1;
  }
  return 0;
}

function compareNoCase( val1, val2 ) {
  if( val1.toLowerCase ) {
    val1 = val1.toLowerCase();
  }
  if( val2.toLowerCase ) {
    val2 = val2.toLowerCase();
  }
	return compare( val1, val2 );
}

function toBool( val ) {
  if( !val ) {
    return false;
  }
  val = val.toString().toLowerCase();
  if( val == '0' || val == 'false' || val == 'off' ) {
    return false;
  }
  return true;
}

function getClass( obj ) {
  return Object.prototype.toString.call(obj)
    .match(/^\[object (.*)\]$/)[1];
}

function isA( obj, typeName ) {
  return Object.prototype.toString.call(obj) === '[object ' + typeName + ']';
}

//////////////////////////////////////////////////////////////////////
//// Hashes
////

// This function just makes the hasOwnProperty syntax a little shorter so it
// fits better as part of a for loop as follows...
//    for( var k in myhash ) if(has(myhash,k)) {
//        // do something
//    }
//
// It seems that most browsers do not return inherited function objects for
// "in" statements, which makes this unnecessary for those when using a base
// Object as a hash.
//
function has( hash, key ) {
    return hash.hasOwnProperty( key );
}

// This is more critical than the above function since most browsers do seem
// to return inherited function objects when using the index [] operator.
//
function getv( hash, key ) {
	if( hash && hash.hasOwnProperty( key ) )
		return hash[key];
	return undefined;
}

function hasValues( hash, filter ) {
  for( var f in filter ) if(has(filter,f))
  {
    if( hash[f] != filter[f] ) {
      return false;
    }
  }
  return true;
}

function copyFields( src, dest )
{
  if( isNil(dest) ) {
    dest = {};
  }
  for( var k in src ) if(has(src,k)) {
    dest[k] = src[k];
  }
  return dest;
}

/**
 * Treats the hash a path to lookup a value in input hash which is a tree structure.
 * @param hash
 * @param pathArray array defining the tree.
 * @returns
 */
function lookup( hash, pathArray ) {
  for( var i in pathArray ) {
    if( !hash ) {
      return undefined;
    }
    hash = hash[ pathArray[i] ];
  }
  return hash;
}

function findRow( rows, fieldVals ) {
  for( var r in rows ) if(has(rows,r)) {
    if( hasValues( rows[r], fieldVals ) ) {
      return rows[r];
    }
  }
  return {};
}

function regexesc( str ) {
    return (str+'').replace(/([.?*+^$[\]\\(){}|-])/g, "\\$1");
}

function padLeft( val, targetLen, padChar ) {
  val = val.toString();
  while( val.length < targetLen ) {
    val = padChar + val;
  }
  return val;
}

var nonNameCharsPat = /[^a-zA-Z0-9_]/g;
function formatAsName( str ) {
  return str.replace( nonNameCharsPat, '_' );
}


