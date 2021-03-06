from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.network.urlrequest import UrlRequest
from kivy.factory import Factory
from kivy.uix.listview import ListItemButton
from kivy.uix.switch import Switch
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.storage.jsonstore import JsonStore 
from kivy.uix.popup import Popup
from plyer import vibrator
from jnius import autoclass
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, BorderImage

from Crypto.Cipher import DES
import os.path
import debug
import cie_connect
import json
import urllib
import kivy
from time import sleep

kivy.require('1.8.0')


def get_sub_number_only(number):
    debug.p("FUNC :::: get_sub_number_only")
    number1 = number.rsplit('/', 1)
    number2 = number1[1][2:]
    return number2


class ColorDownButton(Button):
    """
    Button with a possibility to change the color on on_press (similar to background_down in normal Button widget)
    """
    background_color_normal = ListProperty([.3,.3,.3,1])
    background_color_down = ListProperty([.9, .5, .1, 1])

    def __init__(self, **kwargs):
        super(ColorDownButton, self).__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = self.background_color_normal
        self.text = "Press to Login"

    def on_press(self):
        self.text = "Logging In Now"
        self.background_color = self.background_color_down

    def on_release(self):
        self.background_color = self.background_color_normal



class MexRoot(BoxLayout):
    debug.p("CLASS :::: MexRoot")
    #username_input = ObjectProperty()
    #password_input = ObjectProperty()
    accountRef = ''
    subscription_page = ObjectProperty()
    mex_switch_page = ObjectProperty()
    login_page = ObjectProperty()
    incorrect_password_page = ObjectProperty()

    def __init__(self, **kwargs):
        debug.p("FUNC ::::    MexRoot.__init__")
        super(MexRoot, self).__init__(**kwargs)
        self.store = JsonStore("mex_store.json")

    def set_error_page(self, message):
        """ This func should call an error page"""
        self.clear_widgets()
        if self.incorrect_password_page is None:
            self.incorrect_password_page = IncorrectPasswordPage()
            self.incorrect_password_page.login_status = message
        self.add_widget(self.incorrect_password_page)
        return


    def store_details(self, username, password):
        debug.p("FUNC ::::    MexRoot.store_details")
        BLOCK_SIZE = 16
        PADDING = ' '
        s = self.password_input.text
        pad = lambda s: s +(BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
        des = DES.new('01234567', DES.MODE_ECB)         # This is the decryption hash equivalent
        secret_pass = des.encrypt(pad(s))               # we use this hash to encrypt the password
        #debug.p(secret_pass)
        try:
            f = open('workfile', 'w')
            f.write(secret_pass)
            f.close()
        except IOError:
            debug.p('IOError writing workfile')
            pass
        if username is not None and password is not None:
            debug.p('Ready to Store')
            try:
                self.store.put('details', username = self.username_input.text)
            except IOError:
                debug.p('IOError writing mex_store.json')
                pass
        return
   
    def identify_sub_type(self, subs):
        """ This function will accept the list of two subs and set variables with each path name. 
        return 2 for F2M subscription
        return 1 for Mob Only
        return 0 for error
        """
        debug.p("FUNC ::::    MexRoot.identify_sub_type")
        number_of_subs = len(subs)
        debug.p(number_of_subs)
        if number_of_subs == 1:  #Mobile Only Subscription
            self.mex_switch_page.mobile_number_href = subs[0]
            result = 1
        elif number_of_subs ==2: # Mobile & Fixed Subscription
            if int(subs[0].find('SV8')) > 0:
                self.mex_switch_page.mobile_number_href = subs[0]
                self.mex_switch_page.fixed_number_href = subs[1]
                debug.p(subs[0].find('SV8'))
                debug.p ("if 1" + subs[1])
                result = 2
            elif int(subs[1].find('SV8')) > 0:
                self.mex_switch_page.mobile_number_href = subs[1]
                self.mex_switch_page.fixed_number_href = subs[0] 
                debug.p ("if 2" + subs[0])           
                result = 2
            else:
                debug.p(' ERROR ERROR ERRORERRORERRORERRORERRORERROR')
                result = 0
        else:   # Error condition
            result = 0
        return result

    def check_resuls(self, status):
        """ Take result of NGIN connect and check for errors
        """
        if status == 401:  # Unauthorised Access/Authentication Failure
                self.set_error_page(conn['description'])
            
        elif status ==400: # No Network available
            self.set_error_page("Network Error: \n Please check Network Connectivity!")

        elif status == 200:   
            return


    def go_login(self, username, password):
        debug.p("FUNC ::::    MexRoot.go_login")
        self.clear_widgets()
        if self.mex_switch_page is None:
            self.mex_switch_page = MexSwitchPage()
        self.username_input = username
        self.mex_switch_page.username_input = username
        self.mex_switch_page.password_input = password
        self.password_input = password
        self.store_details(username, password)
        print(str(self.password_input.text))
        print (str(self.username_input.text))
        
        try:
            conn, status = cie_connect.perform_cie_logon(self.username_input.text,self.password_input.text)
        except RuntimeError:
            print "ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR"
            self.set_error_page("Network Error: \n Please check Network Connectivity!")
            
        else:
            if status == 401:  # Unauthorised Access/Authentication Failure
                self.set_error_page(conn['description'])
            
            elif status ==400: # No Network available
                self.set_error_page("Network Error: \n Please check Network Connectivity!")

            elif status == 200:    
                debug.p(conn) 
                self.accountRef = conn['accountRef']
                self.accountRef = self.accountRef.rsplit('/', 1)[0] #this splits the string from the right 
                #using '/' as the delimiter into one extra piece. Then the first past is /accounts/account/subscriptions string
                debug.p(self.accountRef)
                try:
                    conn = cie_connect.get_list_of_mex_subs(self.username_input.text,self.password_input.text, self.accountRef)
                except RuntimeError:
                    print "ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR"
                    self.set_error_page("Mex Sub Error: Network Error:\n Please check Network Connectivity!")
                else:
                    #debug.p(conn) 
                    subscriptions = ["{}".format(d['href']) for d in conn['results']]
                    #debug.p(subscriptions)
                    sub_type = self.identify_sub_type(subscriptions)
                    if sub_type == 1:
                        #MObile Only Sub
                        self.set_error_page('Mobile Only Subscription Type, \n Please contact Eircom Administrator')
                        pass
                    elif sub_type ==2:
                        # Fixed & Mobile Type Sub
                        debug.p(self.mex_switch_page.fixed_number_href)
                        debug.p(self.mex_switch_page.mobile_number_href)
                        x = self.mex_switch_page.getSubscriptionMexSettingsMobile(self.username_input, self.password_input, self.mex_switch_page.mobile_number_href)
                        y = self.mex_switch_page.getSubscriptionMexSettingsFixed(self.username_input, self.password_input, self.mex_switch_page.fixed_number_href)
                        
                        debug.p(x)
                        debug.p(y)
                        if x and y == True:
                            self.add_widget(self.mex_switch_page)
                        else:
                            if x and y == False:
                                self.set_error_page('Both Mex Not Active:\n Incorrect Subscription Type, \n Please contact Eircom Administrator')
                            elif y == False:
                                self.set_error_page('Fixed Mex Not Active:\n Incorrect Subscription Type, \n Please contact Eircom Administrator')
                            else: # X Must b false logically
                                self.set_error_page('Mobile Mex Not Active:\n Incorrect Subscription Type, \n Please contact Eircom Administrator')
                    else:
                        self.set_error_page('2 Incorrect Subscription Type, \n Please contact Eircom Administrator')

            else:
                print "ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR"
                if self.incorrect_password_page is None:
                    self.incorrect_password_page = IncorrectPasswordPage()
                    self.incorrect_password_page.login_status = "FINAL ELSE: Network Error: \n Please check Network Connectivity!"
                self.add_widget(self.incorrect_password_page)
        return 

    def show_login_page(self):
        """ This fuction should be called when the login details are incorrect and we want to return to login form."""
        self.clear_widgets()
        if self.login_page is None:
            self.login_page = LoginForm()
        self.add_widget(self.login_page)
        return

    def show_mob_only_sub_details(self, subscription):
        debug.p("FUNC ::::    MexRoot.show_mob_only_sub_details")
        print ("ENTERING  show_mob_only_details ################################")
        if self.mex_switch_page is None:
            print "\n\n\n\n\n\n **************************** MexSwitchPage is None at show_mob_only_sub_details func"
            self.mex_switch_page = MexSwitchPage()
        self.clear_widgets()
        self.mex_switch_page.getSubscriptionMexSettings(self.username_input, self.password_input,subscription)
        
        self.add_widget(self.mex_switch_page)



    def show_subscription_details(self, subscription):
        debug.p("FUNC ::::    MexRoot.show_subscription_details")
        print ("ENTERING  show_subscription_details ################################")
        self.clear_widgets()
        #self.add_widget(Label(text= subscription))
        if self.mex_switch_page is None:
            print "\n\n\n\n\n\n **************************** MexSwitchPage is None at show_subscription_details func"
            self.mex_switch_page = MexSwitchPage()
        self.add_widget(self.mex_switch_page)
    pass



class MexSwitchPage(BoxLayout):
    debug.p("CLASS ::::    MexSwitchPage")
    mex_root_page = ObjectProperty()
    fixed_number = StringProperty()
    mobile_number = StringProperty()
    cli_to_map_to = StringProperty()
    number_to_forward_to = StringProperty()
    MO_SUB = BooleanProperty()
    FT_SUB = BooleanProperty()
    m2fstate = ObjectProperty()
    f2mstate = ObjectProperty()
    username_input = ObjectProperty()
    password_input = ObjectProperty()
    fixed_subscription_id = StringProperty()
    mobile_subscription_id = StringProperty()
    fixed_lastModified_Date = ""
    fixed_createdDate = ""
    mobile_lastModified_Date = ""
    mobile_createdDate = ""
    mobile_subscription_href = StringProperty()
    fixed_subscription_href = StringProperty()

    class M2FActivateSwitch(Switch):
        debug.p("FUNC ::::    MexSwitchPage.M2FActivateSwitch")
        pass

    class F2MActivateSwitch(Switch):
        debug.p("FUNC ::::    MexSwitchPage.F2MActivateSwitch")
        pass


    def getSubscriptionMexSettingsMobile(self, username, password, subscription):
        debug.p("FUNC ::::    MexSwitchPage.getSubscriptionMexSettingsMobile")
        self.mobile_subscription_href = subscription
        self.username_input = username
        self.password_input = password
        details = cie_connect.get_mobile_only_sub_details(username.text, password.text,subscription)
        
        self.mobile_subscription_id = details['id']
        self.mobile_lastModified_Date = details['lastModified']
        self.mobile_createdDate = details['created']

        result = True # Unless set otherwise in Loop below
        for val in details['attributes']:
            if val['id'] == 'mobexAct':
                if val['value'] != 'MexOriginating': 
                # Mex Service Not Active for Mob Sub or Error .. 
                    result = False # Set Mex Act
                    break

            if val['id'] == 'mobExSub': # Test for MO sub and MEX Active
                if val['value'] == None:
                    self.MO_SUB = False
                else:
                    self.MO_SUB = val['value']

            if val['id'] == 'cliMap':
                debug.p(val['value'])
                self.m2fstate.active= val['value']
                debug.p(val['value'])
            if val['id'] == 'mobExNmr':
                self.cli_to_map_to = val['value']
               
        debug.p ("\n\n\n")
        debug.p(self.cli_to_map_to)
        debug.p(self.MO_SUB)
        debug.p(self.m2fstate.active)
        debug.p(self.username_input.text)
        debug.p('mobile_subscription_id')
        debug.p(self.mobile_subscription_id)
        debug.p(self.mobile_lastModified_Date)
        debug.p(self.mobile_number)
        return result

    def getSubscriptionMexSettingsFixed(self, username, password, subscription):
        debug.p("FUNC ::::    MexSwitchPage.getSubscriptionMexSettingsFixed")
        self.fixed_subscription_href = subscription
        self.username_input = username
        self.password_input = password
        details = cie_connect.get_mobile_only_sub_details(username.text, password.text,subscription)
        print details
        self.fixed_subscription_id = details['id']
        self.fixed_lastModified_Date = details['lastModified']
        self.fixed_createdDate = details['created']

        result = True # Unless set otherwise in Loop below
        for val in details['attributes']:
            if val['id'] == 'mobexAct':
                if val['value'] != 'MexTerminating': 
                # Mex Service Not Active for Mob Sub or Error .. 
                    result = False # Set Mex Act
                    break
                
            if val['id'] == 'mobExTSub': # Test for MO sub and MEX Active
                if val['value'] == None:
                    debug.p('mobExTSub Value is:  ')
                    debug.p(val['value'])
                    self.FT_SUB = False
                else:
                    debug.p('mobExTSub Value is:  ')
                    debug.p(val['value'])
                    self.FT_SUB = val['value']

            if val['id'] == 'cdpnMap':
                self.f2mstate.active= val['value']
            if val['id'] == 'mobExNmr':
                self.number_to_forward_to = val['value']
        
        debug.p ("\n\n\n")
        debug.p(self.number_to_forward_to)
        debug.p(self.FT_SUB)
        debug.p(self.f2mstate.active)
        debug.p(self.username_input.text)
        debug.p(self.fixed_subscription_id)
        debug.p(self.fixed_lastModified_Date)
        
        return result

    def f2mpopup(self):
        """ Function to present f2m POPUP
        """
        debug.p('FUNC: f2mpopup in MexSwitchPage Class')
        if self.f2mstate.active:
            mesg = ("All calls will be diverted to 0{} ".format(self.number_to_forward_to))
        else:
            mesg = ("Calls to 0{}  are not forwarded.").format(self.fixed_subscription_id[2:])
    
        btnclose = Button(text='Back', size_hint_y=None, height='50sp')
        content = BoxLayout(orientation='vertical')
        #content.add_widget(Label(text=mesg, font_size= max(self.height, self.width)/10))
        content.add_widget(btnclose)

        the_title = ("Fixed Line Call Diversion Presentation \n\n\n\n {}\n\n\n\n").format(mesg)
        popup = Popup(title=the_title,
        #content=Label(text=mesg),
        content = content, 
        size_hint=(.8, .8), size = (0,0), separator_color = [0.9,0.9,0.9,1],
        title_color = [.9,.9,.9,1], background = './images/back.png') 
        popup.open()
        btnclose.bind(on_release=popup.dismiss)
        return

    def m2fpopup(self):
        """ Function to present m2f POPUP
        """
        debug.p('FUNC: m2fpopup in MexSwitchPage Class')
        debug.p(self.cli_to_map_to)
        if self.m2fstate.active:
            if(self.cli_to_map_to):
                mesg = ("Hi, 0{} will now be presented as CLI ".format(self.cli_to_map_to))
            else:
                self.getSubscriptionMexSettingsMobile(self.username_input, self.password_input, self.mobile_number_href)
                mesg = ("Hi, 0{} will now be presented as CLI ".format(self.cli_to_map_to))
        else:
            mesg = ("Fixed Number Presentation is not active")

        btnclose = Button(text='Back', size_hint_y=None, height='100sp')
    
        content = BoxLayout(orientation='vertical')
        #content.add_widget(Label(text=mesg, font_size = '20sp'))
        content.add_widget(btnclose)
        
        the_title = ("Mobile to Fixed Number Presentation \n\n\n\n {} \n\n\n\n").format(mesg)
        popup = Popup(title= the_title ,
        #content=Label(text=mesg),
        content = content, 
        size_hint=(.8, .8), size=(0,0 ), background = './images/back.png')
        popup.open()
        btnclose.bind(on_release=popup.dismiss)
        return

    def error_popup(self):
        """ Function to present ERROR POPUP
        """
        debug.p('FUNC: error_popup in MexSwitchPage Class')
        
        mesg = ("An unusual error has occurred. \n Please report to Eircom.\n Close Application")

        btnclose = Button(text='Back', size_hint_y=None, height='100sp')
    
        content = BoxLayout(orientation='vertical')
        #content.add_widget(Label(text=mesg, font_size = '20sp'))
        content.add_widget(btnclose)
        
        the_title = ("Mobile to Fixed Number Presentation \n\n\n\n {} \n\n\n\n").format(mesg)
        popup = Popup(title= the_title ,
        #content=Label(text=mesg),
        content = content, 
        size_hint=(.8, .8), size=(0,0 ), background = './images/back.png')
        popup.open()
        #btnclose.bind(on_release=App.get_running_app().stop())
        return


    def setF2MDiversionActive(self):
        debug.p("FUNC ::::    MexSwitchPage.setF2MDiversionActive")
        debug.p("**********ACTIVATE F2M Divert          " + str(self.f2mstate.active))

        if self.mex_root_page is None:
            self.mex_root_page = MexRoot()

        results = cie_connect.changeMexF2MState(self.username_input.text, self.password_input.text, 
            self.fixed_subscription_href, self.f2mstate.active, self.fixed_lastModified_Date, 
            self.fixed_createdDate, self.fixed_subscription_id )


        if results == True:  # Unauthorised Access/Authentication Failure
            try:
                #vibrator.vibrate(1)
                # Context is a normal java class in the Android API
                Context = autoclass('android.content.Context')

                # PythonActivity is provided by the Kivy bootstrap app in python-for-android
                PythonActivity = autoclass('org.renpy.android.PythonActivity')

                # The PythonActivity stores a reference to the currently running activity
                # We need this to access the vibrator service
                activity = PythonActivity.mActivity

                # This is almost identical to the java code for the vibrator
                vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)

                vibrator.vibrate(500)  # The value is in milliseconds - this is 10s

                self.f2mpopup() 
            except:
                self.f2mpopup() 
            finally:
                return
        else:
            self.error_popup()
            return


    def setM2FPresentationActive(self):
        debug.p("FUNC ::::    MexSwitchPage.setM2FPresentationActive")
        debug.p("###################ACTIVATE M2F Presentation" + str(self.m2fstate.active))
        
        results = cie_connect.changeMexM2FState(self.username_input.text, self.password_input.text, 
            self.mobile_subscription_href, self.m2fstate.active, self.mobile_lastModified_Date,
            self.mobile_createdDate, self.mobile_subscription_id )

        debug.p(results)
        try:
            #vibrator.vibrate(2)
            # 'autoclass' takes a java class and gives it a Python wrapper
            # Context is a normal java class in the Android API
            Context = autoclass('android.content.Context')

            # PythonActivity is provided by the Kivy bootstrap app in python-for-android
            PythonActivity = autoclass('org.renpy.android.PythonActivity')

            # The PythonActivity stores a reference to the currently running activity
            # We need this to access the vibrator service
            activity = PythonActivity.mActivity

            # This is almost identical to the java code for the vibrator
            vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)

            vibrator.vibrate(500)  # The value is in milliseconds - this is 10s
            self.m2fpopup()
        except:
            self.m2fpopup()
            pass
        finally:
            return




class LoginForm(BoxLayout):
    debug.p("CLASS ::::    LoginForm")
    username_input = ObjectProperty() # This is the actual input box, and the input is referenced as self.username_input.text
    password_input = ObjectProperty()
    username = StringProperty() # This allows me to reference in kv file as root.username
    password = StringProperty() # This allows me to reference in kv file as root.username
    login_page = ObjectProperty()

    def __init__(self, **kwargs):
        debug.p("FUNC ::::    LoginForm.__init__ ")
        super(LoginForm, self).__init__(**kwargs)
        self.store = JsonStore("mex_store.json")
        self.password =""

        des = DES.new('01234567', DES.MODE_ECB)
        PADDING = ' '
        DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

        try:
            debug.p("ENTERING init: Check if file exists!!!!!!!!!!!!!!!!!!!!")
            self.store.get('details')['username']
        except KeyError:
            self.username = ""
        except IOError:
            self.username = "" 
        else:
            self.username = self.store.get('details')['username']
        

        if os.path.isfile('workfile'): 
            try:
                f = open('workfile', 'r') 
                m = f.read() # Get encrypted password form file

            except KeyError:
                self.password = ""
            except IOError:
                self.password = ""    # If file does not exist, show password blank
            else:
                x = des.decrypt(m)                          # x is decrypted password
                self.password = x.rstrip(PADDING)           # Strip Padding from decrypted password

    pass


class IncorrectPasswordPage(BoxLayout):
    login_status = StringProperty()

    pass

class CustomLayout(FloatLayout):
    pass

class MarcLabel(Label):
    pass

class MexApp(App):
    debug.p("CLASS ::::    MexApp")
    pass

    
    def on_pause(self):
        debug.p("FUNC ::::    MexRoot.on_pause")
        return True


if __name__ =='__main__':
    MexApp().run()



