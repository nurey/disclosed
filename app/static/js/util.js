/*
  Code from "Developing Featherweight Web Services with JavaScript"
      http://feather.elektrum.org/
  (c)An Elektrum Press, retain this notice
      License: http://feather.elektrum.org/appendix/licenses.html
*/

// decide whether commify() should really periodify() thousandths
var tmpNum = new Number(0.1);
// thousandth marker is opposite of decimal marker
Number.localeThousandth = tmpNum.toLocaleString().match(/,/) ? '.' : ',';

Number.prototype.commify = function () {
  var numStr = this.toString();
  var num = numStr.split('');

  // simplify by only accepting integers longer than 3 digits
  if ( numStr.match(/\D/) || num.length < 3 ) return numStr;
  num.reverse();
  numStr = num.join('');

  numStr = numStr.replace(/(\d\d\d)/g, "$1_marker_");
  // if we did one too many, take it back
  numStr = numStr.replace(/_marker_$/g, '');
  // replace the thousandth _marker_ with ',' or '.'
  numStr = numStr.replace(/_marker_/g, Number.localeThousandth);

  num = numStr.split('');
  num.reverse();
  return num.join('');
}