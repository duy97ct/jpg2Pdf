import cv2
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import uuid
import threading

class CameraToPDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera to PDF App")
        
        self.capture_button = tk.Button(root, text="Capture Image", command=self.capture_image)
        self.capture_button.pack(pady=10)
        
        self.convert_button = tk.Button(root, text="Convert to PDF", command=self.convert_to_pdf)
        self.convert_button.pack(pady=5)

        self.delete_button = tk.Button(root, text="Delete Image", command=self.delete_image)
        self.delete_button.pack(pady=5)
        
        self.image_label = tk.Label(root)
        self.image_label.pack(padx=10, pady=5)
        
        self.captured_images = []
        self.output_pdf_file = ""
        
        # Initialize camera
        self.camera = cv2.VideoCapture(0)
        self.camera_thread = threading.Thread(target=self.update_camera)
        self.camera_thread.daemon = True
        self.camera_thread.start()

    def update_camera(self):
        while True:
            ret, frame = self.camera.read()
            if ret:
                # Convert the frame from BGR to RGB format
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert the frame to PIL Image format
                image = Image.fromarray(rgb_frame)

                # Resize the image to fit the app window
                width, height = image.size
                new_width = 600
                new_height = int((new_width / width) * height)
                image = image.resize((new_width, new_height), Image.LANCZOS)

                # Convert the image to Tkinter format
                tk_image = ImageTk.PhotoImage(image)

                # Update the image label in the app
                self.image_label.config(image=tk_image)
                self.image_label.image = tk_image

    def capture_image(self):
        # Capture a frame from the camera
        ret, frame = self.camera.read()
        
        # Convert the frame from BGR to RGB format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create a PIL Image object
        image = Image.fromarray(rgb_frame)
        
        # Save the captured image temporarily
        temp_image_file = f"captured_image_{len(self.captured_images)}.jpg"
        image.save(temp_image_file)
        
        # Append the image to the list of captured images
        self.captured_images.append(temp_image_file)
        
        # Display the captured image in the app
        self.show_captured_image(temp_image_file)

        # Enable the delete button
        self.delete_button.config(state=tk.NORMAL)

    def show_captured_image(self, image_file):
        # Open the image file
        image = Image.open(image_file)
        
        # Resize the image to fit the app window
        width, height = image.size
        new_width = 600
        new_height = int((new_width / width) * height)
        image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert the image to Tkinter format
        tk_image = ImageTk.PhotoImage(image)
        
        # Update the image label in the app
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image
        
    def delete_image(self):
        if len(self.captured_images) > 0:
            # Remove the last captured image from the list
            last_image = self.captured_images.pop()

            # Delete the temporary image file
            os.remove(last_image)

            # Display the previous image in the app (if any)
            if self.captured_images:
                self.show_captured_image(self.captured_images[-1])
            else:
                # If no images left, clear the image label
                self.image_label.config(image=None)
                self.image_label.image = None

        # Disable the delete button if no images left
        if len(self.captured_images) == 0:
            self.delete_button.config(state=tk.DISABLED)
        
    def convert_to_pdf(self):
        if len(self.captured_images) == 0:
            tk.messagebox.showwarning("Warning", "No images captured.")
            return
        
        # Generate a random name for the output PDF
        random_output_name = str(uuid.uuid4())[:8] + ".pdf"
        self.output_pdf_file = os.path.join(os.getcwd(), random_output_name)
        
        # Create a new PDF file
        c = canvas.Canvas(self.output_pdf_file, pagesize=letter)
        
        # Scale the images to fit the page size and add them to the PDF
        width, height = letter
        for image_file in self.captured_images:
            # Open the image file
            image = Image.open(image_file)
        
            img_width, img_height = image.size
            aspect_ratio = img_width / float(img_height)
            if aspect_ratio >= 1:
                new_width = width
                new_height = width / aspect_ratio
            else:
                new_height = height
                new_width = height * aspect_ratio
        
            # Draw the image on the PDF
            c.drawImage(image_file, 0, 0, width=new_width, height=new_height)
        
            # Add a new page for the next image (if not the last image)
            if image_file != self.captured_images[-1]:
                c.showPage()
        
        # Save the PDF
        c.save()
        
        tk.messagebox.showinfo("Success", f"PDF file saved as {self.output_pdf_file}")
        
        # Delete the temporary image files
        for image_file in self.captured_images:
            os.remove(image_file)
        
        self.captured_images.clear()
        self.output_pdf_file = ""

    def on_close(self):
        # Release the camera and close the OpenCV window
        self.camera.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraToPDFApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
