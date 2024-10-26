import socket
import ssl
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import os
from PIL import Image, ImageTk
import zipfile
import threading
import io

HOST = 'localhost'
PORT = 5001
CERT_FILE = '/home/reuben/cert.pem'  # Path to your self-signed certificate
ADMIN_PASSWORD = "admin"
DOWNLOAD_DIR = 'Downloaded_Files'  # Directory to save downloaded files

# Create the download directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class FileClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Client")
        self.geometry("350x600")

        # Create SSL context and load the self-signed certificate
        self.context = ssl.create_default_context()
        self.context.load_verify_locations(cafile=CERT_FILE)

        # Create socket and wrap with SSL
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket = self.context.wrap_socket(self.socket, server_hostname=HOST)
        self.socket.connect((HOST, PORT))

        # GUI setup
        list_frame = tk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True)
        list_frame.config(bg='lightblue')

        # Treeview widget for displaying files
        self.tree = ttk.Treeview(list_frame, selectmode='extended')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.heading('#0', text='Files')

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar.set)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        button_frame.config(bg='black')

        tk.Button(button_frame, text="Upload File", bg='crimson', fg='white', command=self.upload_file).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(button_frame, text="Upload Folder", bg='crimson', fg='white', command=self.upload_folder).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(button_frame, text="Download", bg='crimson', fg='white', command=self.download_selected).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(button_frame, text="Delete Selected", bg='crimson', fg='white', command=self.delete_selected).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(button_frame, text="Refresh List", bg='crimson', fg='white', command=self.list_files).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(button_frame, text="Exit", bg='crimson', fg='white', command=self.on_closing).pack(fill=tk.X, padx=5)

        self.progress = ttk.Progressbar(self, length=300, mode='determinate')  # Progress bar
        self.progress.pack(pady=10)

        self.icons = self.load_icons()  # Load file type icons
        self.list_files()  # Load the file list on startup
        self.tree.bind('<Double-1>', self.on_item_double_click)

    def load_icons(self):
        icons = {}
        icons['folder'] = ImageTk.PhotoImage(Image.open('Images/folder_icon.png').resize((20, 20), Image.LANCZOS))
        icons['txt'] = ImageTk.PhotoImage(Image.open('Images/text_file_icon.png').resize((20, 20), Image.LANCZOS))
        icons['jpg'] = ImageTk.PhotoImage(Image.open('Images/image_file_icon.png').resize((20, 20), Image.LANCZOS))
        icons['default'] = ImageTk.PhotoImage(Image.open('Images/default_file_icon.png').resize((20, 20), Image.LANCZOS))
        return icons

    def get_file_icon(self, file_name):
        if os.path.isdir(file_name):
            return self.icons['folder']
        elif file_name.endswith('.txt'):
            return self.icons['txt']
        elif file_name.endswith(('.jpg', '.jpeg', '.png')):
            return self.icons['jpg']
        else:
            return self.icons['default']

    def upload_file(self):
        password = simpledialog.askstring("Password", "Enter admin password:", show='*')
        if password != ADMIN_PASSWORD:
            messagebox.showerror("Error", "Invalid password. Only admin can upload files.")
            return
        
        filepath = filedialog.askopenfilename()
        if filepath:
            threading.Thread(target=self.send_file, args=(filepath,)).start()

    def upload_folder(self):
        password = simpledialog.askstring("Password", "Enter admin password:", show='*')
        if password != ADMIN_PASSWORD:
            messagebox.showerror("Error", "Invalid password. Only admin can upload files.")
            return
        
        folder_path = filedialog.askdirectory()
        if folder_path:
            # Use a subdirectory for ZIP files
            zip_file_path = os.path.join(DOWNLOAD_DIR, f"{os.path.basename(folder_path)}.zip")
            
            # Create a ZIP file from the folder
            try:
                with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, files in os.walk(folder_path):
                        for filename in files:
                            file_path = os.path.join(root, filename)
                            zipf.write(file_path, os.path.relpath(file_path, start=folder_path))

                # Now upload the ZIP file
                threading.Thread(target=self.send_file, args=(zip_file_path,)).start()
                # os.remove(zip_file_path)  # Uncomment this if you want to remove the ZIP file after upload
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload folder: {str(e)}")


    def send_file(self, filepath):
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        self.socket.send(f'upload {filename} {filesize}'.encode())
        
        self.progress['maximum'] = filesize  # Set the maximum value of the progress bar
        chunk_size = 65536  # Increased chunk size (64KB)
        with open(filepath, 'rb') as f:
            data_sent = 0
            buffered_stream = io.BytesIO(f.read())  # Use a buffered stream
            while True:
                chunk = buffered_stream.read(chunk_size)
                if not chunk:
                    break
                self.socket.sendall(chunk)  # Use sendall for better performance
                data_sent += len(chunk)
                self.progress['value'] = data_sent  # Update progress bar
                self.update_idletasks()  # Update the GUI

        self.socket.send(b'EOF')
        response = self.socket.recv(1024).decode()
        self.progress['value'] = 0  # Reset progress bar after upload
        if response.startswith('ACK'):
            messagebox.showinfo("Info", f"File '{filename}' uploaded successfully")
        else:
            messagebox.showerror("Error", f"File '{filename}' upload failed")

    def download_file(self, item_name):
        local_file_path = os.path.join(DOWNLOAD_DIR, item_name)
        self.socket.send(f'download {item_name}'.encode())
        response = self.socket.recv(1024).decode()
        
        if response.startswith('EXISTS'):
            filesize = int(response.split()[1])
            self.socket.send(b'ready')
            self.progress['maximum'] = filesize  # Set the maximum value of the progress bar
            chunk_size = 65536  # Increased chunk size (64KB)
            with open(local_file_path, 'wb') as f:
                data_received = 0
                buffered_stream = io.BytesIO()
                while data_received < filesize:
                    data = self.socket.recv(chunk_size)
                    if not data:
                        break
                    buffered_stream.write(data)
                    data_received += len(data)
                    self.progress['value'] = data_received  # Update progress bar
                    self.update_idletasks()  # Update the GUI

                # Write the buffered data to file
                f.write(buffered_stream.getvalue())

            self.progress['value'] = 0  # Reset progress bar after download
            if data_received < filesize:
                messagebox.showwarning("Warning", f"File '{item_name}' was not fully downloaded.")
            else:
                messagebox.showinfo("Info", f"File '{item_name}' downloaded successfully.")
        else:
            messagebox.showerror("Error", f"File '{item_name}' does not exist on the server.")

    def download_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No files selected!")
            return
        
        for item in selected_items:
            filename = self.tree.item(item, 'text')
            threading.Thread(target=self.download_file, args=(filename,)).start()

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No files selected!")
            return
        password = simpledialog.askstring("Password", "Enter admin password:", show='*')
        if password:
            for item in selected_items:
                filename = self.tree.item(item, 'text')
                self.socket.send(f'delete {password} {filename}'.encode())
                response = self.socket.recv(1024).decode()
                messagebox.showinfo("Info", response)
            self.list_files()  # Refresh file list after deletion

    def list_files(self):
        self.socket.send(b'list')
        file_list = self.socket.recv(4096).decode()
        self.tree.delete(*self.tree.get_children())  # Clear the current list
        if file_list:
            for filename in file_list.splitlines():
                icon = self.get_file_icon(filename)
                self.tree.insert('', tk.END, text=filename, image=icon)
        else:
            messagebox.showinfo("Files on Server", "No files found.")

    def on_item_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_name = self.tree.item(selected_item[0], 'text')
            local_file_path = os.path.join(DOWNLOAD_DIR, item_name)

            # Preview the file
            if item_name.endswith(('.jpg', '.jpeg', '.png')):
                self.preview_image(local_file_path)
            elif item_name.endswith('.docx'):
                self.preview_doc(local_file_path)
            else:
                messagebox.showinfo("Preview", f"No preview available for '{item_name}'.")

    def preview_image(self, file_path):
        try:
            img = Image.open(file_path)
            img.thumbnail((400, 400))  # Resize for preview
            img.show()  # Use the default image viewer
        except OSError as e:
            messagebox.showerror("Error", f"Could not open image: {e}")

    def on_closing(self):
        self.socket.close()
        self.destroy()

# Run the application
if __name__ == "__main__":
    app = FileClient()
    app.mainloop()
