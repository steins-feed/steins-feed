function like(button_id) {
    const xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            const stat_like = document.getElementById('like_' + button_id);
            const stat_dislike = document.getElementById('dislike_' + button_id);

            if (stat_like.className == 'liked') {
                stat_like.className = 'like';
            } else {
                stat_like.className = 'liked';
            }

            stat_dislike.className = 'dislike';
        }
    };

    const fd = new FormData();
    fd.append("id", button_id);

    xmlhttp.open("POST", "/home/like");
    xmlhttp.send(fd);
}

function dislike(button_id) {
    const xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            const stat_like = document.getElementById('like_' + button_id);
            const stat_dislike = document.getElementById('dislike_' + button_id);

            stat_like.className = 'like';

            if (stat_dislike.className == 'disliked') {
                stat_dislike.className = 'dislike';
            } else {
                stat_dislike.className = 'disliked';
            }
        }
    };

    const fd = new FormData();
    fd.append("id", button_id);

    xmlhttp.open("POST", "/home/dislike");
    xmlhttp.send(fd);
}
