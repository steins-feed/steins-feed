function insert_alphabetically(node, parent_node) {
    let lo = 0;
    let hi = parent_node.length;

    while (lo < hi) {
        let mid = (lo + hi - (hi - lo) % 2) / 2;
        if (parent_node[mid].innerText.toLowerCase() > node.innerText.toLowerCase()) {
            hi = mid;
        } else if (lo < mid) {
            lo = mid;
        } else {
            lo++;
        }
    }

    if (hi == parent_node.length) {
        parent_node.appendChild(node);
    } else {
        parent_node.insertBefore(node, parent_node[hi]);
    }
}

function toggle_request(left, right, dest, suffix, lang=null, param=null, param_id=null) {
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

    var qs = "";
    if (param != null) {
        qs = param + "_id" + "=" + param_id;
    }
    for (var i = 0; i < tagged.length; i++) {
        qs += "&" + left + "=" + tagged[i];
    }
    for (var i = 0; i < untagged.length; i++) {
        qs += "&" + right + "=" + untagged[i];
    }

    xmlhttp.open("POST", dest + "/toggle_" + suffix, true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlhttp.send(qs);
}

function toggle_display(lang) {
    toggle_request("displayed", "hidden", settings_ep, "display", lang=lang);
}

function toggle_feeds(tag_id, lang) {
    toggle_request("tagged", "untagged", tag_ep, "feeds", lang=lang, param="tag", param_id=tag_id);
}

function toggle_tags(feed_id) {
    toggle_request("tagged", "untagged", feed_ep, "tags", lang=null, param="feed", param_id=feed_id);
}
