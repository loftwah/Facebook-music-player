import requests
import os
import re
import subprocess
from time import sleep
from bs4 import BeautifulSoup
from getpass import getpass

URL = 'https://m.facebook.com'
CACHE = 'fb.accnt'


class Facebook:
    """
    Facebook class
    """

    def __init__(self, session, url):
        """
        Facebook class
        :param session: The session to make request
        :param url: Facebook url
        """
        self.session = session
        self.url = url
        self.cache = False
        self.curr = ''

    def login(self, cache):
        """
        Login into Facebook
        :param cache: The account cache file
        :return: none
        """

        def get_data():
            """
            Get data that required for login
            :return: Tuple { Data Dictionary , A }
            """
            data = {}
            act_url = ''
            log_in = self.session.get(self.url)
            if log_in.ok:
                lpage = BeautifulSoup(log_in.content, 'lxml')

                form = lpage.find('form', {'id': 'login_form'})
                trash = form.find('input', {'name': 'sign_up'})
                inpt = form.find_all('input')

                act_url = form.get('action')

                inpt.remove(trash)

                i = 0
                while i < len(inpt):
                    try:
                        data[inpt[i]['name']] = inpt[i]['value']
                    except:
                        if not os.path.exists(cache):
                            cache_file = open(cache, 'a+')
                            email = input('E-Mail : ')
                            password = getpass('Password : ')
                            cache_file.write(email + '\n')
                            cache_file.write(password)
                        else:
                            cache_file = open(cache, 'r')
                            lines = cache_file.readlines()
                            email = lines[0]
                            password = lines[1]

                        if inpt[i]['name'] == 'email':
                            inpt[i]['value'] = email
                        elif inpt[i]['name'] == 'pass':
                            inpt[i]['value'] = password
                        i -= 1
                    i += 1
            else:
                print('Failed to reach ' + self.url)
                print('Try check your connection')
                sleep(1)
                print('Retry in 3 second ', end='')

                i = 0
                while i < 3:
                    print('.', end='')
                    sleep(1)
                    i += 1
                get_data()

            return data, act_url

        def login():
            """
            Login into facebook with url and data
            :return: none
            """
            data, act_url = get_data()
            self.session.post(self.url + act_url, data)

        def check():
            """
            Check if login attemp is successfull
            :return: Name of the account
            """
            url = 'https://mobile.facebook.com/profile.php'
            r = self.session.get(url)
            ui = UI

            profile = BeautifulSoup(r.content, 'lxml')

            root = profile.find('div', {'id': 'root'})
            name = root.find('strong').text

            if name == '':
                print('Log in Unsuccessful')
                return None
            else:
                print('\n')
                print('Login Success....')
                print('Acccount : ' + name)
                print('')
                print('')
                return name

        login()
        check()

    def search(self, query, arg):
        """
        Search vidio with given query
        :param arg:
        :param query:
        :return: Tumple { Dictionary of search result and how much the video }
        """

        uri = '/search/videos/?q='

        try:
            if arg == 'N':
                req = self.session.get(self.curr)
                result_page = BeautifulSoup(req.content, 'lxml')
                more = result_page.find('div', {'id': 'see_more_pager'})
                self.curr = more.find('a').get('href')
                req = self.session.get(self.curr)
                page = BeautifulSoup(req.content, 'lxml')
            else:
                result_req = self.session.get(self.url + uri + query)
                page = BeautifulSoup(result_req.content, 'lxml')
                self.curr = result_req.url

            result_box = page.find('div', {'id': 'BrowseResultsContainer'})

            r_1 = result_box.find('div')
            r_2 = r_1.find('div')
            r_3 = r_2.find('div')

            posts = r_3.findAll('div', {}, False)

            result = []

            for post in posts:
                data = {}
                titles = post.findAll('p')
                videos = post.findAll('a', {'target': '_blank'})

                title = titles[0].text

                for video in videos:
                    if re.search('^/video_', video['href']):
                        data['title'] = title
                        data['link'] = video['href']
                        result.append(data)
                    else:
                        pass

            return result
        except:
            print('Sorry, no video for ' + query)
            sleep(1)
            print('Try again with different query.')
            sleep(2)
            main()

    def download(self, link):
        tit = '.temp/vid.mp4'

        req = self.session.get(self.url + link)
        soup = BeautifulSoup(req.content, 'lxml')

        form = soup.find('form')

        inpt = form.findAll('input', {'type': 'hidden'})

        act_link = form.get('action')

        data = {}
        for dat in inpt:
            data[dat['name']] = dat['value']

        lin = self.session.post(self.url + act_link, data)

        link = lin.url

        if not os.path.exists('.temp'):
            os.system('mkdir .temp')

        download = self.session.get(link)
        save = open(tit, 'wb')
        save.write(download.content)


class UI:
    """
    Class for the User Interface
    """
    def __init__(self):
        self.color_1 = '\033[95m'
        self.color_2 = '\033[94m'
        self.color_border = '\033[92m'
        self.color_pointer = '\033[91m'
        self.title = '\033[1m'
        self.end = '\033[0m'

    def logo(self):
        """
        Print the logo in screen
        :return: None
        """
        os.system('clear')
        print('\033[94m' + ' _____ _                   ')
        print('\033[94m' + '|  ___| |__  ' + '\033[91m' + ' _ __ ___  _ __')
        print('\033[94m' + '| |_  | \'_ \\' + '\033[91m' + ' | \'_ ` _ \| \'_ \\')
        print('\033[94m' + '|  _| | |_) |' + '\033[91m' + '| | | | | | |_) |')
        print('\033[94m' + '|_|   |_.__/' + '\033[91m' + ' |_| |_| |_| .__/')
        print('                      ' + '\033[91m' + ' |_|')
        print('\033[91m' + ' By : NIxON 42 ( https://github/nixon42 )' + '\033[0m')
        print('')
        print('')

    def list(self, query, data, arg):
        """
        The UI for listing the search result
        :return: Argumen from user
        """

        print(self.color_border + '_____________________________________________________')
        print('')
        print(self.color_1 + (self.title + 'Result for ' + query).upper())
        print(self.color_border + '_____________________________________________________')
        print(self.color_2 + 'ID' + self.color_border + ' | ' + self.color_2 + '                     Title                     ')
        print(self.color_border + '-----------------------------------------------------')

        def swap(number):
            return divmod(number, 2).__getitem__(1) == 1

        i = 1
        color = self.color_1
        for result in data:
            if swap(i):
                color = self.color_2
            else:
                color = self.color_1

            if arg != 0 and i == arg:
                color = self.title + ' ' + self.color_pointer

            title = result['title']
            print(color + ' ' + i.__str__() + ' ' + self.color_border + '|' + color + title[:40] + self.end)
            i += 1


def playing(out):
    t = out.split('/')

    a = t[0].find(':', 3) - 2
    b = t[0].rfind(':') + 3
    curr = t[0][a:b]

    a = t[1].find(':') - 2
    c = t[1].rfind('(')
    b = t[1].rfind(':', 0, c) + 3
    duration = t[1][a:b]

    a = out.find('(') + 1
    b = out.rfind(')') - 1

    current = out[a:b]
    leght = 20
    total = 100

    percent = float(current) * 100 / total
    arrow = '=' * int(percent / 100 * leght - 1) + '>'
    spaces = ' ' * (leght - len(arrow))

    print('\r', end='')
    print('[%s%s] %d%% %s / %s' % (arrow, spaces, percent, curr, duration), end='', flush=True)


def play():
    tit = '.temp/vid.mp4'
    mpv = subprocess.Popen(['mpv', tit, '--no-video'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    while True:
        output = mpv.stderr.readline()
        if output == '' and mpv.poll() is not None:
            print('\n')
            break
        else:
            try:
                playing(output)
            except:
                pass


def main():
    fb_url = URL
    fb_cache = CACHE
    session = requests.session()

    fb = Facebook(session, fb_url)
    ui = UI()

    ui.logo()
    fb.login(fb_cache)

    query = input('Search a music : ')
    data = fb.search(query, 'O')

    arg = 0
    select = True
    while select:

        ui.logo()
        ui.list(query, data, arg)

        print(ui.color_border + '[N] Next  [S] Search  [A] Auto play  [Q] Quit')
        arg = input('\033[94m' + 'Your selection : ' + ui.end)
        if arg == 'A' or arg == 'a':
            i = 1
            for video in data:
                link = video['link']
                title = video['title']

                ui.logo()
                ui.list(query, data, i)
                print('\n')
                print('Playing ' + title[:30] + ' ...')

                fb.download(link)
                play()
                i += 1

        if arg == 'N' or arg == 'n':
            data = fb.search(query, 'N')

        if arg == 'S' or arg == 's':
            main()

        if arg == 'Q' or arg == 'q':
            print('Quitting . . .')
            exit()

        try:
            if int(arg) <= len(data):
                link = data[int(arg)]['link']
                title = data[int(arg)]['title']

                ui.logo()
                ui.list(query, data, arg)
                print('\n')
                print('Playing ' + title[30] + ' ...')

                fb.download(link)
                play()

            else:
                print('Incorect Input ...')
                sleep(1)
                print('Try again!.')
                sleep(1)
        except:
            print('Error ...')
            sleep(1)
            print('Try again!.')
            sleep(1)

if __name__ == '__main__':
    main()

