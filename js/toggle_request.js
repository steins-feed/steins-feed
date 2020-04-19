function insert_alphabetically(node, parent_node) {
    let lo = 0;
    let hi = parent_node.length - 1;
    while (lo < hi) {
        let mid = (lo + hi - (hi - lo) % 2) / 2;
        if (parent_node[mid].innerText > node.innerText) {
            hi = mid;
        } else if (lo < mid) {
            lo = mid;
        } else {
            lo++;
        }
    }
    parent_node.insertBefore(node, parent_node[hi]);
}

function toggle_request(left, right, dest, lang=null, param=null) {
    var tagged = [];
    var left_name = left;
    if (lang != null) {
        left_name += '_' + lang;
    }
    var tags = document.getElementsByName(left_name)[0];
    for (var i=0; i < tags.length; i++) {
        if (tags[i].selected) {
            tagged.push(tags[i].value);
        }
    }

    var untagged = [];
    var right_name = right;
    if (lang != null) {
        right_name += '_' + lang;
    }
    var untags = document.getElementsByName(right_name)[0];
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
                    insert_alphabetically(tags[i], untags);
                }
            }

            for (var i = untags.length - 1; i >= 0; i--) {
                if (untags[i].selected) {
                    untags[i].selected = false;
                    insert_alphabetically(untags[i], tags);
                }
            }
        }
    };

    var qs = "user=" + user;
    if (param != null) {
        qs += "&" + param + "=" + window[param + "_id"];
    }
    qs += "&" + left + "=" + JSON.stringify(tagged);
    qs += "&" + right + "=" + JSON.stringify(untagged);

    xmlhttp.open("POST", "/steins-feed/php_settings/toggle_" + dest + ".php", true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlhttp.send(qs);
}

function toggle_display(lang) {
    toggle_request("displayed", "hidden", "display", lang=lang);
}

function toggle_feeds(lang) {
    toggle_request("tagged", "untagged", "feeds", lang=lang, param="tag");
}

function toggle_tags() {
    toggle_request("tagged", "untagged", "tags", lang=null, param="feed");
}
