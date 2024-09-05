import requests
import json
import html
import re
import sqlite3

# this is just for test. I will revoke this later.
TOKEN = "7082907773:AAGx-50TmQr_v7KAGsR0H7FSE0FcFA9clR8"
chat_id = "519932241"

def send_post_request(url, data):
    try:
        # Need to seet application/x-www-form-urlencoded header for put and use data string.
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, data=data, headers=headers)

        if response.status_code == 200:
            return response.text
        else:
            return {'status_code': response.status_code, 'response_text': response.text}
    except requests.exceptions.RequestException as e:
        # Gestisce eventuali errori di richiesta
        return {'error': str(e)}

def getType(html):
    start = html.find('<span class="category')
    end = html.find('</span>', start)
    if "NOTIZIA" in html[start:end]:
        return "NOTIZIA"
    else:
        return "AVVISO"

def getTitle(html):
    first = '<h3 class="card-title">'
    start = html.find(first)
    end = html.find('</h3>', start)
    return html[start:end].replace(first, '')

def getDate(html):
    first = '<span class="data">'
    start = html.find(first)
    end = html.find('</span>', start)
    return html[start:end].replace(first, '')

def getText(html):
    first = '<p class="card-text text-secondary">'
    start = html.find(first)
    end = html.find('</p>', start)
    return html[start:end].replace(first, '')

def getUrl(html):
    first = '<a class="text-decoration-none" href="'
    start = html.find(first)
    end = html.find('">', start)
    return html[start:end].replace(first, '')


def convert_html_to_obj(html):
    obj = {
        "type": "", # "Avviso" or "Notizia"
        "title": "",
        "date": "", # Yeah date as string for now.
        "body": "",
        "url": "",
    }

    obj["type"] = getType(html)
    obj["title"] = getTitle(html)
    obj["date"] = getDate(html)
    obj["body"] = getText(html)
    obj["url"] = getUrl(html)

    return obj


def send_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"    
    return requests.get(url).json() 

def prepare_message(obj):
    type = obj["type"]
    date = obj["date"]
    title = obj["title"]
    #body = obj["body"] this website is shit. the body and title are same.
    url = obj["url"]

    query = "SELECT * FROM news_history WHERE date = ? AND title = ? AND type = ?;"
    cursor.execute(query, (date, title, type))
    results = cursor.fetchall()
    
    # already in database. don't send again.
    if results:
        return -1

    message = f'{type} - {date}\n\n{title}\n{url}'
    
    query = "INSERT INTO news_history (date, title, type) VALUES (?, ?, ?);"
    cursor.execute(query, (date, title, type))

    return message

def processing_data(html):
    obj = convert_html_to_obj(html)
    pm = prepare_message(obj)
    
    if pm == -1:
        print("Data already in database. Don't send again: " + obj["title"])
        return
    else:
        send_message(pm)

# cluster of 3
def getNewMessage(html):
    start = html.find('<div class="col-md-6 col-xl-4">')
    end = html.find('<div class="col-md-6 col-xl-4">', start + 1)
    if (end == -1):
        processing_data(html[start:])
    else:
        processing_data(html[start:end])
        getNewMessage(html[start + 1:])

def handler(url, data):
    # get response, this is in html code. we will convert this in markdown for send in telegram chat.
    response = send_post_request(url, data)
    obj = json.loads(response)
    page_ajax = obj["response"]

    # clean up the response string for remove this shit.
    page_ajax = page_ajax.replace("\\/", '/').replace("\\n", ' ')
    page_ajax = html.unescape(page_ajax) # convert from html type to utf-8
    page_ajax = re.sub(r'\s+', ' ', page_ajax) # remove tab or other shit
    page_ajax = page_ajax.strip() # remove space

    getNewMessage(page_ajax)

def main():
    # open database connection
    global conn
    conn = sqlite3.connect("database.db", timeout=1000)
    global cursor
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS news_history(id INTEGER PRIMARY KEY AUTOINCREMENT, date varchar(50), title TEXT, type TEXT);")

    url = "https://comune.locri.rc.it/wp-admin/admin-ajax.php"
    # this is data string about request of new news. The page is defined by "post_count=" arg.
    data = "action=load_more&query=%7B%22page%22%3A0%2C%22pagename%22%3A%22novita%22%2C%22error%22%3A%22%22%2C%22m%22%3A%22%22%2C%22p%22%3A0%2C%22post_parent%22%3A%22%22%2C%22subpost%22%3A%22%22%2C%22subpost_id%22%3A%22%22%2C%22attachment%22%3A%22%22%2C%22attachment_id%22%3A0%2C%22name%22%3A%22novita%22%2C%22page_id%22%3A0%2C%22second%22%3A%22%22%2C%22minute%22%3A%22%22%2C%22hour%22%3A%22%22%2C%22day%22%3A0%2C%22monthnum%22%3A0%2C%22year%22%3A0%2C%22w%22%3A0%2C%22category_name%22%3A%22%22%2C%22tag%22%3A%22%22%2C%22cat%22%3A%22%22%2C%22tag_id%22%3A%22%22%2C%22author%22%3A%22%22%2C%22author_name%22%3A%22%22%2C%22feed%22%3A%22%22%2C%22tb%22%3A%22%22%2C%22paged%22%3A0%2C%22meta_key%22%3A%22%22%2C%22meta_value%22%3A%22%22%2C%22preview%22%3A%22%22%2C%22s%22%3A%22%22%2C%22sentence%22%3A%22%22%2C%22title%22%3A%22%22%2C%22fields%22%3A%22%22%2C%22menu_order%22%3A%22%22%2C%22embed%22%3A%22%22%2C%22category__in%22%3A%5B%5D%2C%22category__not_in%22%3A%5B%5D%2C%22category__and%22%3A%5B%5D%2C%22post__in%22%3A%5B%5D%2C%22post__not_in%22%3A%5B%5D%2C%22post_name__in%22%3A%5B%5D%2C%22tag__in%22%3A%5B%5D%2C%22tag__not_in%22%3A%5B%5D%2C%22tag__and%22%3A%5B%5D%2C%22tag_slug__in%22%3A%5B%5D%2C%22tag_slug__and%22%3A%5B%5D%2C%22post_parent__in%22%3A%5B%5D%2C%22post_parent__not_in%22%3A%5B%5D%2C%22author__in%22%3A%5B%5D%2C%22author__not_in%22%3A%5B%5D%2C%22search_columns%22%3A%5B%5D%2C%22ignore_sticky_posts%22%3Afalse%2C%22suppress_filters%22%3Afalse%2C%22cache_results%22%3Atrue%2C%22update_post_term_cache%22%3Atrue%2C%22update_menu_item_cache%22%3Afalse%2C%22lazy_load_term_meta%22%3Atrue%2C%22update_post_meta_cache%22%3Atrue%2C%22post_type%22%3A%22%22%2C%22posts_per_page%22%3A10%2C%22nopaging%22%3Afalse%2C%22comments_per_page%22%3A%2250%22%2C%22no_found_rows%22%3Afalse%2C%22order%22%3A%22DESC%22%7D&page=1&post_count=POST_CLUSTER&load_posts=3&search=&post_types=%22notizia%22&load_card_type=notizia&query_params=%5B%5D&additional_filter=null"

    # just check last 3*3 post in 3^3 time. just for make sure XD
    index = 0
    while index < 3:
        handler(url, data.replace("POST_CLUSTER", str(index * 3)))
        index += 1
        print(index)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
