from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.network.urlrequest import UrlRequest
from kivy.factory import Factory
from kivy.uix.listview import ListItemButton
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.storage.jsonstore import JsonStore 

from Crypto.Cipher import DES
import os.path
import debug
import cie_connect
import json
import urllib



def get_sub_number_only(number):
    debug.p("FUNC :::: get_sub_number_only")
    number1 = number.rsplit('/', 1)
    number2 = number1[1][2:]
    return number2


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


    def identify_mob_fixed_vpn_sub_type(self, subs):
        """ This function will accept the list of two subs and set variables with each path name. 
        """
        debug.p("FUNC ::::    MexRoot.identify_mob_fixed_vpn_subs")
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

    def store_details(self, username, password):
        debug.p("FUNC ::::    MexRoot.store_details")
        BLOCK_SIZE = 16
        PADDING = ' '
        s = self.password_input.text
        pad = lambda s: s +(BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
        des = DES.new('01234567', DES.MODE_ECB)         # This is the decryption hash equivalent
        secret_pass = des.encrypt(pad(s))               # we use this hash to encrypt the password
        debug.p(secret_pass)
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
    
    def set_error_page(self, message):
        """ This func should call an error page"""
        self.clear_widgets()
        if self.incorrect_password_page is None:
            self.incorrect_password_page = IncorrectPasswordPage()
            self.incorrect_password_page.login_status = message
        self.add_widget(self.incorrect_password_page)
        return

    def go_login(self, username, password):
        debug.p("FUNC ::::    MexRoot.go_login")
        self.clear_widgets()
        if self.subscription_page is None:
            self.subscription_page = SubscriptionPage()
        if self.mex_switch_page is None:
            self.mex_switch_page = MexSwitchPage()
        self.username_input = username
        self.password_input = password
        self.store_details(username, password)
        print(str(self.password_input.text))
        print (str(self.username_input.text))
        
        try:
            conn, status = cie_connect.perform_cie_logon(self.username_input.text,self.password_input.text)
        except RuntimeError:
            print "ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR"
            self.set_error_page("Network Error: Please check Network Connectivity!")
        else:
            if status == 401:  # Unauthorised Access/Authentication Failure
                self.set_error_page(conn['description'])
            
            elif status ==400: # No Network available
                self.set_error_page("Network Error: Please check Network Connectivity!")

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
                    self.set_error_page("Mex Sub Error: Network Error: Please check Network Connectivity!")

                else:
                    debug.p(conn) 
                    subscriptions = ["{}".format(d['href']) for d in conn['results']]
                    debug.p(subscriptions)
                    result = self.identify_mob_fixed_vpn_sub_type(subscriptions)
                    result = 1
                    if result ==1:
                        # Mobile Only Subscription
                        self.mex_switch_page.mobile_number = get_sub_number_only(self.mex_switch_page.mobile_number_href)
                        self.clear_widgets()
                        self.mex_switch_page.getSubscriptionMexSettingsMobileOnly(self.username_input, self.password_input,self.mex_switch_page.mobile_number_href)        
                        self.add_widget(self.mex_switch_page)

                    elif result ==2:
                        #Fixed & Mobile Subscription
                        self.mex_switch_page.fixed_number = get_sub_number_only(self.mex_switch_page.fixed_number_href)
                        self.mex_switch_page.mobile_number = get_sub_number_only(self.mex_switch_page.mobile_number_href)
                        if(self.mex_switch_page.getSubscriptionMexSettingsFixedMobile(self.username_input, self.password_input,self.mex_switch_page.fixed_number_href)):
                            self.clear_widgets()
                            self.add_widget(self.mex_switch_page)
                        else:
                            self.set_error_page(" Error Condition generated : SHITTTTTTTTT!!!!!!")
                        pass
                    elif result ==0: # Error Condition
                        print "ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR"
                        self.set_error_page(" Error Condition generated : Should not really hit here!!!!!!!")
                    else:
                        pass
                    
                
            else:
                print "ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR"
                self.set_error_page("FINAL ELSE: Network Error: Please check Network Connectivity!")

        return 

    def show_login_page(self):
        """ This fuction should be called when the login details are incorrect and we want to return to login form."""
        self.clear_widgets()
        if self.login_page is None:
            self.login_page = LoginForm()
        self.add_widget(self.login_page)
        return

    def show_mob_only_sub_details(self, subscription):
        # Probably Obsolete
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

    class M2FActivateSwitch(Switch):
        debug.p("FUNC ::::    MexSwitchPage.M2FActivateSwitch")
            
        pass

    class F2MActivateSwitch(Switch):
        debug.p("FUNC ::::    MexSwitchPage.F2MActivateSwitch")
            
        pass

    debug.p("CLASS ::::    MexSwitchPage")
    fixed_number = StringProperty()
    fixed_number_href = StringProperty()
    mobile_number = StringProperty()
    mobile_number_href = StringProperty()
    MO_SUB = BooleanProperty()
    FT_SUB = BooleanProperty()
    m2fstate = ObjectProperty(M2FActivateSwitch)
    f2mstate = ObjectProperty(F2MActivateSwitch)
    username_input = ObjectProperty()
    password_input = ObjectProperty()
    subscription_id = StringProperty()
    lastModified_Date = ""
    createdDate = ""
    subscription_href = StringProperty()



    def __init__(self, **kwargs):
        debug.p("FUNC ::::    MexSwitchPage.__init__")

        return

    

    def getSubscriptionMexSettingsMobileOnly(self, username, password, subscription):
        debug.p("FUNC ::::    MexSwitchPage.getSubscriptionMexSettings")
        debug.p("FUNC: getSubscriptionMexSettings ++++++++++++++++++++++++++++++++++++++++")

        self.subscription_href = subscription
        self.username_input = username
        self.password_input = password
        details = cie_connect.get_mobile_only_sub_details(username.text, password.text,subscription)
        debug.p(details)

        self.subscription_id = details['id']
        self.lastModified_Date = details['lastModified']
        self.createdDate = details['created']
        for val in details['attributes']:
            if val['id'] == 'mobExSub':
                self.MO_SUB = val['value']
            if val['id'] == 'cliMap':
                self.m2fstate.active= val['value']
        
        debug.p(self.MO_SUB)
        debug.p(self.m2fstate.active)
        
        return

    def getSubscriptionMexSettingsFixedMobile(self, username, password, subscription):
        debug.p("FUNC ::::    MexSwitchPage.getSubscriptionMexSettingsFixedMobile")
        debug.p(subscription)
        self.subscription_href = subscription
        self.username_input = username
        self.password_input = password
        details = cie_connect.get_mobile_only_sub_details(username.text, password.text,subscription)
        debug.p(details)

        self.subscription_id = details['id']
        self.lastModified_Date = details['lastModified']
        self.createdDate = details['created']
        for val in details['attributes']:
            if val['id'] == 'mobExSub':
                if val['value'] == None:
                    self.MO_SUB = False
                else:
                    self.MO_SUB = val['value']

            if val['id'] == 'cliMap' and self.MO_SUB == True:
                self.m2fstate.active= val['value']
            else:
                self.m2fstate.active= False

            if val['id'] == 'mobExTSub':
                if val['value'] == None:
                    self.FT_SUB = False
                else:
                    self.FT_SUB = val['value']
            if val['id'] == 'cdpnMap' and self.FT_SUB == True:
                self.f2mstate.active = val['value']
            else:
                self.f2mstate.active = False

        print ("\n\n\n\n\n\n\n\n\n\n")
        print self.MO_SUB
        print self.m2fstate.active
        print self.FT_SUB
        print self.f2mstate.active
        print self.username_input.text
        print self.subscription_id
        print self.lastModified_Date

        return True

    def setF2MDiversionActive(self):
        debug.p("FUNC ::::    MexSwitchPage.setF2MDiversionActive")
        print "**********ACTIVATE F2M Divert          " + str(self.f2mstate.active)

        results = cie_connect.changeMexF2MState(self.username_input.text, self.password_input.text, 
            self.subscription_href, self.f2mstate.active, self.lastModified_Date, 
            self.createdDate, self.subscription_id )

        print results

        return

    def setM2FPresentationActive(self):
        debug.p("FUNC ::::    MexSwitchPage.setM2FPresentationActive")
        print "###################ACTIVATE M2F Presentation" + str(self.m2fstate.active)
        
        results = cie_connect.changeMexM2FState(self.username_input.text, self.password_input.text, 
            self.subscription_href, self.m2fstate.active, self.lastModified_Date,
            self.createdDate, self.subscription_id )

        print results
        return
    pass


class SubscriptionPage(BoxLayout):
    debug.p("CLASS :::::: SubscriptionPage")
    pass


class SubscriptionButton(ListItemButton):
    debug.p("CLASS :::::: SubscriptionButton")
    pass



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


class MexApp(App):
    debug.p("CLASS ::::    MexApp")
    pass

    
    def on_pause(self):
        debug.p("FUNC ::::    MexRoot.on_pause")
        return True


if __name__ =='__main__':
    MexApp().run()



