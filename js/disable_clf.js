function disable_clf() {
    var list = document.getElementsByClassName("clf");
    for (i = 0; i < list.length; i++) {
	list[i].disabled = true;
    }
}
