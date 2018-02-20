from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.config import Config
import json
import os
import smtplib
import platform
from email.mime.text import MIMEText
from email.header import Header

lastchange = 0
countpassword = 0
Config.set('graphics', 'width', '300')
Config.set('graphics', 'height', '400')
Config.set('graphics', 'fullscreen', '0')

class MiniManager(ScreenManager):
    pass


class MainMenu(Screen):

    def get_countpassword(self):
        global countpassword
        self.ids.count.text = str(countpassword)

    @staticmethod
    def getconnect():
        tolist = App.get_running_app().config.get('mail', 'maillist').split(';')
        smtp = App.get_running_app().config.get('mail', 'smtpip')
        port = App.get_running_app().config.get('mail', 'smtpport')
        sending = App.get_running_app().config.getint('mail', 'sendmail')
        filepath = App.get_running_app().config.get('mail', 'filepath')
        jsonfile = open(filepath, 'r')
        logdict = json.load(jsonfile)
        countpassword = len(logdict)
        # TODO Если countpassword меньше, например, пяти, то отсылать письмо админам, о том, что паролей осталось мало
        jsonfile.close()
        if logdict:
            x = logdict.pop()
            login = x['login']
            password = x['password']
            date = x['date']
            msg = "\nResecetion\nLogin: {}\n  Password: {}".format(login, password)
            mail = MIMEText(msg, 'plain', 'utf-8')
            mail['Subject'] = Header('Запрос пароля к Wi-Fi c iTable', 'utf-8')
            mail['From'] = 'itable@uniflex.by'
            mail['To'] = ", ".join(tolist)
            if sending:
                try:
                    s = smtplib.SMTP(smtp, port)
                    s.starttls()
                    s.sendmail(mail['From'], tolist, mail.as_string())
                    s.quit()
                except:
                    print('Не сработала отправка почты')
            jsonfile = open(filepath, "w+")
            jsonfile.write(json.dumps(logdict))
            jsonfile.close()
        else:
            login = ''
            password = ''

        return login, password


class Setting(Screen):
    pass


class Access(Screen):
    pass


class ITableMiniApp(App):

    def my_callback(self, dt):
        global lastchange
        global countpassword
        try:
            lastmod = os.path.getmtime('pswd.json')
            if lastmod != lastchange:
                jsonfile = open('pswd.json', 'r')
                logdict = json.load(jsonfile)
                countpassword = len(logdict)
                lastchange = lastmod
                print(countpassword)
        except:
            print('File not found')
        print(lastchange)

    def build(self):
        config = self.config
        Clock.schedule_interval(self.my_callback, 2)
        return MiniManager()

    def build_config(self, config):
        config.setdefaults('mail', {'smtpip': '192.168.0.1',
                                    'smtpport': '42',
                                    'maillist': 'mail@domain.com; mail2@domain.com',
                                    'filepath': '',
                                    'sendmail': '0'})

if __name__ == '__main__':
    ITableMiniApp().run()
