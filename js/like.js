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
    xmlhttp.open("POST", "/steins-feed/like.php", true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlhttp.send("user=" + user + "&id=" + button_id + "&submit=Like");
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
    xmlhttp.open("POST", "/steins-feed/like.php", true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlhttp.send("user=" + user + "&id=" + button_id + "&submit=Dislike");
}
