const main = document.getElementById('main');
const articles = main.getElementsByClassName('article-hr');
const em = parseInt(getComputedStyle(main).getPropertyValue('font-size'));

const topnav = document.getElementById('topnav');
//const topnav_height = topnav.offsetHeight;
const topnav_domRect = topnav.getBoundingClientRect();
const topnav_height = topnav_domRect.bottom - topnav_domRect.top;

function next_item() {
    let lo = 0;
    let hi = articles.length - 1;

    while (lo < hi) {
        // lo <= mid < hi
        const mid = ((lo + hi) - (hi - lo) % 2) / 2;

        const article_it = articles[mid];
        const article_domRect = article_it.getBoundingClientRect();
        const article_y = article_domRect.top;

        // articles[hi].top >= topnav_height + 1.0
        if (article_y >= topnav_height + 1.0) {
            hi = mid;
        } else if (lo < mid) {
            lo = mid;
        } else {
            lo++;
        }
    }

    const article = articles[hi];

    article.scrollIntoView();
    scrollBy(0, -topnav_height);
}

function prev_item() {
    let lo = 0;
    let hi = articles.length - 1;

    while (lo < hi) {
        // lo < mid <= hi
        const mid = ((lo + hi) + (hi - lo) % 2) / 2;

        const article_it = articles[mid];
        const article_domRect = article_it.getBoundingClientRect();
        const article_y = article_domRect.top;

        // articles[lo].top <= topnav_height - 1.0
        if (article_y <= topnav_height - 1.0) {
            lo = mid;
        } else if (hi > mid) {
            hi = mid;
        } else {
            hi--;
        }
    }

    const article = articles[lo];
    const domRect = article.getBoundingClientRect();
    const y = domRect.top

    if (y <= topnav_height - 1) {
        article.scrollIntoView();
        scrollBy(0, -topnav_height);
    } else {
        scrollTo(0, 0);
    }
}
