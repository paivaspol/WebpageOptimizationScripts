// first get top-level URL
// this gets attribute on top-level HTML tag (unless in iframe, in which case it considers first <html> tag in iframe)
// first get index of <html> tag in childNodes list (first tag could be <DOCTYPE HTML>
// flag which states whether we have already handled top-level HTML (don't want to trigger process again!)
if ( typeof finished_top === "undefined" ) {
    finished_top = false;
    var html_index = -1;
    for ( var ind = 0; ind < document.childNodes.length; ind++ ) {
        if ( document.childNodes[ind] instanceof Element ) {
            html_index = ind;
            break;
        }
    }
    window.top_level_url = document.childNodes[ind].getAttribute("top_url");
    if ( !window.top_level_url ) {
        finished_top = true;
    }
    
    // lists important URLs specified by each object
    important_urls = {}
    
    // outstanding important URLs
    outstanding_important_urls = [];
    
    // unimportant urls to fetch
    unimportant_urls = [];
    
    // handler function for important URLs
    var important_url_handler = function () {
        var urls = [];
        var unimp_urls = [];
    
        // first get list of important/unimportant urls from headers
        if ( this.readyState == 4 ) { // loaded
            // remove url from list!
            var index = outstanding_important_urls.indexOf(this._url);
            outstanding_important_urls.splice(index, 1);
            link_header = this.getResponseHeader("Link");
            if ( link_header ) {
                parts = link_header.split("<")
                for (var p = 1; p < parts.length; p++) {
                    urls.push(parts[p].split(">")[0]);
                    //console.log("GOT link header: " + parts[p].split(">")[0]);
                }
            }
            unimp_header = this.getResponseHeader("x-systemname-unimportant");
            if ( unimp_header ) {
                unimp_parts = unimp_header.split(",");
                for ( var up = 0; up < unimp_parts.length; up++ ) {
                    unimp_urls.push(unimp_parts[up]);
                }
            }
        }
    
        // add unimportant urls that will ultimately have to be fetched
        if ( unimp_urls.length > 0 ) { // unimportant urls to fetch
            for ( var j = 0; j < unimp_urls.length; j++ ) {
                if ( unimportant_urls.indexOf(unimp_urls[j]) == -1 ) { // new unimportant URL
                    //console.log("GOT UNIMPORTANT URL TO MAKE: " + unimp_urls[j]);
                    unimportant_urls.push(unimp_urls[j]);
                }
            }
        }
    
        if ( urls.length > 0 ) { // more important urls
            for ( var i = 0; i < urls.length; i++ ) {
                if ( outstanding_important_urls.indexOf(urls[i]) == -1 ) { // new important URL
                    outstanding_important_urls.push(urls[i]);
                    // fetch URL
                    var xhr = new XMLHttpRequest();
                    xhr.open("GET", urls[i], true);
                    xhr._url = urls[i];
                    xhr.onreadystatechange = important_url_handler;
                    xhr.setRequestHeader("Access-Control-Expose-Headers", "Link, x-systemname-unimportant");
                    //console.log("sending request as imp for: " + urls[i]);
                    xhr.send();
                }
            }
        }
    
        // if we have no important urls to fetch, fetch unimportant urls!
        if ( outstanding_important_urls.length == 0 ) {
            for ( var y = 0; y < unimportant_urls.length; y++ ) {
                var unimp_xhr = new XMLHttpRequest();
                unimp_xhr.open("GET", unimportant_urls[y], true);
                //console.log("sending request as unimp for: " + unimportant_urls[y]);
                unimp_xhr.setRequestHeader("Access-Control-Expose-Headers", "Link, x-systemname-unimportant");
                unimp_xhr.send();
                // remove from list
                unimportant_urls.splice(y, 1);
            }
        }
    };
    
    // make request for top-level HTML to start the process
    if ( !window.finished_top ) {
        var top_xhr = new XMLHttpRequest();
        top_xhr.open("GET", top_level_url, true);
        top_xhr.onreadystatechange = important_url_handler;
        top_xhr.addEventListener("onreadystatechange", function () {window.finished_top = true;});
        //console.log("sending request to start top for: " + top_level_url);
        top_xhr.setRequestHeader("Access-Control-Expose-Headers", "Link, x-systemname-unimportant");
        top_xhr.send();
        window.finished_top = true;
    }
}
