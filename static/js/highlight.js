function highlight(button_id) {
    const xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            const title = document.getElementById('title_' + button_id);
            const summary = document.getElementById('summary_' + button_id);
            const stat = document.getElementById('highlight_' + button_id)

            if (stat.className == 'highlight') {
                title.innerHTML = this.response;
                //summary.innerHTML = this.response;
                stat.className = 'highlit';
            } else {
                title.innerHTML = this.response;
                //summary.innerHTML = this.response;
                stat.className = 'highlight';
            }
        }
    };

    const fd = new FormData();
    fd.append("id", button_id);

    xmlhttp.open("POST", home_ep + "/highlight");
    xmlhttp.send(fd);
}

