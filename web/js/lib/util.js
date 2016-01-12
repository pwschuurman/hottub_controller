/**
 * Original Link: http://stv.whtly.com/2009/02/27/simple-jquery-string-padding-function/
 */

$.strPad = function(i,l,s) {
    var o = i.toString();
    if (!s) { s = '0'; }
    while (o.length < l) {
        o = s + o;
    }
    return o;
};
