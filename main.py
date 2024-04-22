# Import Required Modules 
from tkinter import *
from pyyoutube import Api 
from pytube import YouTube, Playlist
from threading import Thread 
from tkinter import messagebox
from tkinter import filedialog
import errno, socket, ssl
import requests
import os
from dotenv import load_dotenv
import logging

# Set up logging (optional)
# logging.basicConfig(level=logging.DEBUG)

load_dotenv(".env")

output_dir = "path.txt"


# Network errors, usually related to DHCP or wpa_supplicant (Wi-Fi).
NETWORK_ERRNOS = frozenset((
    errno.ENETUNREACH,  # "Network is unreachable"
    errno.ENETDOWN,  # "Network is down"
    errno.ENETRESET,  # "Network dropped connection on reset"
    errno.ENONET,  # "Machine is not on the network"
))

def is_connection_err(exc):
    """Return True if an exception is connection-related."""
    if isinstance(exc, ConnectionError):
        # https://docs.python.org/3/library/exceptions.html#ConnectionError
        # ConnectionError includes:
        # * BrokenPipeError (EPIPE, ESHUTDOWN)
        # * ConnectionAbortedError (ECONNABORTED)
        # * ConnectionRefusedError (ECONNREFUSED)
        # * ConnectionResetError (ECONNRESET)
        return True
    if isinstance(exc, socket.gaierror):
        # failed DNS resolution on connect()
        return True
    if isinstance(exc, (socket.timeout, TimeoutError)):
        # timeout on connect(), recv(), send()
        return True
    if isinstance(exc, OSError):
        # ENOTCONN == "Transport endpoint is not connected"
        return (exc.errno in NETWORK_ERRNOS) or (exc.errno == errno.ENOTCONN)
    if isinstance(exc, ssl.SSLError):
        # Let's consider any SSL error a connection error. Usually this is:
        # * ssl.SSLZeroReturnError: "TLS/SSL connection has been closed"
        # * ssl.SSLError: [SSL: BAD_LENGTH]
        return True
    return False


def check_internet():
    try:
        response = requests.get("https://www.bing.com", timeout=5)
        return response.status_code == 200
    except Exception as e:
        # messagebox.showerror("Error", "Check your connection\nAnd click OK to continue")
        
        return False




def check_entry_content():
    if url_input_field.get():
        get_videos.config(state=NORMAL)  # Enable the button
    else:
        download_start.config(state=DISABLED)
        get_path.config(state=DISABLED)
        get_videos.config(state=DISABLED)  # Disable the button
        list_box.delete(0, END)

def clear_entry():
    url_input_field.delete(0, END)  # Clear the entry's content
    check_entry_content()
    select_all_checkbox.config(state=DISABLED)

def get_path():
    # Open a file dialog to select a directory
    path = filedialog.askdirectory()
    if path:
        # download_videos(path=path)
        print(f"Selected path: {path}")
        with open(output_dir, "w") as path_file:
            path_file.write(path)
    
        # The listbox and select all check button become clickable only if the "choose" path button is clicked
        list_box.config(state=NORMAL)
        select_all_checkbox.config(state=NORMAL)


        return path
    else:
        print("No path selected.")
        with open(output_dir, "r") as path:
            path = path.read().strip()
            print(path)
            list_box.config(state=DISABLED)
            messagebox.showerror("Error", "no path")
            return None




def paste_from_clipboard():
    # clear Input before pasting a new link
    clear_entry()

    clipboard_data = root.clipboard_get()
    url_input_field.insert(0, clipboard_data)
    check_entry_content()
    
def check_selection(event):
    selected_indices = list_box.curselection()

    if len(selected_indices) == 0:
        print(f"{len(selected_indices)} item is selected")

    if selected_indices and len(selected_indices) == list_box.size():
        select_all_checkbox_var.set(1)
        print("All items are selected!")


    if selected_indices and len(selected_indices) != list_box.size():
        if len(selected_indices) == 1:
            print(f"{len(selected_indices)} item is selected!")

        else:
            select_all_checkbox_var.set(0)
            print(f"{len(selected_indices)} items are selected!")

    if selected_indices:
        download_start.config(state=NORMAL)  # Enable the button
    else:
        download_start.config(state=DISABLED)  # Disable the button


def select_all():
    state = select_all_checkbox_var.get()

def checkbutton_state():
    state = select_all_checkbox_var.get()
    # print(get_videos_button)

    num_items = list_box.size()
    if state == 1:
        print(f"Checkbutton state: {state}")
        
        # Select all items
        list_box.selection_set(0, num_items - 1)
        download_start.config(state=NORMAL)  # Enable the button
        
    else:
        list_box.selection_clear(0, num_items - 1)
        download_start.config(state=DISABLED)  # Disable the button

def straight_download(url=None):
    from pytube import Playlist

    # Input the URL of the playlist
    playlist_url = input('Enter the URL of the playlist: ')
    playlist = Playlist(playlist_url)

    # Print the number of videos in the playlist
    print(f'Number of videos in the playlist: {len(playlist.video_urls)}')

    # Download each video in the playlist
    for video_url in playlist.video_urls:
        print(video_url)
        # Download logic here (e.g., using stream.download())

# straight_download()
def get_list_videos(): 
    # global video_item
    # Clear ListBox 
    list_box.delete(0, 'end') 

        # Call the function to check internet connection

    while check_internet() == False:
        print("No internet connection.")
        messagebox.showerror("Error", "Check your connection\nAnd click OK to continue")
    else:
        print("Internet connection is available.")
        if get_path.cget("state") == "disabled":
            select_all_checkbox_var.set(0)
            checkbutton_state()
            list_box.config(state=NORMAL)
            

    global playlist_item_by_id 
    # Create API Object 
    api = Api(api_key=os.environ.get("API_KEY")) 
    # try:
        
            

    if "youtube" in url_input_field.get() and "playlist" in url_input_field.get(): 
        playlist_id = url_input_field.get()[len( 
            "https://www.youtube.com/playlist?list="):]
        print(playlist_id) 
        # print(selected_option.get())
        # Get list of video links 
        playlist_item_by_id = api.get_playlist_items( 
            playlist_id=playlist_id, count=None, return_json=True) 
        

        # Iterate through all video links and insert into listbox
        for index, videoid in enumerate(playlist_item_by_id['items']):
            video_id = videoid['contentDetails']['videoId']
            video_title = videoid['snippet']['title']
        
            list_box.insert(END, f" {str(index+1)}. {video_title}")
            # all_items = [list_box.get(index) for index in range(list_box.size())]
            # print(len(all_items))
            # list_box.insert(END, f" {str(index+1)}. {video_title}     Size: {get_video_id(video_id=video_id)} MB")
        # link = f"https://www.youtube.com/watch?v={videoid}"
        # link = f"https://www.youtube.com/watch?v={video_id}"

        # yt_obj = YouTube(link)

        # video_title = yt_obj.title  # Get the video title

        # print(f"Video Title: {video_title}")
        # video_size_mb = yt_obj.streams.get_highest_resolution().filesize / (1024 * 1024)  # Video size in MB
        # print(f"Video Size (MB): {video_size_mb:.2f} MB")
    if "youtu.be" in url_input_field.get():
        video_id = url_input_field.get()[len("https://youtu.be/"):]
        
        # Get the video and it title
        video_item = api.get_video_by_id(video_id=video_id, return_json=True)
        # print(video)
        video_info =video_item["items"][0]["snippet"]
        video_title =video_info["title"]
        
        print(video_id) 


        list_box.insert(END, f"{video_title}")

        # playlist_id = url_input_field.get() 

        # https://youtu.be/0hEmxOEeVO0
        # https://www.youtube.com/watch?v=S7MNX_UD7vY


    # The list become clickable based on the state of the Choose path button
    if get_path.cget("state") == "normal":
        list_box.config(state=NORMAL)
        select_all_checkbox_var.set(0)
        print("yes")
    if get_path.cget("state") == "disabled":
        select_all_checkbox_var.set(0)
        checkbutton_state()
        list_box.config(state=DISABLED)
        get_path.config(state=NORMAL)
            # Simulating the exception for demonstration purposes
            # raise pyyoutube.error.PyYouTubeException("YouTubeException(status_code=404,message=The playlist identified with the request's <code>url_input_field</code> parameter cannot be found.)")
    # except Exception as e:
        # #     # Handle the exception
    # #     error_message = str(e)  # Get the error message from the exception
    #     # print(e.with_traceback())
    #     print("No connection")
    #     messagebox.showerror("Error", f"An error occurred:\nVideo cannot be found with that link\nCheck your link")
        # messagebox.showerror("Error", f"An error occurred:\n{error_message}")


    



def threading(): 
    # Call download_videos function 
    t1 = Thread(target=download_videos) 
    t1.start() 


def download_videos():
    def connection_checker():
        while check_internet() == False:
            print("No internet connection.")
            messagebox.showerror("Error", "Check your connection\nAnd click OK to continue")
        else:
            print("Internet connection is available.")
            if get_path.cget("state") == "disabled":
                select_all_checkbox_var.set(0)
                checkbutton_state()
                list_box.config(state=NORMAL) 
        download_start.config(state="disabled") 
        get_path.config(state="disabled")
        get_videos.config(state="disabled") 

    connection_checker()

    # Iterate through all selected videos 
    # Counter variable to keep track of position number
    # position = 1
    for i in list_box.curselection():
        video_id = ""
        video_title = list_box.get(i)

        if "youtu.be" in url_input_field.get():
            video_id = url_input_field.get()[len("https://youtu.be/"):]
        
            print(video_id)

        # if selected_option.get() == "Enter Playlist URL":
    
        # print(video)
        # video_info =video_item["items"][0]["snippet"]
    
        if "youtube" in url_input_field.get() and "playlist" in url_input_field.get(): 
            playlist_id = url_input_field.get()[len( 
                "https://www.youtube.com/playlist?list="):]
            # print(selected_option.get())
            # Get list of video links 
            # playlist_item_by_id = api.get_playlist_items(playlist_id=playlist_id, count=None, return_json=True) 
            video_id = playlist_item_by_id['items'][i]['contentDetails']['videoId']
            print(video_id) 
            

        link = f"https://www.youtube.com/watch?v={video_id}"

        yt_obj = YouTube(link)

    #     # video_title = yt_obj.title  # Get the video title
        print(video_title)

    # #     print(f"Video Title: {video_title}")
    # #     video_size_mb = yt_obj.streams.get_highest_resolution().filesize / (1024 * 1024)  # Video size in MB
    # #     print(f"Video Size (MB): {video_size_mb:.2f} MB")

    # #     list_box.insert(END, f" {video_size_mb:.2f} MB")
        
        

        filters = yt_obj.streams.filter(progressive=True, file_extension='mp4') 

        # download the highest quality video 
        with open(output_dir, "r") as path_file:
            output_path = path_file.readline()
        
        connection_checker()
        filters.get_highest_resolution().download(output_path=output_path, filename_prefix=str(video_title).split(".")[0] + ". ")

        # Increment position counter
        # position += 1

    messagebox.showinfo("Success", "Video Successfully downloaded") 
    download_start.config(state="normal") 
    get_path.config(state="normal")
    get_videos.config(state="normal") 




    
# Create Object 
root = Tk() 

# Title
root.title("GDYtube")

# Set geometry 
root.geometry('600x600') 

# iconbitmap(): The iconbitmap() method allows you to set an icon for your Tkinter window. It takes the path to an .ico file as its argument. 
# root.iconbitmap("/path/to/your_icon.ico")

# iconphoto(): The iconphoto() method sets the title bar icon for a Tkinter window. You can use various image types, including .png.
root.iconphoto(False, PhotoImage(file="app_data/favicon.png"))

# Add Label 
Label(root, text="GUIDASWORLD Youtube Playlist Downloader", 
	font="italic 15 bold").pack(pady=10) 
Label(root, text="Highest resolutions only", 
	font="italic 10 bold").pack(pady=10) 


def show_selected():
   # Display the selected option
    label.config(text=selected_option.get())



# Create a frame to hold playlist or one video radio button
radio_button_frame = Frame(root)
radio_button_frame.pack()

# Create radio buttons and associate them with the variable
selected_option = StringVar()
# selected_option.set("Enter Playlist URL")  # Set the default value
# option1 = Radiobutton(radio_button_frame, text="Standard", value="Enter video URL", variable=selected_option, command=show_selected)
# option2 = Radiobutton(radio_button_frame, text="Playlist", value="Enter Playlist URL", variable=selected_option, command=show_selected)

# # Pack the radio buttons and label horizontally
# option1.pack(side="left", padx=10)
# option2.pack(side="left", padx=10)

# Create a label to display the selected option
label = Label(radio_button_frame, text="Enter Playlist URL:", font="italic 10")
label.pack(side="left", padx=10)


# Add Entry box 
url_input_field = Entry(root, width=60) 

url_input_field.pack(pady=5)
clear_url = Button(root, text="Clear link", command=clear_entry)
clear_url.pack(padx=10) 

# Create a frame to hold the buttons
button_frame = Frame(root)
button_frame.pack()

# Create a "Paste" button
paste_button = Button(button_frame, text="Paste", command=paste_from_clipboard)
paste_button.pack(side="left", padx=10)

# Create a "Get Videos" button
get_videos = Button(button_frame, text="Get Videos", command=get_list_videos, state=DISABLED)
get_videos.pack(side="left", padx=10)

# Bind the function to the Entry widget
url_input_field.bind("<KeyRelease>", lambda event: check_entry_content())

# Choose a path for video
get_path = Button(button_frame, text="Choose a path", command=get_path, state=DISABLED)
get_path.pack(side="left", padx=10)

# Create a "Download Start" button
download_start = Button(button_frame, text="Download Start", command=threading, state=DISABLED)
download_start.pack(side="left", padx=10)

# Create a "Quit" button
quit_download = Button(button_frame, text="Quit", command=quit)
quit_download.pack(side="left", padx=10)


Checkbutton_frame = Frame(root)
Checkbutton_frame.pack()

# Create select All checkbox
select_all_checkbox_var = IntVar()  # Variable to store the state
select_all_checkbox = Checkbutton(Checkbutton_frame, text="Select All", variable=select_all_checkbox_var, command=checkbutton_state, state=DISABLED)
select_all_checkbox.pack()

# Add Scrollbar 
scrollbar = Scrollbar(root) 
scrollbar.pack(side=RIGHT, fill=BOTH) 
list_box = Listbox(root, selectmode="multiple") 
list_box.pack(expand=YES, fill="both") 
list_box.config(yscrollcommand=scrollbar.set) 
scrollbar.config(command=list_box.yview) 

# Bind the selection event to the check_selection function
list_box.bind("<<ListboxSelect>>", check_selection)



# Execute Tkinter 
root.mainloop() 

