const main = document.getElementById('main');
const articles = main.getElementsByTagName('article');
const em = parseInt(getComputedStyle(main).getPropertyValue('font-size'));

function next_item() {
    let lo = 0;
    let hi = articles.length - 1;

    while (lo < hi) {
        let mid = ((lo + hi) - (hi - lo) % 2) / 2;
        let article_it = articles[mid];
        let domRect = article_it.getBoundingClientRect();
        if (domRect.y >= 2 * em + 1) {
            hi = mid;
        } else if (lo < mid) {
            lo = mid;
        } else {
            lo++;
        }
    }

    let article = articles[hi];
    article.scrollIntoView();
    scrollBy(0, -2 * em);
}

function prev_item() {
    let lo = 0;
    let hi = articles.length - 1;

    while (lo < hi) {
        let mid = ((lo + hi) + (hi - lo) % 2) / 2;
        let article_it = articles[mid];
        let domRect = article_it.getBoundingClientRect();
        if (domRect.y <= 2 * em - 1) {
            lo = mid;
        } else if (hi > mid) {
            hi = mid;
        } else {
            hi--;
        }
    }

    let article = articles[lo];
    let domRect = article.getBoundingClientRect();
    if (domRect.y <= 2 * em - 1) {
        article.scrollIntoView();
        scrollBy(0, -2 * em);
    } else {
        scrollTo(0, 0);
    }
}
