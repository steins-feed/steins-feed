function highlight(button_id) {
    const xmlhttp = new XMLHttpRequest();

    const title = document.getElementById('title_' + button_id);
    const summary = document.getElementById('summary_' + button_id);
    const stat = document.getElementById('highlight_' + button_id)

    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            title.innerHTML = this.response;
            //summary.innerHTML = this.response;

            if (stat.className == 'highlight') {
                stat.className = 'highlit';
            } else {
                stat.className = 'highlight';
            }
        }
    };

    const fd = new FormData();
    fd.append("id", button_id);

    if (stat.className == 'highlight') {
        xmlhttp.open("POST", home_ep + "/highlight");
    } else {
        xmlhttp.open("POST", home_ep + "/unhighlight");
    }

    xmlhttp.send(fd);
}

