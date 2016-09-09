if (!(typeof outstanding_important_urls === "undefined") ) {

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
}
