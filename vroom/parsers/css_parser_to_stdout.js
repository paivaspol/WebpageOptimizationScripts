var css = require('css'),
    fs = require('fs');

if (process.argv.length < 3) {
  console.log('Usage: node css_parser.js [filename] [outputFilename]');
  process.exit(-1);
}

var filename = process.argv.slice(2)[0]; // Get the filename
var fileContent = fs.readFileSync(filename, 'utf-8');

// console.log(fileContent);

try {
  var parsedCSS = css.parse(fileContent);
} catch (e) {
  process.exit(-1);
}

var rules = parsedCSS.stylesheet.rules;

var results = [];  // List containing objects of CSS selector with its child
var fontfaceDeclarations = { };

/* 
 * Assumption: Hardcode the screen resolution (Nexus 6: 412 x 732)
 * Object Schema:
 * {
 *  type: '' { download, media, rule },
 *  url: '',
 *  selector: '' not set if download.
 * }
 */
rules.forEach(function(rule) {
  var declarations = rule.declarations;
  if (declarations !== undefined) {
    var currentFontFamily = undefined;
    declarations.forEach(function(declaration) {
      if (rule.type === 'font-face') {
        if (declaration.property == 'font-family') {
          fontfaceDeclarations[declaration.value] = { };
          currentFontFamily = declaration.value;
        } else if (declaration.value !== undefined &&
          declaration.value.indexOf('url') >= 0) {
          // console.log(declaration.value);
          var css_child = { };
          css_child.type = 'font-face';
          css_child.url = declaration.value;
          fontfaceDeclarations[currentFontFamily] = css_child;
        }
      } else if (rule.type == 'media') {
        // Loop through the rules.
        console.log(media);
        var mediaRules = declaration.rules;
        mediaRules.forEach(function(mediaRule) {
          if (rule.type == 'rule' &&
              declaration.value.indexOf('url') >= 0) {
            /*
            console.log(rule);
            console.log(rule.selectors);
            console.log(declaration.value);
            */
            // Ignore media for now.
          }
        }, this);
      } else if (rule.type == 'rule') {
        if (declaration.property === 'font-family') {
          var fontFamily = declaration.value;
          if (fontFamily in fontfaceDeclarations) {
            results.push(fontfaceDeclarations[fontFamily]);           
            delete fontfaceDeclarations[fontFamily];
          }
        } else if (declaration.value !== undefined &&
            declaration.value.indexOf("url") >= 0) {
          var css_child = { };
          css_child.type = 'rule';
          css_child.selectors = rule.selectors;
          css_child.url = declaration.value;
          results.push(css_child);
        }
      }
    }, this);
  }
}, this);
// console.log(obj.stylesheet.rules);
//
// console.log(fontfaceDeclarations);
console.log(JSON.stringify({ 'results': results }));

// fs.writeFile(outputFilename, JSON.stringify({ 'results': results }), function(err) {
//   console.log('Saved ' + outputFilename);
// });
