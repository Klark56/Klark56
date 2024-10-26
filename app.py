from tkinter import *
import socket
import platform
import tkinter as tk
import subprocess
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image , UnidentifiedImageError
from tkinter import Tk
import os
from tkinter import ttk,Canvas,Frame,Scrollbar
from tkinter import filedialog, Toplevel, Label, Button
import threading
from datetime import datetime

root = tk.Tk()
root.title("CONNECT")
root.geometry("350x560")
root.configure(bg="#000")
root.resizable(False,False)


header_frame=tk.Frame(root, bg='black', height=25)
top_frame = tk.Frame(root,bg='lightblue', height=435)
bottom_frame = tk.Frame(root, bg='black', height=100)

header_frame.pack(fill='both', expand=True)
top_frame.pack(fill='both', expand=True)
bottom_frame.pack(fill='both', expand=True)

def client_side():
    system = platform.system()
    if system == 'Linux':
        subprocess.run(['python3', 'client_side.py'])
    else:
        subprocess.run(['python', 'client_side.py'])


def Applications():
    system = platform.system()
    if system == 'Linux':
        subprocess.run(['python3', 'system_apps.py'])
    else:
        subprocess.run(['python', 'system_apps.py'])

    


def Send():
    window = Toplevel(root)
    window.title("Send")
    window.geometry('350x560')
    window.configure(bg="black")
    window.resizable(False, False)
    
    global senderfile, conn, listening, filenames
    listening = False
    senderfile = None
    conn = None
    filenames = []

    def select_files():
        global filenames
        new_files = filedialog.askopenfilenames(
            initialdir=os.getcwd(), 
            title='Select Files',
            filetypes=(('All files', '*.*'), ('Text files', '*.txt'))
        )
        filenames.extend(new_files)
        file_count_label.config(text=f"{len(filenames)} files selected")

    def sender():
        global listening, senderfile, conn
        try:
            senderfile = socket.socket()
            senderfile.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            host = socket.gethostbyname(socket.gethostname())
            port = 8080
            senderfile.bind((host, port))
            senderfile.listen(1)
            senderfile.settimeout(1)  # Set timeout for non-blocking
            listening = True
            print(f"ID: {host}")
            print('Searching for incoming connections....')
            while listening:
                try:
                    conn, addr = senderfile.accept()
                    print(f"Connection established with {addr}")

                    for filename in filenames:
                        with open(filename, 'rb') as file:
                            file_data = file.read(1024)
                            while file_data:
                                conn.send(file_data)
                                file_data = file.read(1024)
                            print(f"Data from {filename} has been transmitted successfully")

                    conn.close()
                    break
                except socket.timeout:
                    continue
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if senderfile:
                senderfile.close()
            listening = False

    def start_sending():
        sender_thread = threading.Thread(target=sender)
        sender_thread.start()

    def disconnect():
        global listening
        listening = False
        try:
            if conn:
                conn.close()
            if senderfile:
                senderfile.close()
            print("Disconnected.")
        except Exception as e:
            print(f"An error occurred while disconnecting: {e}")
            
    def back_to_main():
        window.destroy()
        
    # Icon
    root_icon1 = PhotoImage(file="Images/send_38dp_4B77D1_FILL0_wght400_GRAD0_opsz40.png")
    window.iconphoto(False, root_icon1)

    Startbackground = ImageTk.PhotoImage(Image.open("Images/receiver.png"))
    Label(window, image=Startbackground).place(x=-35, y=0)

    Middlebackground = ImageTk.PhotoImage(Image.open("Images/id.png"))
    Label(window, image=Middlebackground, bg="#f4fdfe").place(x=58, y=240)

    Label(window, text="Send", font=('arial', 20), bg="#f4fdfe").place(x=153, y=70)
    
    host = socket.gethostname()
    Label(window, text=f'My device: {host}', bg='white', fg='black').place(x=143, y=270)

    file_count_label = Label(window, text="No files selected", bg='#fdf4fe', fg='black')
    file_count_label.place(x=130, y=420)

    Button(window, text="Back", width=4, height=1, font='arial 14 bold', bg='black', fg='orange',command=back_to_main).place(x=5,y=10)
    Button(window, text="+ add files", width=10, height=1, font='arial 14 bold', bg='#fff', fg='black', command=select_files).place(x=52, y=500)
    Button(window, text="SEND", width=8, height=1, font='arial 14 bold', bg='#000', fg='#fff', command=start_sending).place(x=193, y=500)
    Button(window, text="X", width=1, height=1, font='arial 14 bold', bg='red', fg='black',command=disconnect).place(x=305,y=500)
    
    window.mainloop()
    
    
    
def Receive():
    main = Toplevel(root)
    main.title("Receive")
    main.geometry('350x560')
    main.configure(bg="black")
    main.resizable(False, False)
    
    global receiving, receiver_thread
    receiving = False
    receiver_thread = None

    def Receiver():
        global receiving, receiver_thread
        try:
            ID = SenderID.get()
            port = 8080
            receiving = True

            def receive_files():
                try:
                    senderfile = socket.socket()
                    senderfile.connect((ID, port))
                    file_count = 0

                    while receiving:
                        filename1 = f"incoming_file_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                        with open(filename1, 'wb') as file:
                            while True:
                                file_data = senderfile.recv(1024)
                                if not file_data:
                                    break
                                file.write(file_data)
                            file_count += 1
                            file_count_label.config(text=f"{file_count} files received")

                    print("All files have been received successfully")
                    senderfile.close()
                except Exception as e:
                    print(f"An error occurred: {e}")

            receiver_thread = threading.Thread(target=receive_files)
            receiver_thread.start()
        except Exception as e:
            print(f"An error occurred: {e}")

    def disconnect_receiver():
        global receiving, receiver_thread
        receiving = False
        try:
            if receiver_thread and receiver_thread.is_alive():
                receiver_thread.join()
            print("Disconnected from receiver.")
        except Exception as e:
            print(f"An error occurred while disconnecting: {e}")

    def back_to_main():
        main.destroy()
    
    # Icon
    root_icon1 = PhotoImage(file="Images/send_38dp_4B77D1_FILL0_wght400_GRAD0_opsz40.png")
    main.iconphoto(False, root_icon1)

    Topbackground = ImageTk.PhotoImage(Image.open("Images/receiver.png"))
    Label(main, image=Topbackground).place(x=-35, y=0)

    Lowerbackground = ImageTk.PhotoImage(Image.open("Images/android.jpeg"))
    Label(main, image=Lowerbackground, bg="#f4fdfe").place(x=-17, y=270)

    Label(main, text="Receive", font=('arial', 20), bg="#f4fdfe").place(x=140, y=70)
    Label(main, text="Enter sender id", font=('arial', 10, 'bold'), bg="orange").place(x=20, y=204)
    SenderID = Entry(main, width=25, fg='black', border=2, bg='white', font=('arial', 15))
    SenderID.place(x=20, y=235)
    SenderID.focus()

    file_count_label = Label(main, text="No files received", bg='white', fg='black')
    file_count_label.place(x=20, y=400)

    icon_image = PhotoImage(file="Images/arrow.png")
    ic_img = Button(main, text="Receive", compound=LEFT, image=icon_image, width=130, height=20, bg="#39c790", font=('arial 14 bold'), command=Receiver)
    ic_img.place(x=20, y=350)

    Button(main, text="Back", width=4, height=1, font='arial 14 bold', bg='black', fg='orange',command=back_to_main).place(x=5,y=10)
    Button(main, text="CANCEL", width=8, height=1, font='arial 14 bold', bg='red', fg='#fff', command=disconnect_receiver).place(x=133, y=450)
    
    main.mainloop()
    

def open_file_explorer():
    file=Toplevel(root)   
    file.title("My~Files")
    file.geometry("350x560")
    file.resizable(False,False)
    image= Image.open("Images/R.jpeg")
    new_size = (root.winfo_screenwidth(), root.winfo_screenheight())
    image = image.resize(new_size, Image.LANCZOS)
    tk_image = ImageTk.PhotoImage(image)
    background_label =Label(file, image=tk_image)
    background_label.place(x=-0, y=0, relwidth=1,relheight=1) 
    
    
        

        
    def view():
        file_path = filedialog.askdirectory()
        if file_path:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", file_path])
            else:  # Linux
                subprocess.call(["xdg-open", file_path]) 
    
    def back_main():
        file.destroy()
    

    root_icon1=PhotoImage(file="Images/send_38dp_4B77D1_FILL0_wght400_GRAD0_opsz40.png")
    file.iconphoto(False,root_icon1)
    
    Topbackground = ImageTk.PhotoImage(Image.open("Images/sender.png"))
    Label(file, image=Topbackground).place(x=-15,y=0)
    
    host=socket.gethostname()
    Label(file,text=f'Hostname: {host}',bg='white',fg='black').place(x=160,y=90)
    username=os.getlogin()
    Label(file,text=f'Username: {username}',bg='#fff',fg='#000').place(x=160,y=120)
    
    Botbackground = ImageTk.PhotoImage(Image.open("Images/background.png"))
    Label(file, image=Botbackground).place(x=-10,y=340)
    
    
    icon_image = PhotoImage(file="Images/files.png")
    ic_img=Button(file,text="My~Files",compound=CENTER,image=icon_image,width=130,height=100, bg="#000",font=('arial 14 italic'),command=view,fg="orange")
    ic_img.place(x=40,y=222)
    
    
    
    Button(file, text="Back", width=4, height=1, font='arial 14 bold', bg='black', fg='orange',command=back_main).place(x=5,y=10)
    
    
    file.mainloop()



#icon
root_icon=PhotoImage(file="Images/send_38dp_4B77D1_FILL0_wght400_GRAD0_opsz40.png")
root.iconphoto(False,root_icon)


def exit_app():
    root.destroy()

exit_button = tk.Button(root, text="Exit",font=('Arial',7),bg='crimson',fg='white' ,command=exit_app)
exit_button.place(x=305,y=1)


Label(root,text="CONNECT",font=('Acumin Variable Concept',10,'bold'),bg="orange").place(x=135,y=2)


main_back= ImageTk.PhotoImage(Image.open("Images/File_Sharing1.png"))
Label(root, image=main_back,bg='lightblue').place(x=0,y=25)



send_image=PhotoImage(file="Images/send2.png")
send=tk.Button(root,image=send_image,bd=1,bg="lightgreen",border=3,command=Send)
send.place(x=40,y=470)


receive_image=PhotoImage(file="Images/receive.png")
receive=Button(root,image=receive_image,bg="lightgreen",border=3,command=Receive)
receive.place(x=270,y=470)

view_file=PhotoImage(file="Images/files2.png")
view=Button(root,image=view_file,bg="black",border=3,command=open_file_explorer)
view.place(x=200,y=202)

Appli=PhotoImage(file="Images/server2.png")
Appli1=Button(root,image=Appli,bg='black', bd=3,command=client_side)
Appli1.place(x=100,y=200)

view_apps=PhotoImage(file="Images/app.png")
view2=Button(root,image=view_apps,bg="black",border=5,command=Applications)
view2.place(x=137,y=445)


# label
Label(root,text="Send",font=('Acumin Variable Concept',10,'bold'),bg="black",fg="white").place(x=45,y=530)
Label(root,text="Receive",font=('Acumin Variable Concept',10,'bold'),bg="black",fg="white").place(x=273,y=530)
Label(root,text="My~Files",font=('Acumin Variable Concept',10,'bold'),bg="black",fg="white").place(x=199,y=260)
Label(root,text="Online",font=('Acumin Variable Concept',10,'bold'),bg="black",fg="white").place(x=105,y=259)



root.mainloop()