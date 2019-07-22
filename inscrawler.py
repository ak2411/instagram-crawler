import requests
from bs4 import BeautifulSoup
import re
import json
import hashlib
import urllib
from datetime import datetime
from queue import Queue, Empty
from threading import Thread
import os
import time

## Crawler

def main_inscrawler(who='/beyonce'):
    url_list = []
    name_list = []
    query = {'id': '', 'first': 12, 'hash': '', 'after': ''}
    url='http://instagram.com'
    def getSession(rhx_gis, variables):
        """ Get session preconfigured with required headers & cookies. """
        #"rhx_gis:csfr_token:user_agent:variables"
        values = "%s:%s" % (
                rhx_gis,
                variables)
        x_instagram_gis = hashlib.md5(values.encode()).hexdigest()

        session = requests.Session()
        session.headers = {
                'x-instagram-gis': x_instagram_gis
                }

        return session

    def coba_lagi(r, first):
        nonlocal session, url
        has_next = False
        # get queryID
        if first:
            soup = BeautifulSoup(r.content, "html.parser")
            script_tag = soup.find('script', text=re.compile('window\._sharedData'))
            shared_data = script_tag.string.partition('=')[-1].strip(' ;')
            result = json.loads(shared_data)
            get_first_image_links(result['entry_data']["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"])
            query['after'] = result["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
            # get query_hash
            link_tag = soup.select("link[href*='ProfilePageContainer.js']") #find link with the query_hash
            print(link_tag)
            js_file = session.get(url+link_tag[0]["href"]) #get the JS file
            query['id'] = result["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
            hash = re.search(re.compile('s.pagination},queryId:"(.*)"'), js_file.text)
            if hash:
                query['hash'] = hash.group(1)
            has_next = result["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
        else:
            result = json.loads(r.text)
            query['after'] = result["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
            has_next = result["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
        if not has_next:
            return ''
        variables = '{"id":"'+query['id']+'","first":12,"after":"'+query['after']+'"}'
        rhx_gis = ''
        session = getSession(rhx_gis, variables)
        encoded_vars = urllib.parse.quote(variables)
        next_url = 'https://www.instagram.com/graphql/query/?query_hash=%s&variables=%s' % (query['hash'], encoded_vars)
        return next_url

    first_url_list = []
    first_name_list = []
    def get_first_image_links(node_dict):
        nonlocal first_url_list, first_name_list
        for i in node_dict:
            typename = str(i['node']['__typename'])
            if typename == "GraphImage":
                pic_url = str(i['node']['display_url'])
                # print(ctr, pic_url)
                first_url_list.append(pic_url)
                num_likes = i['node']["edge_media_preview_like"]['count']
                num_comments = i['node']["edge_media_to_comment"]['count']
                date = i['node']['taken_at_timestamp']
                # print(datetime.fromtimestamp(date))
                name = str(num_likes)+'-'+str(num_comments)+'-'+str(date)+'.jpg'
                first_name_list.append(name)

    def get_image_links(r):
        # print(r)
        data = json.loads(r.text)
        pics_url_list = []
        pics_name_list = []
        for i in data['data']['user']['edge_owner_to_timeline_media']['edges']:
            typename = str(i['node']['__typename'])
            if typename == "GraphImage":
                pic_url = str(i['node']['display_url'])
                # print(ctr, pic_url)
                pics_url_list.append(pic_url)
                num_likes = i['node']["edge_media_preview_like"]['count']
                num_comments = i['node']["edge_media_to_comment"]['count']
                date = i['node']['taken_at_timestamp']
                # print(datetime.fromtimestamp(date))
                name = str(num_likes)+'-'+str(num_comments)+'-'+str(date)+'.jpg'
                pics_name_list.append(name)
        return pics_url_list, pics_name_list


    def download_images(url_list, name_list, user):
        #os.chdir("/Volumes/My Passport")
        folder_path = "Influencers" + "/" + user
        retries = 0
        user_data = dict()
        user_data[user] = []
        for i, url in enumerate(url_list):
            if retries > 10:return
            path = folder_path + "/" + str(i) + '-' + name_list[i]
            #'./b2/'+str(i)+'-'+name_list[i]
            img_data = dict()
            img_data["id"] = str(i)
            img_data["url"] = url
            img_data["info"] = name_list[i]
            user_data[user].append(img_data)
            try:
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(e)
                print("rate limited!")
                retries = retries + 1
                print("Retries:", retries)
                continue
        with open(folder_path+'data.txt', 'w+') as outfile:
            json.dump(user_data, outfile)

    def retry(session, next, attempts=10, wait=600):
        for i in range(attempts):
            response = session.get(next)
            if response.status_code != 200:
                print(response)
                print("Waiting....")
                time.sleep(wait)
            else:
                print("Continuing")
                return response
        return "failed"

    session = requests.Session()
    # session.headers = { 'user-agent': CHROME_UA }
    r = session.get(url+who)
    next = coba_lagi(r, True)
    url_list.extend(first_url_list)
    name_list.extend(first_name_list)

    # count = 0
    while next is not '':
        # count += 1
        # print(count)
        response = retry(session, next, 10, 600)
        if response == "failed":
            break
        pics_url_list, pics_name_list = get_image_links(response)
        url_list.extend(pics_url_list)
        name_list.extend(pics_name_list)
        next = coba_lagi(response, False)
    print(len(url_list))
    download_images(url_list, name_list, who)

## Crawler Threading
#starts at liam payne
users = [
         "chiaraferragni", "tataweneck", "jairmessiasbolsonaro",
         "daquan", "iambeckyg",
         "nickyjampr",
         "lilyjcollins"]
#failed: shakira, nickiminaj,

users = ["instagram", "fcbarcelona", "nasa", "nike", "realmadrid", "natgeo"]

users = ["nickiminaj", "mosalah", "gigihadid", "davidbeckham", "camimendes", "shakira",
         "priyankachopra", "zacefron", "paulodybala", "roses_are_rosie",
         "milliebobbybrown", "chrishemsworth", "ladygaga", "colesprouse",
         "aliaabhatt", "k.mbappe", "sooyaaa__", "lilireinhart", "brunamarquezine",
         "real__pcy", "maluma", "danbilzerian", "thenotoriousmma", "narendramodi",
         "hazardeden_10", "marcelotwelve", "vindiesel", "lizakoshy", "jamescharles",
         "madelame", "justintimberlake", "paulpogba", "cohsehun", "kevinhart4real",
         "sophiet", "mileycyrus", "dualipa", "beingsalmankhan", "garethbale11",
         "ronaldinho", "akshaykumar", "jasonstatham", "travisscott", "caradelevingne",
         "pewdiepie", "karolg",
         "shraddhakapoor", "iamzlatanibrahimovic", "katrinakaif", "sergioramos",
         "eminem", "stephencurry30", "katyperry", "gal_gadot", "emrata",
         "baekhyunee_exo", "willsmith", "bts.bighitofficial",
         "brentrivera", "jacquelinef143", "lilpump", "amandacerny", "maeriliamendoncaca",
         "anushkasharma", "eljuanpazurita", "dishaptani", "bretmanrock", "nehakakkar",
         "luissuarez9", "iamsrk", "prattprattpratt", "ranveersingh", "shahidkapoor"]
# print(users[45:49], users[49])
users = users[41:]

def generate_folders():
    #add this when you have hard disk connected
    #os.chdir("/Volumes/My Passport")
    path = "Influencers"
    for name in users:
        path_name = path + "/" + name
        try:
            os.makedirs(path_name)
        except:
            print(path_name + " already made!")

def threaded_crawler():
    generate_folders()
    results = dict()
    threads = []
    q = Queue()
    num_threads = min(2, len(users))
    for i in range(len(users)):
        q.put(("/"+users[i]))
    def crawl_wrapper(q):
        while not q.empty():
            user = q.get()
            try:
                result = main_inscrawler(user)
                results[user] = result

            except Exception as e:
                print(e)
                print("user " + user + " failed")
            q.task_done()
        return True

    for i in range(num_threads):
        print("starting thread " + str(i))
        process = Thread(target=crawl_wrapper, args=[q])
        process.start()
    q.join()
    return results
threaded_crawler()
