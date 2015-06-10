// Place your application-specific JavaScript functions and classes here
// This file is automatically included by javascript_include_tag :defaults

function openGlossaryWindow(anchor) {
    var href = anchor.getAttribute("href").replace("/glossary/", "/glossary/popup/");
    var windowprops = "toolbar=0,location=0,directories=0,status=yes,menubar=0,scrollbars=yes,resizable=yes,width=425,height=320";
    window.open(href, "Glossary", windowprops);
    return false;
}

function initGlossary() { 
    
    if (!document.getElementsByTagName){ return; }
    var anchors = document.getElementsByTagName('a');

    // loop through all anchor tags
    for (var i=0; i<anchors.length; i++){
        var anchor = anchors[i];
        
        var relAttribute = String(anchor.getAttribute('rel'));
        
        // use the string.match() method to catch 'lightbox' references in the rel attribute
        if (anchor.getAttribute('href') && (relAttribute.toLowerCase().match('glossary'))){
            anchor.onclick = function () { openGlossaryWindow(this); return false;}
        }
    }
    
}

function googleSearchHighlight() {
    if (!document.createElement) return;
    /* don't highlight on the search page */
    if(document.location.href.indexOf('/search/') > -1) return; 
    ref = document.referrer;
    /* alert(ref); */
    if (ref.indexOf('/search/') == -1) return;
    qs = ref.substr(ref.indexOf('/search/')+8);
    qs = qs.split("/")[0];
    qsa = qs.split('+');
    for (i=0;i<qsa.length;i++) {
        qsip = qsa[i];
        // alert("QSIP = " + qsip);
        // var body = $("contentContainer"); // document.getElementsByTagName("body")[0];
        var body = document.getElementById("contentContainer");
        // alert(body);
        highlightWord(body, qsip);
        /*
        qsip = qsa[i].split('=');
        if (qsip.length == 1) continue;
        if (qsip[0] == 'q' || qsip[0] == 'p') { // q= for Google, p= for Yahoo
            words = unescape(qsip[1].replace(/\+/g,' ')).split(/\s+/);
            for (w=0;w<words.length;w++) {
                highlightWord(document.getElementsByTagName("body")[0],words[w]);
            }
        }
        */
    }
}

function highlightWord(node,word) {
    // Iterate into this nodes childNodes

    if (node.hasChildNodes) {
        var hi_cn;
        for (hi_cn=0;hi_cn<node.childNodes.length;hi_cn++) {
            highlightWord(node.childNodes[hi_cn],word);
        }
    }
    
    // And do this node itself
    if (node.nodeType == 3) { // text node
        tempNodeVal = node.nodeValue.toLowerCase();
        tempWordVal = word.toLowerCase();
        if (tempNodeVal.indexOf(tempWordVal) != -1) {
            pn = node.parentNode;
            if (pn.className != "searchword") {
                // word has not already been highlighted!
                nv = node.nodeValue;
                ni = tempNodeVal.indexOf(tempWordVal);
                // Create a load of replacement nodes
                before = document.createTextNode(nv.substr(0,ni));
                docWordVal = nv.substr(ni,word.length);
                after = document.createTextNode(nv.substr(ni+word.length));
                hiwordtext = document.createTextNode(docWordVal);
                hiword = document.createElement("span");
                hiword.className = "searchword";
                hiword.appendChild(hiwordtext);
                pn.insertBefore(before,node);
                pn.insertBefore(hiword,node);
                pn.insertBefore(after,node);
                pn.removeChild(node);
            }
        }
    }
}


function highlightTerm() {
    if (!document.createElement) return;
    // ensure this only executes when showing search results
    if (document.getElementById("searchAgain")) {
        var searchTerm = document.getElementById("q").value;
        words = unescape(searchTerm.replace(/\+/g,' ')).split(/\s+/);
        for (w=0;w<words.length;w++) {
            highlightWord(document.getElementsByTagName("body")[0],words[w]);
        }
    }
}

function toEpoch() {
    var dDate = new Date();
    var s = (dDate.getTime() - dDate.getMilliseconds()) / 1000;
    return s;
}

function hideReproductiveKeywords() {
    var items = $("h2:contains('How do they reproduce?')").nextAll();
    for(var i = 0; i < items.length; i++) {
        if($(items[i]).is("h2")) {
            break;
        } else if ($(items[i]).is("div.boxWrapper")) {
            $(items[i]).hide()
        }
    }
    // .each(function() {
    //     if($(this).is("h2")) {
    //         // break at the next h2
    //         return;
    //     } else if ($(this).is("div.boxWrapper")) {
    //         $(this).hide();
    //     }
    // })
}


// Event.observe(window, 'load', initGlossary, false);
// Event.observe(window, 'load', googleSearchHighlight);

$(document).ready(initGlossary);
$(document).ready(googleSearchHighlight);
// $(document).ready(hideReproductiveKeywords);