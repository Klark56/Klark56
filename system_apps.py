import tkinter as tk
from tkinter import PhotoImage, Canvas, Scrollbar, Frame,Button,Label
from PIL import Image, ImageTk
import platform
import os




def get_installed_apps():
    apps = []
    system = platform.system()
    if system == "Windows":
        import winreg
        registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                subkey_name = winreg.EnumKey(key, i)
                with winreg.OpenKey(key, subkey_name) as subkey:
                    try:
                        app_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                        apps.append((app_name, install_location))
                    except FileNotFoundError:
                        continue
    elif system == "Linux":
        desktop_files_path = '/usr/share/applications'
        for item in os.listdir(desktop_files_path):
            if item.endswith('.desktop'):
                apps.append((item[:-8], os.path.join(desktop_files_path, item)))  # Strip '.desktop'
    elif system == "Darwin":  # macOS
        applications_path = "/Applications"
        for app in os.listdir(applications_path):
            apps.append((app, os.path.join(applications_path, app)))
    return apps

def get_icon_path(app_path):
    system = platform.system()
    if system == "Windows":
        exe_path = os.path.join(app_path, 'app.exe')
        return exe_path if os.path.exists(exe_path) else None
    elif system == "Linux":
        with open(app_path, 'r') as file:
            for line in file:
                if line.startswith('Icon='):
                    icon_path = line.strip().split('=')[1]
                    if os.path.exists(icon_path):
                        return icon_path
                    # Check standard icon directories
                    possible_paths = [
                        os.path.join('/usr/share/icons', icon_path),
                        os.path.join('/usr/share/pixmaps', icon_path),
                    ]
                    for path in possible_paths:
                        if os.path.exists(path):
                            return path
    elif system == "Darwin":  # macOS
        icon_path = os.path.join(app_path, "Contents/Resources/icon.icns")
        return icon_path if os.path.exists(icon_path) else None
    return None

def display_icons(frame, apps, default_icon):
    max_columns = 4
    row = 0
    col = 0
    
    for app_name, app_path in apps:
        icon_path = get_icon_path(app_path)
        try:
            if icon_path and os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                icon_image.thumbnail((30, 30), Image.LANCZOS)  
            else:
                icon_image = Image.open(default_icon)
                icon_image.thumbnail((30, 30), Image.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)
        except (FileNotFoundError, OSError, ValueError):
            icon_image = Image.open(default_icon)
            icon_image.thumbnail((30, 30), Image.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)

        button = tk.Button(frame, image=icon_photo, text=app_name, compound='top',bg='lightblue', width=45, height=45, borderwidth=0, relief='flat')
        button.image = icon_photo  # Keep a reference to avoid garbage collection
        button.grid(row=row, column=col, padx=8, pady=8)

        col += 1
        if col >= max_columns: 
            col = 0
            row += 1

def setup_applications_display(root):
    header_frame2 = Frame(root, bg='black',height=540)
    header_frame = Frame(root, bg='black')
    header_frame2.pack(fill='both', expand=True)
    header_frame.pack(fill='both', expand=True)

    # Create canvas and scrollbars
    canvas = Canvas(header_frame2)
    # scroll_x = Scrollbar(header_frame2, orient="horizontal", command=canvas.xview, width=10)  
    scroll_y = Scrollbar(header_frame2, orient="vertical", command=canvas.yview, width=10)    
    frame = Frame(canvas, bg='black')

    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set)
    # canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

    # Enable touch scrolling
    def on_touch_scroll(event):
        canvas.xview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind("<MouseWheel>", on_touch_scroll)  # For mouse scroll
    canvas.bind("<Button-4>", on_touch_scroll)    # For Linux touchpads
    canvas.bind("<Button-5>", on_touch_scroll)    # For Linux touchpads


    default_icon_path = "Images/icon.png"
    if not os.path.exists(default_icon_path):
        print(f"Error: {default_icon_path} not found.")
        return

    apps = get_installed_apps()
    display_icons(frame, apps, default_icon_path)
    
    def exit_app():
        root.destroy()

    exit_button = tk.Button(header_frame, text="HOME",font=('Arial',20),bg='crimson',fg='white' ,command=exit_app)
    exit_button.place(x=120)

    

    # Pack the canvas and scrollbar correctly
    canvas.pack(side="top", fill="both", expand=True)
    # scroll_x.pack(side="bottom", fill="x")
    scroll_y.pack(side="right", fill="y")


root = tk.Tk()
root.title("Installed Applications")
root.geometry('350x560')  
root.config= ImageTk.PhotoImage(Image.open("Images/th.jpeg"))
Label(root, image=root.config).place(x=0,y=0)
root.resizable(False,False)


root_icon=PhotoImage(file="Images/send_38dp_4B77D1_FILL0_wght400_GRAD0_opsz40.png")
root.iconphoto(False,root_icon)

setup_applications_display(root)


root.mainloop()
