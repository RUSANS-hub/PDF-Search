from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.client import OAuth2WebServerFlow
import re
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext
import webbrowser
from tqdm import tqdm
import pyperclip


class GoogleDriveDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Drive Downloader")

        self.folder_link_label = tk.Label(root, text="Google Drive Folder Link:")
        self.folder_link_label.pack(pady=10)

        self.folder_link_entry = tk.Entry(root, width=40)
        self.folder_link_entry.pack(pady=10)

        self.output_folder_label = tk.Label(root, text="Local Folder Name:")
        self.output_folder_label.pack(pady=10)

        self.output_folder_entry = tk.Entry(root, width=40)
        self.output_folder_entry.pack(pady=10)

        self.ok_button = tk.Button(root, text="Download", command=self.on_download)
        self.ok_button.pack(pady=20)

        self.open_browser_button = tk.Button(root, text="Open Browser", command=self.on_open_browser)
        self.open_browser_button.pack(pady=10)

        self.status_text = scrolledtext.ScrolledText(root, height=10, width=60, state=tk.DISABLED)
        self.status_text.pack(pady=10)

    def on_download(self):
        folder_link = self.folder_link_entry.get()
        output_folder = self.output_folder_entry.get()

        gauth = self.authenticate_google_drive()

        if gauth is None:
            self.display_status("Error: Authentication failed. Make sure you fill in the credentials correctly.")
            return

        self.download_files_from_google_drive(folder_link, output_folder, gauth)
        self.display_status("Download completed.")

    def on_open_browser(self):
        authorize_url = self.get_authorize_url()
        webbrowser.open_new(authorize_url)

    def authenticate_google_drive(self):
        flow = OAuth2WebServerFlow(
            client_id='336430597454-4q3924j5lcafiedhmold73t95bajv8o4.apps.googleusercontent.com',
            client_secret='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',
            scope='https://www.googleapis.com/auth/drive',
            redirect_uri='http://localhost'
        )

        authorize_url = flow.step1_get_authorize_url()

        # GUI untuk memasukkan kode otorisasi
        auth_root = tk.Toplevel(self.root)
        auth_root.title("Google Drive Authentication")

        label = tk.Label(auth_root, text="Paste the authorization code here:")
        label.pack(pady=10)

        link_var = tk.StringVar()
        link_entry = tk.Entry(auth_root, width=40, textvariable=link_var)
        link_entry.pack(pady=10)

        ok_button = tk.Button(auth_root, text="OK", command=lambda: self.on_auth_ok(link_var.get(), auth_root, flow))
        ok_button.pack(pady=10)

        open_browser_button = tk.Button(auth_root, text="Open Browser", command=lambda: self.on_auth_open_browser(flow))
        open_browser_button.pack(pady=10)

        auth_root.wait_window()

        return getattr(self, 'gauth', None)

    def on_auth_ok(self, link, auth_root, flow):
        code = self.extract_authorization_code(link)
        if code:
            auth_root.destroy()
            credentials = flow.step2_exchange(code)
            self.gauth = GoogleAuth()
            self.gauth.credentials = credentials
        else:
            self.display_status("Warning: Invalid authorization code")

    def on_auth_open_browser(self, flow):
        authorize_url = self.get_authorize_url(flow)
        webbrowser.open_new(authorize_url)

    def download_files_from_google_drive(self, folder_link, output_folder, gauth):
        try:
            if not is_authenticated(gauth):
                self.display_status("Error: Authentication failed. Make sure you fill in the credentials correctly.")
                return

            folder_link = folder_link.split('?')[0]

            drive = GoogleDrive(gauth)

            folder_id = folder_link.split('/')[-1]

            file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()

            os.makedirs(output_folder, exist_ok=True)

            # Display alert message before downloading
            messagebox.showinfo("Konfirmasi", "Anda Akan Mengunduh Semua File Yang Tersedia Pada Link")
        
            for file in tqdm(file_list, desc="Downloading", unit="file", dynamic_ncols=True, leave=False):
                file.GetContentFile(os.path.join(output_folder, file['title']))

            self.display_status("Download completed.")
            messagebox.showinfo("Download Selesai!")
        except Exception as e:
            self.display_status(f"Error: {str(e)}")	
            
            
            
            
            

    def get_authorize_url(self, flow=None):
        if not flow:
            flow = OAuth2WebServerFlow(
                client_id='336430597454-4q3924j5lcafiedhmold73t95bajv8o4.apps.googleusercontent.com',
                client_secret='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',
                scope='https://www.googleapis.com/auth/drive',
                redirect_uri='http://localhost'
            )

        return flow.step1_get_authorize_url()

    @staticmethod
    def extract_authorization_code(link):
        match = re.search(r'code=([^&]+)', link)
        if match:
            return match.group(1)
        else:
            return None

    def display_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)


def is_authenticated(gauth):
    return gauth.credentials is not None and not gauth.credentials.access_token_expired


def main():
    root = tk.Tk()
    app = GoogleDriveDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

