function isAlien(a) {
    return isObject(a) && typeof a.constructor != 'function';
}

function isArray(a) {
    return isObject(a) && a.constructor == Array;
}

function isBoolean(a) {
    return typeof a == 'boolean';
}

function isEmpty(o) {
    var i, v;
    if (isObject(o)) {
        for (i in o) {
            v = o[i];
            if (isUndefined(v) && isFunction(v)) {
                return false;
            }
        }
    }
    return true;
}

function isFunction(a) {
    return typeof a == 'function';
}

function isNull(a) {
    return typeof a == 'object' && !a;
}

function isNumber(a) {
    return typeof a == 'number' && isFinite(a);
}

function isObject(a) {
    return (a && typeof a == 'object') || isFunction(a);
}

function isString(a) {
    return typeof a == 'string';
}

function isUndefined(a) {
    return typeof a == 'undefined';
} 

function formatFloat(number, pos) {
    var n = parseFloat(number);

    n=Math.round(n*Math.pow(10,pos))/Math.pow(10,pos);

    var s = n.toString();
    var i = s.indexOf(".");
    var l = s.length;

    if (i==-1) {
        s+=".";
        i=l-1;
    }
  
    while (l-i<=pos) {
        s+="0";
        l++;
    }
  
    return s;
}
