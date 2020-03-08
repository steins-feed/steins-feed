function toggle_tags() {
    var tagged = [];
    var tags = document.getElementsByName('tagged')[0];
    for (var i=0; i < tags.length; i++) {
        if (tags[i].selected) {
            tagged.push(tags[i].value);
        }
    }

    var untagged = [];
    var untags = document.getElementsByName('untagged')[0];
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

    var qs = "user=" + user + "&feed=" + feed_id;
    qs += "&tagged=" + JSON.stringify(tagged);
    qs += "&untagged=" + JSON.stringify(untagged);

    xmlhttp.open("POST", "/steins-feed/php_settings/toggle_tags.php", true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlhttp.send(qs);
}
