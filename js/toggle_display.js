function toggle_display(lang) {
    var tagged = [];
    var tags = document.getElementsByName('displayed_' + lang)[0];
    for (var i=0; i < tags.length; i++) {
        if (tags[i].selected) {
            tagged.push(tags[i].value);
        }
    }

    var untagged = [];
    var untags = document.getElementsByName('hidden_' + lang)[0];
    for (var i=0; i < untags.length; i++) {
        if (untags[i].selected) {
            untagged.push(untags[i].value);
        }
    }

    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            for (var i = tags.length - 1; i >= 0; i--) {
                if (tags[i].selected) {
                    tags[i].selected = false;
                    untags.appendChild(tags[i]);
                }
            }

            for (var i = untags.length - 1; i >= 0; i--) {
                if (untags[i].selected) {
                    untags[i].selected = false;
                    tags.appendChild(untags[i]);
                }
            }
        }
    };

    var qs = "user=" + user;
    qs += "&displayed=" + JSON.stringify(tagged);
    qs += "&hidden=" + JSON.stringify(untagged);

    xmlhttp.open("POST", "/steins-feed/php_settings/toggle_display.php", true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlhttp.send(qs);
}
