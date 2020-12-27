function like(button_id) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var stat_like = document.getElementById('like_' + button_id);
            var stat_dislike = document.getElementById('dislike_' + button_id);
            if (stat_like.className == 'liked') {
                stat_like.className = 'like';
            } else {
                stat_like.className = 'liked';
            }
            stat_dislike.className = 'dislike';
        }
    };
    xmlhttp.open("POST", home_ep + "like", true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlhttp.send("id=" + button_id);
}

function dislike(button_id) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var stat_like = document.getElementById('like_' + button_id);
            var stat_dislike = document.getElementById('dislike_' + button_id);
            if (stat_dislike.className == 'disliked') {
                stat_dislike.className = 'dislike';
            } else {
                stat_dislike.className = 'disliked';
            }
            stat_like.className = 'like';
        }
    };
    xmlhttp.open("POST", home_ep + "dislike", true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlhttp.send("id=" + button_id);
}
