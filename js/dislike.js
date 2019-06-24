function set_color_dislike(button_id) {
    var stat_like = document.getElementById('like_' + button_id);
    var stat_dislike = document.getElementById('dislike_' + button_id);
    if (stat_dislike.className == 'disliked') {
        stat_dislike.className = 'dislike';
    } else {
        stat_dislike.className = 'disliked';
    }
    stat_like.className = 'like';
}
