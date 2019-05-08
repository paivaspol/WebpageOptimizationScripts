var esprima = require('esprima'),
    fs = require('fs');

var filename = process.argv.slice(2)[0];
var fileContent = fs.readFileSync(filename, 'utf-8');

try {
  var parsedJS = esprima.parse(fileContent);
} catch (e) {
  process.exit(-1);
}

console.log(JSON.stringify(parsedJS));
