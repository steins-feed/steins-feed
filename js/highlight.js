var token_pattern = "(\\b\\w\\w+\\b)(?![^<]*>)";

function highlight_on(s, stemmer, words) {
    var tokens = new Set(s.match(new RegExp(token_pattern, 'g')));

    for (token_it of tokens) {
        var stemmed = stemmer.stemWord(token_it.toLowerCase());
        var stemmed_val = 2. * words[stemmed] - 1.;
        if (!(stemmed in words) || Math.abs(stemmed_val) < 0.5) {
            continue;
        }

        var src = new RegExp(token_pattern.replace("\\w\\w+", token_it), 'g');
        var dest = "<span class=\"tooltip\"><mark>" + token_it + "</mark><span class=\"tooltiptext\">" + stemmed_val.toFixed(2) + "</span></span>";
        s = s.replace(src, dest);
    }

    return s;
}

function highlight_off(s) {
    var tokens = new Set(s.match(new RegExp(token_pattern, 'g')));

    for (token_it of tokens) {
        var src = new RegExp("<span class=\"tooltip\"><mark>" + token_it + "</mark><span class=\"tooltiptext\">0.\\d\\d</span></span>", 'g');
        s = s.replace(src, token_it);
    }

    return s;
}

function highlight(button_id, lang) {
    var stemmer = new window[lang + "Stemmer"]();
    var words = window[lang.toLowerCase() + "_words"];

    var title = document.getElementById('title_' + button_id);
    var summary = document.getElementById('summary_' + button_id);
    var stat = document.getElementById('highlight_' + button_id)

    if (stat.className == 'highlight') {
        title.innerHTML = highlight_on(title.innerHTML, stemmer, words);
        summary.innerHTML = highlight_on(summary.innerHTML, stemmer, words);
        stat.className = 'highlit';
    } else {
        title.innerHTML = highlight_off(title.innerHTML);
        summary.innerHTML = highlight_off(summary.innerHTML);
        stat.className = 'highlight';
    }
}
