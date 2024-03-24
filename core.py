import tkinter as tk
import cv2
from PIL import Image, ImageTk
import numpy as np


class ImageSegmentationApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry(f'+{1400}+{900}')
        self.root.title("Plane Segmentation App")
        self.button_font = ("Helvetica", 12, "bold")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.canvas = tk.Canvas(height=screen_height // 2 - 10, width=screen_width // 2 - 10, bg="lightblue")
        self.canvas.pack(fill="both", expand=True)

        self.canvas_text = tk.Canvas(height=screen_height // 4 - 10, width=screen_width // 2 - 10, bg="lightblue")
        self.canvas_text.pack(fill="both", expand=True)

        self.image = None
        self.processed_image = None

        self.load_button = tk.Button(self.root,
                                     text="Load Image\n",
                                     command=self.load_image,
                                     font=self.button_font)
        self.load_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.load_button = tk.Button(self.root,
                                     text="Process Image using Canny\n",
                                     command=self.process_image_canny,
                                     font=self.button_font)
        self.load_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.load_button = tk.Button(self.root,
                                     text="Process Image using\npixel-by-pixel transformations",
                                     command=self.process_image_pixel,
                                     font=self.button_font)
        self.load_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def load_image(self):
        file_path = tk.filedialog.askopenfilename(initialdir="./images", title="Select Image",
                                                filetypes=(("JPEG files", "*.jpg"), ("PNG files", "*.png"),
                                                           ("All files", "*.*")))
        if file_path:
            self.image = cv2.imread(file_path)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.display_image(self.image)

    def update_message(self, new_message):
        self.canvas_text.delete("all")

        canvas_width = self.canvas_text.winfo_width()
        canvas_height = self.canvas_text.winfo_height()

        center_x = canvas_width / 2
        center_y = canvas_height / 2
        self.canvas_text.create_text(center_x, center_y,
                                     text=new_message,
                                     fill="black",
                                     font=("Helvetica", 14, "bold"),
                                     justify=tk.CENTER,
                                     anchor=tk.CENTER)

    def resize_image_to_canvas(self, img, canvas_size):
        canvas_width, canvas_height = canvas_size

        img_width, img_height = img.size
        width_ratio = canvas_width / img_width
        height_ratio = canvas_height / img_height
        scaling_factor = min(width_ratio, height_ratio)

        new_width = int(img_width * scaling_factor)
        new_height = int(img_height * scaling_factor)

        return img.resize((new_width, new_height))

    def display_image(self, image):
        if image is None:
            return None
        
        self.canvas_text.delete("all")

        canvas_width = self.canvas_text.winfo_width()
        canvas_height = self.canvas_text.winfo_height()

        center_x = canvas_width / 2
        center_y = canvas_height / 2

        img_pil = Image.fromarray(image).convert("RGB")
        img_pil = self.resize_image_to_canvas(img_pil, (canvas_width, canvas_height))

        self.image_tk = ImageTk.PhotoImage(img_pil)
        self.canvas.create_image(center_x,
                                 center_y,
                                 image=self.image_tk,
                                 anchor=tk.CENTER)

    def process_image_canny(self):
        if self.image is None:
            return None

        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # reduce noise in the image
        image = cv2.GaussianBlur(image, (9, 9), 0)

        kernel = np.ones((5, 5), np.uint8)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)

        edges = cv2.Canny(image, 50, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # create a blank mask to store the segmented objects
        mask = np.zeros_like(self.image)
        fill_color = (0, 255, 0)

        cv2.drawContours(mask, contours, -1, fill_color, 2)

        self.processed_image = mask
        self.display_image(self.processed_image)
        self.update_message(f'Approximate number of planes\non the image: {len(contours)}')

    def process_image_pixel(self):
        if self.image is None:
            return None

        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        image = cv2.GaussianBlur(image, (31, 31), 0)

        blurred = cv2.GaussianBlur(image, (9, 9), 0)

        gauss_contours = blurred - image

        # opening
        erosion = cv2.erode(gauss_contours, np.ones((3, 3), np.uint8), iterations=2)
        dilation = cv2.dilate(erosion, np.ones((2, 2), np.uint8), iterations=6)

        # find components
        _, labels, stats, _ = cv2.connectedComponentsWithStats(dilation, 4)
        labels = np.unique(labels)
        threshold_S = 10
        for label in labels:
            if stats[label, cv2.CC_STAT_AREA] < threshold_S:
                labels[labels == label] = 0
        labels = np.unique(labels)
        self.processed_image = dilation
        self.display_image(self.processed_image)
        self.update_message(f'Approximate number of planes\non the image: {len(labels) - 1}')


def main():
    root = tk.Tk()
    app = ImageSegmentationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
