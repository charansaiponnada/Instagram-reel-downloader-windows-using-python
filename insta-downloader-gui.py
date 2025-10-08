import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import instaloader
import threading
import os
import requests
from datetime import datetime

class InstaDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Reel Downloader")
        # Improved size and background for a modern look
        self.root.geometry("720x560")
        self.root.configure(bg='#f5f7fa')

        # Variables
        self.download_path = tk.StringVar(value="reels_download")
        self.is_downloading = False
        self._placeholder = "Enter one or more Reel URLs here, one per line..."
        self._progress_total = 0
        self._progress_current = 0

        self.setup_ui()
    
    def setup_ui(self):
        # Themed styling
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('Header.TLabel', font=('Helvetica', 18, 'bold'), foreground='#13315c')
        style.configure('Sub.TLabel', font=('Helvetica', 10), foreground='#394049')
        style.configure('Accent.TButton', background='#2b8cff', foreground='white')
        style.map('Accent.TButton', background=[('active', '#1865d6')])

        # Main frame
        main_frame = ttk.Frame(self.root, padding=(18, 18, 18, 12))
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="Instagram Reel Downloader", style='Header.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # URL input section
        url_label = ttk.Label(main_frame, text="Enter Reel URLs (one per line):", style='Sub.TLabel')
        url_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        # URL input with placeholder behavior
        self.url_text = scrolledtext.ScrolledText(main_frame, height=10, width=80, wrap=tk.WORD)
        self.url_text.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        self.url_text.insert(1.0, self._placeholder)
        self.url_text.configure(foreground='#6b6f76')
        self.url_text.bind('<FocusIn>', self._clear_placeholder)
        self.url_text.bind('<FocusOut>', self._restore_placeholder)

        # Download path section
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(path_frame, text="Download folder:").grid(row=0, column=0, sticky=tk.W)

        path_entry = ttk.Entry(path_frame, textvariable=self.download_path, width=52)
        path_entry.grid(row=1, column=0, padx=(0, 10), sticky=(tk.W, tk.E))

        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_folder)
        browse_btn.grid(row=1, column=1)

        path_frame.columnconfigure(0, weight=1)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(6, 6), sticky=tk.W)

        self.download_btn = ttk.Button(button_frame, text="Download Reels", command=self.start_download, style='Accent.TButton')
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))

        clear_btn = ttk.Button(button_frame, text="Clear URLs", command=self.clear_urls)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_download, state='disabled')
        self.stop_btn.pack(side=tk.LEFT)

        # Keyboard shortcuts
        self.root.bind('<Control-d>', lambda e: self.start_download())
        self.root.bind('<Control-o>', lambda e: self.browse_folder())
        self.root.bind('<Control-l>', lambda e: self.clear_urls())

        # Tooltips
        self._add_tooltip(self.download_btn, 'Start downloading the entered reel URLs (Ctrl+D)')
        self._add_tooltip(browse_btn, 'Choose a folder to save downloaded reels (Ctrl+O)')
        self._add_tooltip(clear_btn, 'Clear the URL input box (Ctrl+L)')

        # Progress
        self.progress_var = tk.StringVar(value="Ready")
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var, style='Sub.TLabel')
        progress_label.grid(row=5, column=0, columnspan=2, pady=(18, 6), sticky=tk.W)

        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', length=560)
        self.progress_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 12))

        # Log output
        log_label = ttk.Label(main_frame, text="Download Log:", style='Sub.TLabel')
        log_label.grid(row=7, column=0, sticky=tk.W, pady=(10, 5))

        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, width=80, wrap=tk.WORD)
        self.log_text.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_text.configure(state='normal')

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            self.download_path.set(folder)
    
    def clear_urls(self):
        self.url_text.delete(1.0, tk.END)
        self.url_text.insert(1.0, self._placeholder)
        self.url_text.configure(foreground='#6b6f76')
    
    def log_message(self, message):
        # Thread-safe UI update
        timestamp = datetime.now().strftime("%H:%M:%S")
        def _append():
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
        self.root.after(0, _append)
    
    def start_download(self):
        urls_text = self.url_text.get(1.0, tk.END).strip()
        if not urls_text or urls_text == self._placeholder:
            messagebox.showwarning("Warning", "Please enter at least one URL")
            return
        
        # Parse URLs (handle both comma-separated and line-separated)
        urls = []
        for line in urls_text.split('\n'):
            line = line.strip()
            if ',' in line:
                urls.extend([url.strip() for url in line.split(',') if url.strip()])
            elif line:
                urls.append(line)
        
        if not urls:
            messagebox.showwarning("Warning", "No valid URLs found")
            return
        
        # Validate download path
        download_folder = self.download_path.get()
        if not download_folder:
            messagebox.showwarning("Warning", "Please select a download folder")
            return
        
        # Create folder if it doesn't exist
        try:
            os.makedirs(download_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot create download folder: {e}")
            return

        # Start download in a separate thread with determinate progress
        self.is_downloading = True
        self.download_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self._progress_total = len(urls)
        self._progress_current = 0
        self.progress_bar['maximum'] = max(1, self._progress_total)
        self.progress_bar['value'] = 0
        self.progress_var.set(f"Starting download of {len(urls)} reel(s)...")
        self.log_text.delete(1.0, tk.END)

        self.download_thread = threading.Thread(target=self.download_reels, args=(urls,))
        self.download_thread.daemon = True
        self.download_thread.start()
    
    def stop_download(self):
        self.is_downloading = False
        self.progress_var.set("Stopping...")
        self.log_message("Download stopped by user")
    
    def download_reels(self, urls):
        try:
            # Create an instance of the Instaloader class with custom settings
            L = instaloader.Instaloader(
                download_pictures=False,      # Don't download pictures
                download_videos=True,         # Download videos
                download_video_thumbnails=False,  # Don't download thumbnails
                download_geotags=False,       # Don't download geotags
                download_comments=False,      # Don't download comments
                save_metadata=False,          # Don't save metadata
                compress_json=False           # Don't compress JSON
            )
            
            successful_downloads = 0
            failed_downloads = 0
            
            for i, url in enumerate(urls, 1):
                if not self.is_downloading:
                    break
                
                try:
                    self.progress_var.set(f"Downloading {i}/{len(urls)}: Processing URL...")
                    self.log_message(f"Processing URL {i}/{len(urls)}: {url}")
                    
                    # Extract shortcode from URL
                    url_parts = url.rstrip('/').split('/')
                    if 'reel' in url_parts:
                        shortcode_index = url_parts.index('reel') + 1
                        if shortcode_index < len(url_parts):
                            shortcode = url_parts[shortcode_index]
                        else:
                            raise ValueError("Invalid URL format")
                    else:
                        raise ValueError("URL does not contain 'reel'")
                    
                    # Get the post object from the shortcode
                    post = instaloader.Post.from_shortcode(L.context, shortcode)
                    
                    # Download only the video file
                    if post.is_video:
                        self.progress_var.set(f"Downloading {i}/{len(urls)}: Saving video...")
                        
                        # Create a custom filename
                        video_filename = f"{shortcode}.mp4"
                        video_path = os.path.join(self.download_path.get(), video_filename)
                        
                        # Download the video URL directly
                        import requests
                        video_response = requests.get(post.video_url, stream=True)
                        video_response.raise_for_status()
                        
                        with open(video_path, 'wb') as video_file:
                            for chunk in video_response.iter_content(chunk_size=8192):
                                if chunk and self.is_downloading:
                                    video_file.write(chunk)
                                elif not self.is_downloading:
                                    break
                        
                        if self.is_downloading:
                            successful_downloads += 1
                            self.log_message(f"✓ Successfully downloaded video: {video_filename}")
                            self._increment_progress()
                        else:
                            # Remove incomplete file if download was stopped
                            if os.path.exists(video_path):
                                os.remove(video_path)
                            break
                    else:
                        self.log_message(f"⚠ URL is not a video reel: {url}")
                        failed_downloads += 1
                        self._increment_progress()
                    
                except Exception as e:
                    failed_downloads += 1
                    self.log_message(f"✗ Failed to download {url}: {str(e)}")
                    self._increment_progress()
            
            # Final summary
            if self.is_downloading:
                self.progress_var.set(f"Completed: {successful_downloads} successful, {failed_downloads} failed")
                self.log_message(f"\n=== Download Summary ===")
                self.log_message(f"Total processed: {len(urls)}")
                self.log_message(f"Successful: {successful_downloads}")
                self.log_message(f"Failed: {failed_downloads}")
                
                if successful_downloads > 0:
                    self.log_message(f"Files saved to: {self.download_path.get()}")
            
        except Exception as e:
            self.log_message(f"Critical error: {str(e)}")
            self.progress_var.set("Error occurred")
        
        finally:
            # Reset UI state
            self.is_downloading = False
            self.download_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            # Ensure determinate progress bar is complete
            try:
                self.progress_bar['value'] = self._progress_total
            except Exception:
                pass
            
            if not hasattr(self, 'progress_var') or 'Error' not in self.progress_var.get():
                if successful_downloads > 0:
                    messagebox.showinfo("Complete", 
                                      f"Download completed!\n"
                                      f"Successful: {successful_downloads}\n"
                                      f"Failed: {failed_downloads}")

    # --- UI helpers ---
    def _increment_progress(self):
        # Called from download thread; schedule UI update
        def _step():
            self._progress_current += 1
            try:
                self.progress_bar['value'] = self._progress_current
                self.progress_var.set(f"{self._progress_current}/{self._progress_total} completed")
            except Exception:
                pass
        self.root.after(0, _step)

    def _clear_placeholder(self, event=None):
        content = self.url_text.get(1.0, tk.END).strip()
        if content == self._placeholder:
            self.url_text.delete(1.0, tk.END)
            self.url_text.configure(foreground='black')

    def _restore_placeholder(self, event=None):
        content = self.url_text.get(1.0, tk.END).strip()
        if not content:
            self.url_text.insert(1.0, self._placeholder)
            self.url_text.configure(foreground='#6b6f76')

    def _add_tooltip(self, widget, text):
        # Simple tooltip implementation
        class Tooltip:
            def __init__(self, w, t):
                self.w = w
                self.t = t
                self.tipwin = None
                w.bind('<Enter>', self.show)
                w.bind('<Leave>', self.hide)
            def show(self, e=None):
                if self.tipwin or not self.t:
                    return
                x = e.x_root + 12
                y = e.y_root + 12
                self.tipwin = tw = tk.Toplevel(self.w)
                tw.wm_overrideredirect(True)
                tw.wm_geometry(f"+{x}+{y}")
                label = tk.Label(tw, text=self.t, justify=tk.LEFT,
                                 background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                                 font=("tahoma", "8", "normal"))
                label.pack(ipadx=4)
            def hide(self, e=None):
                if self.tipwin:
                    self.tipwin.destroy()
                    self.tipwin = None
        Tooltip(widget, text)

def main():
    root = tk.Tk()
    app = InstaDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()