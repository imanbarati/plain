from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from PIL import Image as PILImage
import os


class DraggableSignature(Widget):
    def __init__(self, signature_path, **kwargs):
        super().__init__(**kwargs)
        self.signature_path = signature_path
        try:
            # Load signature image
            with self.canvas:
                self.rect = Rectangle(source=self.signature_path, size=(100, 50), pos=self.pos)
            self.bind(pos=self.update_position)
        except Exception as e:
            print(f"Error loading signature: {e}")

    def update_position(self, *args):
        self.rect.pos = self.pos

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):  # Register touch events only within widget bounds
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):  # Allow dragging only if touch is within bounds
            self.center = touch.pos
            return True
        return super().on_touch_move(touch)


class SignatureApp(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # File chooser
        self.file_chooser = FileChooserIconView(size_hint=(1, 0.5), pos_hint={'x': 0, 'y': 0.5})
        self.add_widget(self.file_chooser)

        # Buttons for functionality
        self.button_layout = BoxLayout(size_hint=(1, 0.1), pos_hint={'x': 0, 'y': 0.4})
        self.add_widget(self.button_layout)

        self.open_button = Button(text="Open Base Image")
        self.open_button.bind(on_release=self.open_base_image)
        self.button_layout.add_widget(self.open_button)

        self.add_signature_button = Button(text="Add Signature")
        self.add_signature_button.bind(on_release=self.add_signature)
        self.button_layout.add_widget(self.add_signature_button)

        self.save_button = Button(text="Save Image", disabled=True)
        self.save_button.bind(on_release=self.save_image)
        self.button_layout.add_widget(self.save_button)

        # Toggle File Chooser
        self.toggle_file_chooser_button = Button(text="Show File Chooser", size_hint=(1, 0.1), pos_hint={'x': 0, 'y': 0.3})
        self.toggle_file_chooser_button.bind(on_release=self.toggle_file_chooser)
        self.add_widget(self.toggle_file_chooser_button)

        # Base image widget and signature widgets
        self.base_image_widget = None
        self.base_image_path = None
        self.signature_widgets = []

    def toggle_file_chooser(self, instance):
        if self.file_chooser.parent:
            self.remove_widget(self.file_chooser)
        else:
            self.add_widget(self.file_chooser)

    def open_base_image(self, instance):
        selected = self.file_chooser.selection
        if selected:
            self.base_image_path = selected[0]
            print(f"Base image loaded: {self.base_image_path}")
            try:
                self.remove_widget(self.file_chooser)  # Hide file chooser

                if self.base_image_widget:
                    self.remove_widget(self.base_image_widget)

                self.base_image_widget = KivyImage(source=self.base_image_path, size_hint=(1, 0.4), pos_hint={'x': 0, 'y': 0})
                self.add_widget(self.base_image_widget)
                self.save_button.disabled = False
            except Exception as e:
                print(f"Error displaying base image: {e}")

    def add_signature(self, instance):
        selected = self.file_chooser.selection
        if selected:
            signature_path = selected[0]
            print(f"Signature image added: {signature_path}")
            try:
                # Keep file chooser for adding multiple signatures
                sig_widget = DraggableSignature(signature_path, pos=(0, 0), size=(100, 50))
                self.add_widget(sig_widget)
                self.signature_widgets.append(sig_widget)
            except Exception as e:
                print(f"Error adding signature: {e}")

    def save_image(self, instance):
        if self.base_image_path:
            try:
                base_image = PILImage.open(self.base_image_path).convert("RGBA")
                for sig_widget in self.signature_widgets:
                    sig_image = PILImage.open(sig_widget.signature_path).convert("RGBA")
                    x, y = map(int, sig_widget.pos)
                    sig_image_resized = sig_image.resize((100, 50))
                    base_image.paste(sig_image_resized, (x, y), sig_image_resized)

                output_path = os.path.expanduser("~/final_image_with_signatures.png")
                base_image.save(output_path)
                print(f"Final image saved: {output_path}")
            except Exception as e:
                print(f"Error saving image: {e}")


class InteractiveSignatureApp(App):
    def build(self):
        return SignatureApp()


if __name__ == "__main__":
    InteractiveSignatureApp().run()
