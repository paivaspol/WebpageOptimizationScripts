if (!(typeof outstanding_important_urls === "undefined") ) {

    console.log("[unimportant-url] Fired: " + performance.now() + " len(outstanding_imporatant_urls): " + outstanding_important_urls.length);
    console.log(outstanding_important_urls);

    // go through list of outstanding xhrs and see if we can process them
    for ( var t = 0; t < outstanding_xhrs.length; t++ ) {
        var curr_xhr = outstanding_xhrs[t];
        if ( curr_xhr.readyState >= 2 ) { // headers should be back so we can handle it
            curr_xhr.onreadystatechange(); // fires handler...handler should remove the entry from the list as well
        }
    }

    // if we have no important urls to fetch, fetch unimportant urls!
    if ( outstanding_important_urls.length == 0 ) {
        for ( var y = 0; y < unimportant_urls.length; y++ ) {
            var unimp_xhr = new XMLHttpRequest();
            unimp_xhr.open("GET", unimportant_urls[y], true);
            console.log("sending request as unimp for: " + unimportant_urls[y]);
            //unimp_xhr.setRequestHeader("Access-Control-Expose-Headers", "Link, x-systemname-unimportant");
            unimp_xhr.send();
            // remove from list
            unimportant_urls.splice(y, 1);
        }
    }
}
