from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider


class MainApp(App):
    def build(self):
        # Root layout
        root_layout = BoxLayout(orientation="horizontal")

        # Main view for webcam
        webcam_label = Label(text="Webcam Stream Goes Here", size_hint=(0.75, 1))
        root_layout.add_widget(webcam_label)

        # Settings layout
        settings_layout = BoxLayout(orientation="vertical", size_hint=(0.25, 1))

        # Adding 4 buttons
        for i in range(4):
            settings_layout.add_widget(Button(text=f"Setting {i+1}"))

        # Adding 4 horizontal sliders
        for i in range(4):
            settings_layout.add_widget(Slider(orientation="horizontal"))

        root_layout.add_widget(settings_layout)

        return root_layout


if __name__ == "__main__":
    MainApp().run()
