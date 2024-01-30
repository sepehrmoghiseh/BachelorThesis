from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt

class MatplotlibApp(App):
    def build(self):
        # Create a Matplotlib figure and plot
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3, 4, 5], [2, 4, 6, 8, 10])

        # Create a Kivy layout
        layout = BoxLayout(orientation='vertical')

        # Create a Matplotlib canvas
        canvas = FigureCanvasKivyAgg(fig)
        layout.add_widget(canvas)

        return layout

if __name__ == '__main__':
    MatplotlibApp().run()
