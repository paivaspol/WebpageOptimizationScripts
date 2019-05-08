var esprima = require('esprima'),
    fs = require('fs');

var filename = process.argv.slice(2)[0];
var outputFilename = process.argv.slice(3)[0];
var fileContent = fs.readFileSync(filename, 'utf-8');

try {
  var parsedJS = esprima.parse(fileContent);
} catch (e) {
  process.exit(-1);
}

fs.writeFile(outputFilename, JSON.stringify(parsedJS), function(err) {
  console.log('Saved ' + outputFilename);
});
