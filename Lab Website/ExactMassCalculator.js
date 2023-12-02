//=============================================================
// Exact Mass Calculator, Single Isotope Version.
// Part of SIS ChemTools.
//
// Developed by David J. Manura, Scientific Instrument Services.
// (c) 1996-2002 Scientific Instrument Services.
//
// Notes:
//   Token types:
//     '(' - group initiator
//     ')' - group terminator
//     'A' - atom
//     'N' - number
//     'T' - terminator character
//   Operand stack node types:
//     'S' - bottom of stack
//     'D' - data item
//     '(' - group separator
//=============================================================

// the operand stack
var stack = new myobject();
var stackpos = 0;

// the character stream
var stream;

// table of most abundant isotopes.
// from the CRC Handbook of Chemistry and Physics.
var info = new myobject();
info["H"] = [1.007825, 0.9999];
info["He"] = [4.002603, 1.0000];
info["Li"] = [7.016005, 0.9258];
info["Be"] = [9.012183, 1.0000];
info["B"] = [11.009305, 0.8020];
info["C"] = [12.000000, 0.9890];
info["N"] = [14.003074, 0.9963];
info["O"] = [15.994915, 0.9976];
info["F"] = [18.998403, 1.0000];
info["Ne"] = [19.992439, 0.9060];
info["Na"] = [22.989770, 1.0000];
info["Mg"] = [23.985045, 0.7890];
info["Al"] = [26.981541, 1.0000];
info["Si"] = [27.976928, 0.9223];
info["P"] = [30.973763, 1.0000];
info["S"] = [31.972072, 0.9502];
info["Cl"] = [34.968853, 0.7577];
info["Ar"] = [39.962383, 0.9960];
info["K"] = [38.963708, 0.9320];
info["Ca"] = [39.962591, 0.9695];
info["Sc"] = [44.955914, 1.0000];
info["Ti"] = [47.947947, 0.7380];
info["V"] = [50.943963, 0.9975];
info["Cr"] = [51.940510, 0.8379];
info["Mn"] = [54.938046, 1.0000];
info["Fe"] = [55.934939, 0.9172];
info["Co"] = [58.933198, 1.0000];
info["Ni"] = [57.935347, 0.6827];
info["Cu"] = [62.929599, 0.6917];
info["Zn"] = [63.929145, 0.4860];
info["Ga"] = [68.925581, 0.6010];
info["Ge"] = [73.921179, 0.3650];
info["As"] = [74.921596, 1.0000];
info["Se"] = [79.916521, 0.4960];
info["Br"] = [78.918336, 0.5069];
info["Kr"] = [83.911506, 0.5700];
info["Rb"] = [84.911800, 0.7217];
info["Sr"] = [87.905625, 0.8258];
info["Y"] = [88.905856, 1.0000];
info["Zr"] = [89.904708, 0.5145];
info["Nb"] = [92.906378, 1.0000];
info["Mo"] = [97.905405, 0.2413];
info["Ru"] = [101.90434, 0.3160];
info["Rh"] = [102.905503, 1.0000];
info["Pd"] = [105.903475, 0.2733];
info["Ag"] = [106.905095, 0.5184];
info["Cd"] = [113.903361, 0.2873];
info["In"] = [114.903875, 0.9570];
info["Sn"] = [119.902199, 0.3240];
info["Sb"] = [120.903824, 0.5730];
info["Te"] = [129.906229, 0.3380];
info["I"] = [126.904477, 1.0000];
info["Xe"] = [131.904148, 0.2690];
info["Cs"] = [132.905433, 1.0000];
info["Ba"] = [137.905236, 0.7170];
info["La"] = [138.906355, 0.9991];
info["Ce"] = [139.905442, 0.8848];
info["Pr"] = [140.907657, 1.0000];
info["Nd"] = [141.907731, 0.2713];
info["Sm"] = [151.919741, 0.2570];
info["Eu"] = [152.921243, 0.5220];
info["Gd"] = [157.924111, 0.2484];
info["Tb"] = [158.925350, 1.0000];
info["Dy"] = [163.929183, 0.2820];
info["Ho"] = [164.930332, 1.0000];
info["Er"] = [165.930305, 0.3360];
info["Tm"] = [168.934225, 1.0000];
info["Yb"] = [173.938873, 0.3180];
info["Lu"] = [174.940785, 0.9740];
info["Hf"] = [179.946561, 0.3520];
info["Ta"] = [180.948014, 0.9999];
info["W"] = [183.950953, 0.3067];
info["Re"] = [186.955765, 0.6260];
info["Os"] = [191.961487, 0.4100];
info["Ir"] = [192.962942, 0.6270];
info["Pt"] = [194.964785, 0.3380];
info["Au"] = [196.966560, 1.0000];
info["Hg"] = [201.970632, 0.2965];
info["Tl"] = [204.974410, 0.7048];
info["Pb"] = [207.976641, 0.5240];
info["Bi"] = [208.980388, 1.0000];
info["Th"] = [232.038054, 1.0000];
info["U"] = [238.050786, 0.9927];

function myobject() {}

//--- lexer

// character test functions

// returns true if given character is a letter, else false.
function isalpha(c) {
  var balpha = (c>="a" && c<="z") || (c>="A" && c<="Z");
  return balpha;
}
// returns true if given character is a digit, else false.
function isdigit(c) {
  var bnum = (c>="0" && c<="9");
  return bnum;
}

// string test functions.

// returns true is given string is an element, else false.
function iselement(str) {
  var bele = info[str];
  return bele;
}

// initialize the character stream with the given
// character string.
function loadStream(str) {
  stream = str;
}

// retrieve the next token object.
// Note: an end-of-stream token has type "T".
function nextToken() {
  var token = new myobject();

  if(stream.length == 0)
    token.type = "T";
  else if(isalpha(stream.charAt(0))) {
    var test1 = stream.charAt(0);
    var test2 = test1;
    if(stream.length >= 2 && isalpha(stream.charAt(1)))
      test2 += stream.charAt(1);
    var ele = null;
    if(iselement(test2))
      ele = test2;
    else if(iselement(test1))
      ele = test1;

    if(ele != null) {
      token.type = "A";
      token.text = ele;
      stream = stream.substring(ele.length); // advance
    }
    else {
      token.type = "B";
      token.text = test2;
      token.message = "Invalid element abbreviation.";
    }
  }
  else if(isdigit(stream.charAt(0))) {
    var num = '';
    while(stream.length > 0 && isdigit(stream.charAt(0))) {
      num += stream.charAt(0);
      stream = stream.substring(1); // advance
    }
    token.type = "N";
    token.text = num;
  }
  else if(stream.charAt(0) == '(') {
    token.type = "(";
    stream = stream.substring(1); // advance
  }
  else if(stream.charAt(0) == ')') {
    token.type = ")";
    stream = stream.substring(1); // advance
  }
  else {
    token.type = "B";
    token.text = stream.charAt(0);
    token.message = "Invalid character.";
  }
    

  return token;
}


//--- parser / generator

function resetStack() {
  stackpos = 0;
}

// push given object onto the operand stack.
function push(data) {
  stack[stackpos] = data;
  stackpos++;
}

// pops element from the operand stack
function pop() {
  stackpos--;
  var data = stack[stackpos];
  return data;
}

// computes mass (amu) and fractional abundance
// of a single isotope of the species represented
// by the given chemical formula.  A result object
// is returned.
//
// Note: The isotope selected has the property that each atom
// in the species is the most abundant isotope of that
// element. For low mass chemical species, the chosen
// isotope is often the most abundant isotope; however,
// this is often not the case for larger mass species due
// to the need for a more complex algorithm to make such a
// determination. 
function formulamass(formula) {
  var result = new myobject();

  loadStream(formula);

  // prepare stack
  resetStack();
  var node = new myobject();
  node.type = "S";
  push(node);

  // state machine
  var token;
  var token = nextToken();
  while(token.type != "T") {
    if(token.type == "B") {
      result.error = 1;
      result.message = "Unrecognized token \"" + token.text + "\": "
          + token.message;
      return result;
    }
    var pmass;
    var pabun;
    if(token.type == "A")
    {
      var entry = info[token.text];
      var emass = entry[0];
      var eabun = entry[1];

      token = nextToken();

      var node = new myobject();
      node.type = "D";
      node.pmass = emass;
      node.pabun = eabun;
      push(node);
    }
    else if(token.type == "N") {
      var node = pop();
      if(node.type != "D") {
        result.error = 1;
        result.message = "Unexpected number: " + token.text + ".";
        return result;
      }
      var quan = 0 + token.text;

      var node2 = new myobject();
      node2.pmass = node.pmass * quan;
      node2.pabun = Math.pow(node.pabun, quan);
      push(node2);

      token = nextToken();
    }
    else if(token.type == "(") {
      var node = new myobject();
      node.type = "(";
      push(node);

      token = nextToken();
    }
    else if(token.type == ")") {
      var pmass = 0;
      var pabun = 1;

      // do calcs
      var count = 0;
      while(1) {
        var node = pop();
        if(node.type == "S") {
           result.error = 1;
           result.message = "Mismatched right parenthesis.";
           return result;
        }
        else if(node.type == "(") break;

        pmass += node.pmass;
        pabun *= node.pabun;

        ++count;
      }
      if(count == 0) {
        result.error = 1;
        result.message = "Empty grouping."; // warn
        return result;
      }

      var node2 = new myobject();
      node2.type = "D";
      node2.pmass = pmass;
      node2.pabun = pabun;
      push(node2);

      if(token.type == "T") break; //fix:cleanup
      token = nextToken();

    }

  }

  // do calcs
  var count = 0;
  var pmass = 0;
  var pabun = 1;
  while(1) {
    var node = pop();
    if(node.type == "(") {
       result.error = 1;
       result.message = "Mismatched left parenthesis.";
       return result;
    }
    if(node.type == "S") break;

    ///alert("calc:" + node.pmass);
    pmass += node.pmass;
    pabun *= node.pabun;

    ++count;
  }
  if(count == 0) {
    result.error = 1;
    result.message = "Empty formula."; // warn
    return result;
  }

  result.error = 0;
  result.mass = pmass;
  result.abun = pabun;
  return result;
}




