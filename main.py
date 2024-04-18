import matplotlib.pyplot as plt
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image, AsyncImage
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton, MDFloatingActionButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.textfield import MDTextField

from garden_matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from service import *


class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', spacing=22, padding=[20, 167, 80, 10])
        background_image = Image(source='pics/output.jpg', allow_stretch=True, keep_ratio=False)
        self.add_widget(background_image)
        self.layout.size_hint = (None, None)
        self.layout.width = 300  # Adjust the width as needed
        self.layout.height = 300  # Adjust the height as needed
        self.layout.pos_hint = {'center_x': 0.52, 'center_y': 0.6}

        # Loading spinner container
        loading_container = MDBoxLayout(orientation='vertical', spacing=10)
        self.loading_spinner = MDSpinner(size_hint=(None, None), size=(200, 200), opacity=0)
        loading_container.add_widget(self.loading_spinner)
        self.layout.add_widget(loading_container)
        self.add_widget(self.layout)
        self.card = MDCard(orientation='vertical', size_hint_y=None, height="40dp", md_bg_color=(0.154, 0.14, 0.33))

        # Title label (initially invisible)
        self.title_label = MDLabel(text='Login', font_size='24sp', opacity=0, pos_hint={'x': 0.38, 'y': 0.5})
        self.card.add_widget(self.title_label)
        # Username input (initially invisible)
        self.username_input = TextInput(hint_text='Username', multiline=False, line_height=1.5, size_hint=(None, None),
                                        width=200, height=50, opacity=0)

        # Password input (initially invisible)
        self.password_input = TextInput(hint_text='Password', password=True, size_hint=(None, None),
                                        width=200, opacity=0, height=50, multiline=False)

        # Login button with mouse hover animation (initially invisible)
        self.login_button = MDRaisedButton(text='Login', size_hint=(None, None), width=200, height=50, opacity=0,
                                           pos_hint={'x': 0.35, 'y': 0.5})
        self.login_button.bind(on_press=self.login_to_openwrt)
        self.login_button.bind(on_enter=self.on_button_enter)
        self.login_button.bind(on_leave=self.on_button_leave)

        # Start the loading animation
        self.start_loading_animation()

    def start_loading_animation(self):
        # Set the initial position of the loading spinner to the center
        # Set the initial opacity to 0 (invisible)
        self.loading_spinner.opacity = 0

        # Display the loading spinner for 3 seconds
        Animation(opacity=1, duration=1, t='out_quad').start(self.loading_spinner)
        Clock.schedule_once(self.fade_out_loading_spinner, 3)

    def fade_out_loading_spinner(self, dt):
        # Fade out the loading spinner
        Animation(opacity=0, duration=1, t='out_quad').start(self.loading_spinner)

        # Delay before fading in other components
        Clock.schedule_once(self.fade_in_components, 1)

    def fade_in_components(self, dt):
        # Fade in other components
        Animation(duration=2).start(self)
        self.layout.add_widget(self.card)
        self.layout.add_widget(self.username_input)
        self.layout.add_widget(self.password_input)
        self.layout.add_widget(self.login_button)
        self.layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        Animation(opacity=1, duration=1, t='out_quad').start(self.card)
        Animation(opacity=1, duration=1, t='out_quad').start(self.title_label)

        Animation(opacity=1, duration=1, t='out_quad').start(self.username_input)
        Animation(opacity=1, duration=1, t='out_quad').start(self.password_input)
        Animation(opacity=1, duration=1, t='out_quad').start(self.login_button)

    def login_to_openwrt(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        try:
            result_data = login(username, password)

            # Check if login was successful
            if result_data is not None:
                self.show_popup(self, "yes")
                self.successful_login(result_data)

            else:
                self.show_popup(self, "no")

        except requests.RequestException as e:
            self.show_popup(self, "error")

    def successful_login(self, result_data):
        # Get the ScreenManager
        app = MDApp.get_running_app()
        app.result_data = result_data
        self.manager.current = 'home'

    def on_button_enter(self, instance):
        # Mouse hover animation: change background color on enter
        anim = Animation(background_color=(0.4, 0.7, 1, 1), duration=0.2)
        anim.start(instance)

    def on_button_leave(self, instance):
        # Mouse hover animation: restore background color on leave
        anim = Animation(background_color=(0.2, 0.6, 1, 1), duration=0.2)
        anim.start(instance)

    def show_popup(self, instance, message):
        # Create a Popup with some content
        popup_content = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        if message == "yes":
            popup_content.add_widget(MDLabel(text='Login Successful!'))
        elif message == "no":
            popup_content.add_widget(MDLabel(text='Login Unsuccessful!'))
        else:
            popup_content.add_widget(MDLabel(text='Error!'))
        popup = Popup(title='Login Status', content=popup_content, size_hint=(None, None), size=(300, 200))
        anim_in = Animation(opacity=1, duration=2)
        anim_in.start(popup)
        Clock.schedule_once(lambda dt: anim_in.start(popup), 0)

        # Schedule the fade-out animation after two seconds
        Clock.schedule_once(lambda dt: self.fade_out_popup(popup), 4)

        popup.open()

    def fade_out_popup(self, popup):
        # Fade-out animation (duration: 2 seconds)
        anim_out = Animation(opacity=0, duration=2)
        anim_out.start(popup)


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.check = 0
        self.flag = 0

        # Create the main screen
        self.lay = MDBoxLayout(orientation='horizontal')
        # Create a BoxLayout with horizontal orientation
        self.sub_layout = MDBoxLayout(orientation='vertical', size_hint=(0.4, 1), padding=[10, 15, 10, 30], spacing=5)
        self.buttons = MDBoxLayout(orientation='horizontal', size_hint=(1, None), padding=[10, 15, 10, 30], spacing=20)
        self.layout = MDBoxLayout(orientation='vertical', size_hint=(0.2, 1), padding=[10, 15, 10, 30], spacing=10)
        self.spacer = MDBoxLayout(orientation='vertical', size_hint=(1, 0.8))
        self.lay.add_widget(self.sub_layout)
        self.lay.add_widget(self.layout)
        self.home = MDFloatingActionButton(icon="pics/25694.png", on_press=self.login_to_openwrt,
                                           md_bg_color=(0.154, 0.14, 0.33))
        background_image = Image(source='pics/output.jpg', allow_stretch=True, keep_ratio=False)
        self.right_menu()
        # Create a ScrollView
        self.scroll_view = MDScrollView()
        # Create a BoxLayout to hold the cards
        self.box_layout = MDBoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=[10, 15, 10, 30],
                                      opacity=0.8, size_hint=(1, None))
        self.box_layout.bind(minimum_height=self.box_layout.setter('height'))

        # Add the BoxLayout to the ScrollView
        self.scroll_view.add_widget(self.box_layout)
        self.buttons.add_widget(self.home)
        # Add the ScrollView to the main layout
        self.sub_layout.add_widget(self.buttons)
        self.sub_layout.add_widget(self.scroll_view)
        # Add three MDCards to the BoxLayout

        # Add the main layout to the screen
        self.add_widget(background_image)
        self.add_widget(self.lay)

    def on_enter(self, *args):
        if self.flag == 0 or what_device_is_connected(self.result_data) != self.connected:
            app = MDApp.get_running_app()
            self.result_data = app.result_data
            self.info()

            self.connected = what_device_is_connected(self.result_data)
            self.addconnected(self.connected)
            self.flag = self.flag + 1

    def addconnected(self, connected):
        if self.check > 0:
            self.box_layout.clear_widgets()
            self.check = 0
        for key, values in connected.items():
            if 'ipv4' in connected[key]:
                self.card1 = MDCard(orientation='vertical', size_hint_y=None, spacing=5, height="185dp",
                                    padding=[5, 5, 5, 5])
                self.text_input1 = MDTextField(
                    hint_text="device",
                    text=key,
                    readonly=True,
                    multiline=False
                )

                self.text_input2 = MDTextField(
                    hint_text="ip",
                    text=connected[key]['ipv4'],
                    readonly=True,
                    multiline=False
                )
                if findName(key) != None:
                    self.text_input3 = MDTextField(
                        hint_text="name",
                        text=findName(key),
                        readonly=True,
                        multiline=False
                    )
                    self.card1.add_widget(self.text_input3)
                    self.card1.height = "225dp"
                self.optionBox = MDBoxLayout(orientation='horizontal', size_hint=(1, 0.3), spacing=4)
                self.edit = MDRectangleFlatButton(text="edit name",
                                                  md_bg_color=(0.154, 0.14, 0.33), size_hint=(3, None))
                self.delete = MDRectangleFlatButton(text="delete name",
                                                    md_bg_color=(0.154, 0.14, 0.33), size_hint=(3, None))
                self.disconnect = MDRectangleFlatButton(text="disconnect the devices",
                                                        md_bg_color=(0.154, 0.14, 0.33), size_hint=(3, None))
                self.optionBox.add_widget(self.edit)
                self.optionBox.add_widget(self.delete)
                self.optionBox.add_widget(self.disconnect)

                self.card1.add_widget(self.text_input1)
                self.card1.add_widget(self.text_input2)
                self.card1.add_widget(self.optionBox)
                self.edit.bind(on_press=self.show_popup)
                self.delete.bind(on_press=self.show_popup_delete)
                self.disconnect.bind(on_press=self.show_popup_disconnect)

                # Add the MDCard to the BoxLayout
                self.box_layout.add_widget(self.card1)
        self.check = self.check + 1

    def show_popup_disconnect(self, instance):
        self.options = MDBoxLayout(orientation='vertical', spacing=4)

        self.alert = MDTextField(

            text="are you sure you want to disconnect the device\n: " + instance.parent.parent.children[2].text + " ?",
            multiline=True, foreground_color=get_color_from_hex("#FFFFFF"))
        self.optionBox = MDBoxLayout(orientation='horizontal', size_hint=(1, 0.3), spacing=4)
        self.yes = MDRectangleFlatButton(text="Yes",
                                         md_bg_color=(0.154, 0.14, 0.33), size_hint=(4, None))
        self.no = MDRectangleFlatButton(text="No",
                                        md_bg_color=(0.154, 0.14, 0.33), size_hint=(4, None))
        self.optionBox.add_widget(self.yes)
        self.optionBox.add_widget(self.no)
        self.options.add_widget(self.alert)
        self.options.add_widget(self.optionBox)
        self.popup1 = Popup(title=instance.parent.parent.children[2].text, content=self.options, size_hint=(None, None),
                            size=(450, 200))
        self.no.bind(on_release=self.popup1.dismiss)
        self.yes.bind(on_press=self.disconnectDevice)
        anim_in = Animation(opacity=1, duration=2)
        anim_in.start(self.popup1)
        self.popup1.open()

    def disconnectDevice(self, instance):
        print(instance.parent.parent.children[1].text[48:-2].lower())
        disconnect(instance.parent.parent.children[1].text[48:-2])
        self.popup1.dismiss()
        self.connected = what_device_is_connected(self.result_data)
        self.addconnected(self.connected)

    def login_to_openwrt(self, *args):
        self.manager.current = "home"

    def update_date(self, interval):
        # Update the text of the MDTextField with the current date and time
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.date.text = current_date

    def right_menu(self):
        self.change_pass = MDRectangleFlatButton(text="change password", size_hint=(1, None),
                                                 md_bg_color=(0.154, 0.14, 0.33), opacity=0.94)
        self.speedtest = MDRectangleFlatButton(text="speed test", size_hint=(1, None), md_bg_color=(0.154, 0.14, 0.33))
        self.button3 = MDRectangleFlatButton(text="Login History", size_hint=(1, None), md_bg_color=(0.154, 0.14, 0.33))
        self.button4 = MDRectangleFlatButton(text="speedtest History", size_hint=(1, None),
                                             md_bg_color=(0.154, 0.14, 0.33))
        self.button5 = MDRectangleFlatButton(text="user speedtest History", size_hint=(1, None),
                                             md_bg_color=(0.154, 0.14, 0.33))
        self.button6 = MDRectangleFlatButton(text="user usage History", size_hint=(1, None),
                                             md_bg_color=(0.154, 0.14, 0.33))
        self.button7 = MDRectangleFlatButton(text="data usage", size_hint=(1, None),
                                             md_bg_color=(0.154, 0.14, 0.33))
        self.speedtest.bind(on_press=self.speedtest_method)
        self.change_pass.bind(on_press=self.change_password)
        self.button3.bind(on_press=self.loginHistory)
        self.button4.bind(on_press=self.speedtestHistory)
        self.button5.bind(on_press=self.userSpeedtestHistory)
        self.button6.bind(on_press=self.userUsageHistory)
        self.button7.bind(on_press=self.dataUsageHistory)

        self.layout.add_widget(self.change_pass)
        self.layout.add_widget(self.speedtest)
        self.layout.add_widget(self.button3)
        self.layout.add_widget(self.button4)
        self.layout.add_widget(self.button5)
        self.layout.add_widget(self.button6)
        self.layout.add_widget(self.button7)

        self.layout.add_widget(self.spacer)

    def info(self):
        if self.check > 0:
            self.spacer.clear_widgets()
            self.check = 0
        user = getUser()
        self.infos = MDCard(orientation='vertical', size_hint_y=None, spacing=5, height="130dp", padding=[5, 5, 5, 5],
                            md_bg_color=(0.154, 0.14, 0.33))

        # Get the current date and time
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        self.user = MDTextField(
            hint_text="user",
            text=str(user['name']) + ', welcome!',
            readonly=True,
            multiline=False,
            foreground_color=get_color_from_hex("#FFFFFF")
        )

        self.date = MDTextField(
            hint_text="date",
            text=str(formatted_datetime),
            readonly=True,
            multiline=False,
            foreground_color=get_color_from_hex("#F32FFF")
        )

        self.infos.add_widget(self.user)
        self.infos.add_widget(self.date)
        self.spacer.add_widget(self.infos)
        self.check = self.check + 1

        Clock.schedule_interval(self.update_date, 1)

    def change_password(self, instance):
        # Get the ScreenManager
        self.manager.current = 'changePass'

    def loginHistory(self, instance):
        # Get the ScreenManager
        self.manager.current = 'history'

    def speedtest_method(self, instance):
        # Get the ScreenManager
        self.manager.current = 'speedtest'

    def speedtestHistory(self, instance):
        # Get the ScreenManager
        self.manager.current = 'speedtestHistory'

    def userSpeedtestHistory(self, instance):
        # Get the ScreenManager
        self.manager.current = 'userSpeedtestHistory'

    def userUsageHistory(self, instance):
        # Get the ScreenManager
        self.manager.current = 'userUsageHistory'

    def dataUsageHistory(self, instance):
        # Get the ScreenManager
        self.manager.current = 'dataUsage'

    def show_popup(self, instance):
        self.card = MDCard(orientation='vertical', size_hint_y=None, spacing=5, height="100dp",
                           padding=[5, 5, 5, 5])
        # Create a Popup with some content
        self.user = MDTextField(
            hint_text="NAME",
            multiline=False, foreground_color=get_color_from_hex("#FFFFFF"))
        self.card.add_widget(self.user)
        self.submit = MDRectangleFlatButton(text="SUBMIT",
                                            md_bg_color=(0.154, 0.14, 0.33), size_hint=(1, None))
        self.card.add_widget(self.submit)
        self.submit.bind(on_press=self.editName)
        self.popup1 = Popup(title=instance.parent.parent.children[2].text, content=self.card, size_hint=(None, None),
                            size=(300, 200))
        anim_in = Animation(opacity=1, duration=2)
        anim_in.start(self.popup1)
        self.popup1.open()

    def show_popup_delete(self, instance):
        self.options = MDBoxLayout(orientation='vertical', spacing=4)

        self.alert = MDTextField(

            text="are you sure you want\n to delete the name for " + instance.parent.parent.children[2].text + " ?",
            multiline=True, foreground_color=get_color_from_hex("#FFFFFF"))
        self.optionBox = MDBoxLayout(orientation='horizontal', size_hint=(1, 0.3), spacing=4)
        self.yes = MDRectangleFlatButton(text="Yes",
                                         md_bg_color=(0.154, 0.14, 0.33), size_hint=(4, None))
        self.no = MDRectangleFlatButton(text="No",
                                        md_bg_color=(0.154, 0.14, 0.33), size_hint=(4, None))
        self.optionBox.add_widget(self.yes)
        self.optionBox.add_widget(self.no)
        self.options.add_widget(self.alert)
        self.options.add_widget(self.optionBox)
        self.popup1 = Popup(title=instance.parent.parent.children[2].text, content=self.options, size_hint=(None, None),
                            size=(450, 200))
        self.no.bind(on_release=self.popup1.dismiss)
        self.yes.bind(on_press=self.deleteName)
        anim_in = Animation(opacity=1, duration=2)
        anim_in.start(self.popup1)
        self.popup1.open()

    def editName(self, instance):

        editName(self.user.text, instance.parent.parent.parent.children[2].text)
        self.popup1.dismiss()

        self.connected = what_device_is_connected(self.result_data)
        self.addconnected(self.connected)

    def deleteName(self, instance):
        deleteName(instance.parent.parent.children[1].text[46:-2])
        self.popup1.dismiss()

        self.connected = what_device_is_connected(self.result_data)
        self.addconnected(self.connected)


class changePassword(MDScreen):
    def __init__(self, *args, **kwargs):
        super(changePassword, self).__init__(*args, **kwargs)
        self.lay2 = MDBoxLayout(orientation='vertical')
        self.background_image = Image(source='pics/output.jpg', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background_image)
        self.home = MDFloatingActionButton(icon="pics/25694.png", on_press=self.login_to_openwrt,
                                           md_bg_color=(0.154, 0.14, 0.33))
        self.buttons = MDBoxLayout(orientation='horizontal', size_hint=(1, None), padding=[10, 15, 10, 30], spacing=20)
        self.buttons.add_widget(self.home)
        self.lay2.add_widget(self.buttons)
        self.change()

    def change(self):
        self.changeLayout = MDBoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.3))
        self.spacing = MDBoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.5))
        self.box = MDCard(orientation='vertical', spacing=5, height="130dp", padding=[5, 5, 5, 5],
                          md_bg_color=(0.154, 0.14, 0.33), pos_hint={'x': 0.35, 'y': 0.3}, size_hint=(0.3, None),
                          opacity=0.94)
        self.password = MDTextField(
            hint_text="new password",
            multiline=False,
            password=True,
            foreground_color=get_color_from_hex("#FFFFFF"),
        )
        self.confirm = MDTextField(
            hint_text="confirm password",
            multiline=False,
            password=True,
            foreground_color=get_color_from_hex("#FFFFFF"),
            size=(30, 30)
        )
        self.change_pass = MDRectangleFlatButton(text="change password", size_hint=(0.3, None),
                                                 md_bg_color=(0.154, 0.14, 0.33), pos_hint={'x': 0.35, 'y': 0.3}
                                                 , opacity=0.94)
        self.change_pass.bind(on_press=self.changeIt)
        self.box.add_widget(self.password)
        self.box.add_widget(self.confirm)
        self.changeLayout.add_widget(self.box)
        self.changeLayout.add_widget(self.change_pass)
        self.lay2.add_widget(self.changeLayout)
        self.lay2.add_widget(self.spacing)
        self.add_widget(self.lay2)

    def show_popup(self, instance, message):
        # Create a Popup with some content
        popup_content = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        if message == "yes":
            popup_content.add_widget(MDLabel(text='change Successful!'))
        elif message == "no":
            popup_content.add_widget(MDLabel(text='passwords are not a match!'))
        popup = Popup(title='change Status', content=popup_content, size_hint=(None, None), size=(300, 200))
        anim_in = Animation(opacity=1, duration=2)
        anim_in.start(popup)
        Clock.schedule_once(lambda dt: anim_in.start(popup), 0)

        # Schedule the fade-out animation after two seconds
        Clock.schedule_once(lambda dt: self.fade_out_popup(popup), 4)

        popup.open()

    def fade_out_popup(self, popup):
        # Fade-out animation (duration: 2 seconds)
        anim_out = Animation(opacity=0, duration=2)
        anim_out.start(popup)

    def changeIt(self, *args):
        if (self.password.text == self.confirm.text):
            changePasswordService(self.password.text)
            self.show_popup(self, 'yes')
            self.manager.current = "login"

        else:
            self.show_popup(self, 'no')

    def login_to_openwrt(self, *args):
        self.manager.current = "home"


class speedTest(MDScreen):
    def __init__(self, *args, **kwargs):
        super(speedTest, self).__init__(*args, **kwargs)
        self.lay2 = MDBoxLayout(orientation='vertical')
        self.background_image = Image(source='pics/output.jpg', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background_image)
        self.home = MDFloatingActionButton(icon="pics/25694.png", on_press=self.login_to_openwrt,
                                           md_bg_color=(0.154, 0.14, 0.33))
        self.buttons = MDBoxLayout(orientation='horizontal', size_hint=(1, None), padding=[10, 15, 10, 30], spacing=20)
        self.buttons.add_widget(self.home)
        self.lay2.add_widget(self.buttons)
        self.change()

    def change(self):
        self.changeLayout = MDBoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.3))
        self.spacing = MDBoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.5))
        self.box = MDCard(orientation='vertical', spacing=5, height="130dp", padding=[5, 5, 5, 5],
                          md_bg_color=(0.154, 0.14, 0.33), pos_hint={'x': 0.35, 'y': 0.3}, size_hint=(0.3, None),
                          opacity=0.94)
        self.downloadbox = MDTextField(
            hint_text="download",
            multiline=False,
            readonly=True,
            foreground_color=get_color_from_hex("#FFFFFF"),
        )
        self.uploadbox = MDTextField(
            hint_text="upload",
            multiline=False,
            readonly=True,

            foreground_color=get_color_from_hex("#FFFFFF"),
            size=(30, 30)
        )
        self.testrun = MDRectangleFlatButton(text="run a test", size_hint=(0.3, None),
                                             md_bg_color=(0.154, 0.14, 0.33), pos_hint={'x': 0.35, 'y': 0.3}
                                             , opacity=0.94)
        self.testrun.bind(on_press=self.show_popup)
        self.box.add_widget(self.downloadbox)
        self.box.add_widget(self.uploadbox)
        self.changeLayout.add_widget(self.box)
        self.changeLayout.add_widget(self.testrun)
        self.lay2.add_widget(self.changeLayout)
        self.lay2.add_widget(self.spacing)
        self.add_widget(self.lay2)

    def show_popup(self, instance):
        # Create a Popup with some content
        popup_content = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        popup_content.add_widget(AsyncImage(source='pics/34338d26023e5515f6cc8969aa027bca.gif'))
        popup = Popup(title='testing', content=popup_content, size_hint=(None, None), size=(300, 200))
        anim_in = Animation(opacity=1, duration=2)
        anim_in.start(popup)
        Clock.schedule_once(lambda dt: anim_in.start(popup), 0)
        popup.open()
        Clock.schedule_once(lambda dt: self.test(popup), 3)

    def fade_out_popup(self, popup):
        # Fade-out animation (duration: 2 seconds)
        anim_out = Animation(opacity=0, duration=2)
        anim_out.start(popup)

    def pop(self, *args):
        popup_content = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        popup_content.add_widget(MDLabel(text='test Successful!'))
        popup = Popup(title='change Status', content=popup_content, size_hint=(None, None), size=(300, 200))
        popup.open()
        Clock.schedule_once(lambda dt: self.test(popup), 1)

    def test(self, popup, *args):
        self.download, self.upload = run_speed_test()
        self.downloadbox.text = str(self.download)
        self.uploadbox.text = str(self.upload)
        Clock.schedule_once(lambda dt: self.fade_out_popup(popup), 0)

    def login_to_openwrt(self, *args):
        self.manager.current = "home"


class loginHistory(MDScreen):
    def __init__(self, *args, **kwargs):
        super(loginHistory, self).__init__(*args, **kwargs)
        self.background_image = Image(source='pics/output.jpg', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background_image)

        self.box_layout = MDBoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=[10, 15, 10, 30],
                                      opacity=0.8, size_hint=(1, None))
        self.home = MDFloatingActionButton(icon="pics/25694.png",
                                           md_bg_color=(0.154, 0.14, 0.33), on_press=self.login_to_openwrt)
        self.buttons = MDBoxLayout(orientation='horizontal', size_hint=(1, None), padding=[10, 15, 10, 30], spacing=20)
        self.buttons.add_widget(self.home)
        self.lay2 = MDBoxLayout(orientation='vertical')
        self.lay2.add_widget(self.buttons)
        self.spacer = MDBoxLayout(orientation='vertical', size_hint=(1, 0.8))
        self.scroll_view = MDScrollView()
        self.scroll_view.add_widget(self.box_layout)
        self.box_layout.bind(minimum_height=self.box_layout.setter('height'))

        self.lay2.add_widget(self.scroll_view)
        self.add_widget(self.lay2)

    def on_enter(self, *args):
        self.addconnected()

    def addconnected(self):
        self.box_layout.clear_widgets()
        report = reportLogin()
        lines = report.splitlines()

        for line in lines:
            first = line.find("|")
            second = line.find("|", first + 1)
            self.card = MDCard(orientation='vertical', size_hint_y=None, spacing=5, height="130dp",
                               padding=[5, 5, 5, 5])
            self.text_input1 = MDTextField(
                hint_text="ip",
                text=line[first + 1:second],
                readonly=True,
                multiline=False
            )

            self.text_input2 = MDTextField(
                hint_text="date",
                text=line[second + 2:],
                readonly=True,
                multiline=False
            )

            self.card.height = '130dp'

            self.card.add_widget(self.text_input1)
            self.card.add_widget(self.text_input2)
            # Add the MDCard to the BoxLayout
            self.box_layout.add_widget(self.card)

    def login_to_openwrt(self, *args):
        self.manager.current = "home"


class speedtestHistory(MDScreen):
    def __init__(self, *args, **kwargs):
        super(speedtestHistory, self).__init__(*args, **kwargs)
        self.uploads = None
        self.speeds = None
        self.times = None
        # Create a Matplotlib figure and plot

    def on_enter(self, *args):
        fig, ax = plt.subplots()

        # Assuming speedtestGateWay() returns two lists of timestamps and speeds
        self.times, self.speeds, self.uploads = speedtestGateWay()
        bar_width = 0.35
        bar_positions_download = [i - bar_width / 2 for i in range(len(self.times))]
        # Convert timestamps to Matplotlib date format

        # Plot the data
        ax.bar(bar_positions_download, self.speeds, width=0.4, align='center', label='Download Speeds', color='blue',
               alpha=0.7)
        ax.bar(bar_positions_download, self.uploads, width=0.4, align='edge', label='Upload Speeds', color='orange',
               alpha=0.7)
        ax.set_xticks(range(len(self.times)))
        ax.set_xticklabels([date.strftime("%Y-%m-%d %H:%M:%S") for date in self.times], rotation=45, ha="right")

        ax.legend()
        # Create a Kivy layout
        layout = BoxLayout(orientation='vertical')

        # Create a Matplotlib canvas
        canvas = FigureCanvasKivyAgg(fig)
        layout.add_widget(canvas)
        turn_back_button = MDRaisedButton(text='Turn Back', on_press=self.turn_back)
        layout.add_widget(turn_back_button)
        self.add_widget(layout)
    def turn_back(self, instance):
        # Handle the "Turn Back" button press here
        self.manager.current = "home"


class userSpeedtestHistory(MDScreen):
    def __init__(self, *args, **kwargs):
        super(userSpeedtestHistory, self).__init__(*args, **kwargs)
        self.uploads = None
        self.speeds = None
        self.times = None
        # Create a Matplotlib figure and plot

    def on_enter(self, *args):
        fig, ax = plt.subplots()

        # Assuming speedtestGateWay() returns two lists of timestamps and speeds
        self.times, self.speeds, self.uploads = userSpeedMat()
        bar_width = 0.35
        bar_positions_download = [i - bar_width / 2 for i in range(len(self.times))]
        # Convert timestamps to Matplotlib date format

        # Plot the data
        ax.bar(bar_positions_download, self.speeds, width=0.4, align='center', label='Download Speeds', color='blue',
               alpha=0.7)
        ax.bar(bar_positions_download, self.uploads, width=0.4, align='edge', label='Upload Speeds', color='orange',
               alpha=0.7)
        ax.set_xticks(range(len(self.times)))
        ax.set_xticklabels([date.strftime("%Y-%m-%d %H:%M:%S") for date in self.times], rotation=45, ha="right")

        ax.legend()
        # Create a Kivy layout
        layout = BoxLayout(orientation='vertical')

        # Create a Matplotlib canvas
        canvas = FigureCanvasKivyAgg(fig)
        layout.add_widget(canvas)
        turn_back_button = MDRaisedButton(text='Turn Back', on_press=self.turn_back)
        layout.add_widget(turn_back_button)
        self.add_widget(layout)

    def turn_back(self, instance):
        # Handle the "Turn Back" button press here
        self.manager.current = "home"


class userUsageHistory(MDScreen):
    def __init__(self, *args, **kwargs):
        super(userUsageHistory, self).__init__(*args, **kwargs)
        self.speeds = None
        self.times = None
        # Create a Matplotlib figure and plot

    def convert_to_minutes(self, seconds):
        return seconds / 60.0

    def on_enter(self, *args):
        self.times, self.speeds = usage()
        fig, ax = plt.subplots()
        times_in_minutes = [self.convert_to_minutes(sec) for sec in self.times]
        y_unit = 'Minutes' if max(times_in_minutes) > 60 else 'Seconds'
        ax.bar(self.speeds, times_in_minutes, color='blue', label=f'Usage Time ({y_unit})', alpha=0.7, width=0.4)
        ax.set_xticks(self.speeds)
        ax.set_xticklabels(self.speeds, rotation=45, ha='right')

        canvas = FigureCanvasKivyAgg(fig)
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(canvas)

        # Create a Matplotlib canvas
        turn_back_button = MDRaisedButton(text='Turn Back', on_press=self.turn_back)
        self.layout.add_widget(turn_back_button)
        self.add_widget(self.layout)

    def turn_back(self, instance):
        # Handle the "Turn Back" button press here
        self.manager.current = "home"


class dataUsage(MDScreen):
    def __init__(self, *args, **kwargs):
        super(dataUsage, self).__init__(*args, **kwargs)
        self.data = None
        self.times = None
        # Create a Matplotlib figure and plot

    def on_enter(self, *args):
        fig, ax = plt.subplots()

        # Assuming speedtestGateWay() returns two lists of timestamps and speeds
        self.times, self.data = data_usage()
        bar_width = 0.35
        bar_positions_download = [i - bar_width / 2 for i in range(len(self.times))]
        # Convert timestamps to Matplotlib date format

        # Plot the data
        ax.bar(bar_positions_download, self.data, width=0.4, align='center', label='Total Speeds', color='blue',
               alpha=0.7)
        ax.set_xticks(range(len(self.times)))
        ax.set_xticklabels([date.strftime("%Y-%m-%d") for date in self.times], rotation=45, ha="right")

        ax.legend()
        # Create a Kivy layout
        layout = BoxLayout(orientation='vertical')

        # Create a Matplotlib canvas
        canvas = FigureCanvasKivyAgg(fig)
        layout.add_widget(canvas)
        turn_back_button = MDRaisedButton(text='Turn Back', on_press=self.turn_back)
        layout.add_widget(turn_back_button)
        self.add_widget(layout)

    def turn_back(self, instance):
        # Handle the "Turn Back" button press here
        self.manager.current = "home"


class OpenWRTApp(MDApp):
    def build(self):
        sm = MDScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(changePassword(name='changePass'))
        sm.add_widget(speedTest(name='speedtest'))
        sm.add_widget(loginHistory(name='history'))
        sm.add_widget(speedtestHistory(name='speedtestHistory'))
        sm.add_widget(userSpeedtestHistory(name='userSpeedtestHistory'))
        sm.add_widget(userUsageHistory(name='userUsageHistory'))
        sm.add_widget(dataUsage(name='dataUsage'))

        return sm


if __name__ == "__main__":
    OpenWRTApp().run()
