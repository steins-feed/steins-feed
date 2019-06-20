#!/usr/bin/env python3

from steins_sql import get_cursor

def select_lang(feed_id=None, selected='English'):
    s = '''<select name='lang'>
  <option value="Afrikanns">Afrikanns</option>
  <option value="Albanian">Albanian</option>
  <option value="Arabic">Arabic</option>
  <option value="Armenian">Armenian</option>
  <option value="Basque">Basque</option>
  <option value="Bengali">Bengali</option>
  <option value="Bulgarian">Bulgarian</option>
  <option value="Catalan">Catalan</option>
  <option value="Cambodian">Cambodian</option>
  <option value="Chinese (Mandarin)">Chinese (Mandarin)</option>
  <option value="Croation">Croation</option>
  <option value="Czech">Czech</option>
  <option value="Danish">Danish</option>
  <option value="Dutch">Dutch</option>
  <option value="English">English</option>
  <option value="Estonian">Estonian</option>
  <option value="Fiji">Fiji</option>
  <option value="Finnish">Finnish</option>
  <option value="French">French</option>
  <option value="Georgian">Georgian</option>
  <option value="German">German</option>
  <option value="Greek">Greek</option>
  <option value="Gujarati">Gujarati</option>
  <option value="Hebrew">Hebrew</option>
  <option value="Hindi">Hindi</option>
  <option value="Hungarian">Hungarian</option>
  <option value="Icelandic">Icelandic</option>
  <option value="Indonesian">Indonesian</option>
  <option value="Irish">Irish</option>
  <option value="Italian">Italian</option>
  <option value="Japanese">Japanese</option>
  <option value="Javanese">Javanese</option>
  <option value="Korean">Korean</option>
  <option value="Latin">Latin</option>
  <option value="Latvian">Latvian</option>
  <option value="Lithuanian">Lithuanian</option>
  <option value="Macedonian">Macedonian</option>
  <option value="Malay">Malay</option>
  <option value="Malayalam">Malayalam</option>
  <option value="Maltese">Maltese</option>
  <option value="Maori">Maori</option>
  <option value="Marathi">Marathi</option>
  <option value="Mongolian">Mongolian</option>
  <option value="Nepali">Nepali</option>
  <option value="Norwegian">Norwegian</option>
  <option value="Persian">Persian</option>
  <option value="Polish">Polish</option>
  <option value="Portuguese">Portuguese</option>
  <option value="Punjabi">Punjabi</option>
  <option value="Quechua">Quechua</option>
  <option value="Romanian">Romanian</option>
  <option value="Russian">Russian</option>
  <option value="Samoan">Samoan</option>
  <option value="Serbian">Serbian</option>
  <option value="Slovak">Slovak</option>
  <option value="Slovenian">Slovenian</option>
  <option value="Spanish">Spanish</option>
  <option value="Swahili">Swahili</option>
  <option value="Swedish ">Swedish </option>
  <option value="Tamil">Tamil</option>
  <option value="Tatar">Tatar</option>
  <option value="Telugu">Telugu</option>
  <option value="Thai">Thai</option>
  <option value="Tibetan">Tibetan</option>
  <option value="Tonga">Tonga</option>
  <option value="Turkish">Turkish</option>
  <option value="Ukranian">Ukranian</option>
  <option value="Urdu">Urdu</option>
  <option value="Uzbek">Uzbek</option>
  <option value="Vietnamese">Vietnamese</option>
  <option value="Welsh">Welsh</option>
  <option value="Xhosa">Xhosa</option>
</select>'''

    if not feed_id is None:
        s = s.replace("<select name='lang'>", "<select name='lang_{}'>".format(feed_id))
    s = s.replace("<option value=\"{}\">".format(selected), "<option value=\"{}\" selected>".format(selected))

    return s

def side_nav(user="nobody", lang="International", page_no=0, feed="Full", clf="Naive Bayes"):
    s = "<form>\n"
    c = get_cursor()

    # Language.
    s += "<p>Language:</p>\n"
    langs = ["International"]
    langs += [e[0] for e in c.execute("SELECT DISTINCT Language FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID WHERE {}=1".format(user)).fetchall()]
    for lang_it in langs:
        t = "<input type=\"radio\" name=\"lang\" value=\"{0}\">{0}<br>\n".format(lang_it)
        if lang_it == lang:
            idx = t.find(">")
            t = t[:idx] + " checked" + t[idx:]
        s += t

    # Feed.
    s += "<p>Feed:</p>\n"
    for feed_it in ["Full", "Magic", "Surprise"]:
        t = "<input type=\"radio\" name=\"feed\" value=\"{0}\">{0}<br>\n".format(feed_it)
        if feed_it == feed:
            idx = t.find(">")
            t = t[:idx] + " checked" + t[idx:]
        s += t

    # Algorithm.
    s += "<p>Algorithm:</p>\n"
    for clf_it in ["Naive Bayes", "Logistic Regression", "SVM", "Linear SVM"]:
        t = "<input type=\"radio\" name=\"clf\" value=\"{0}\">{0}<br>\n".format(clf_it)
        if clf_it == clf:
            idx = t.find(">")
            t = t[:idx] + " checked" + t[idx:]
        s += t

    # Button.
    s += "<p>\n"
    s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no)
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(user)
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Display\">\n"
    s += "</p>\n"

    s += "</form>\n"

    s += "<hr>\n"

    # Report.
    s += "<form><p>\n"
    s += "<select name=\"clf\">\n"
    for clf_it in ["Naive Bayes", "Logistic Regression", "SVM", "Linear SVM"]:
        t = "<option value=\"{0}\">{0}</option>\n".format(clf_it)
        if clf_it == clf:
            idx = t.find(">")
            t = t[:idx] + " selected" + t[idx:]
        s += t
    s += "</select>\n"
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(user)
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/analysis.php\" value=\"Report\">\n"
    s += "</p></form>\n"

    s += "<hr>\n"

    # Statistics & Settings.
    s += "<p><a href=\"/steins-feed/statistics.php?user={}\">Statistics</a></p>\n".format(user)
    s += "<p><a href=\"/steins-feed/settings.php?user={}\">Settings</a></p>\n".format(user)

    return s
