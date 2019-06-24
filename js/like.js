function set_color_like(button_id) {
    var stat_like = document.getElementById('like_' + button_id);
    var stat_dislike = document.getElementById('dislike_' + button_id);
    if (stat_like.className == 'liked') {
        stat_like.className = 'like';
    } else {
        stat_like.className = 'liked';
    }
    stat_dislike.className = 'dislike';
}
