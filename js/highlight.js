function highlight(button_id) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            //var summary = document.getElementById('summary_' + button_id);
            //summary.innerHTML = this.responseText;
            var resp = this.responseText;
            var resp_len = resp.length;
            var resp_idx = resp.indexOf(String.fromCharCode(0));
            var title = document.getElementById('title_' + button_id);
            title.innerHTML = resp.substring(0, resp_idx);
            var summary = document.getElementById('summary_' + button_id);
            summary.innerHTML = resp.substring(resp_idx+1, resp_len);
        }
    };
    xmlhttp.open("POST", "/steins-feed/highlight.php", true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlhttp.send("user=" + USER + "&id=" + button_id);
}
