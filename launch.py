import tkinter as tk
from tkinter import scrolledtext, Label
from PIL import Image, ImageTk
import requests
from io import BytesIO
from main import MainApp

class RoundButton(tk.Canvas):
    def __init__(self, parent, width, height, corner_radius, text="", command=None):
        tk.Canvas.__init__(self, parent, width=width, height=height, highlightthickness=0)
        self.command = command

        self.round_rectangle(0, 0, width-1, height-1, corner_radius, fill="lightgray")
        self.create_text(width/2, height/2, text=text, fill="black")
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def round_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        self.create_polygon(points, **kwargs, smooth=True)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.itemconfig(1, fill="gray")  # Change the rectangle color

    def _on_leave(self, event):
        self.itemconfig(1, fill="lightgray")  # Change it back

class AppGUI:
    def __init__(self, root, app_logic):
        self.app_logic = app_logic
        self.setup_ui(root)

    def setup_ui(self, root):
        root.title("API操作界面")
        left_frame = tk.Frame(root)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.input_prompt = scrolledtext.ScrolledText(left_frame, width=50, height=4)
        self.input_prompt.pack(pady=5)

        button_frame = tk.Frame(left_frame)
        button_frame.pack(pady=5)

        self.btn_generate_text = RoundButton(button_frame, width=100, height=30, corner_radius=10, text="生成文本", command=self.on_generate_text)
        self.btn_generate_text.grid(row=0, column=0, padx=5)

        self.btn_generate_image = RoundButton(button_frame, width=100, height=30, corner_radius=10, text="生成图片", command=self.on_generate_image)
        self.btn_generate_image.grid(row=0, column=1, padx=5)

        self.btn_text_to_image = RoundButton(button_frame, width=100, height=30, corner_radius=10, text="文本到图片", command=self.on_text_to_image)
        self.btn_text_to_image.grid(row=0, column=2, padx=5)

        self.output_area = scrolledtext.ScrolledText(left_frame, width=50, height=10)
        self.output_area.pack(pady=5)

        # 图片显示区域
        self.image_frame = tk.Frame(root, width=1024, height=1024)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.image_label = Label(self.image_frame)
        self.image_label.pack(expand=True)

    def on_generate_text(self):
        prompt = self.input_prompt.get("1.0", tk.END).strip()
        if prompt:
            text_output = self.app_logic.generate_text(prompt)
            self.display_output(text_output)

    def on_generate_image(self):
        prompt = self.input_prompt.get("1.0", tk.END).strip()
        if prompt:
            image_url = self.app_logic.generate_image(prompt)
            self.display_output(f"Image URL: {image_url}")
            self.display_image(image_url)

    def on_text_to_image(self):
        self.on_generate_image()  # 直接调用生成图片的方法

    def display_output(self, message):
        self.output_area.configure(state='normal')
        self.output_area.delete(1.0, tk.END)  # Clear the output area
        self.output_area.insert(tk.END, message + "\n")
        self.output_area.configure(state='disabled')

    def display_image(self, image_url):
        try:
            response = requests.get(image_url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((1024, 1024), Image.ANTIALIAS)  # Resize if necessary
            photo = ImageTk.PhotoImage(img, master=self.image_frame)
            self.image_label.config(image=photo)
            self.image_label.image = photo  # keep a reference!
        except Exception as e:
            self.display_output(f"Error displaying image: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app_logic = MainApp()
    app_gui = AppGUI(root, app_logic)
    root.mainloop()