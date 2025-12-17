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
        self.root.geometry("1000x900")
        self.root.configure(bg='#ffffff')

        # Variables
        self.download_path = tk.StringVar(value="reels_download")
        self.is_downloading = False
        self._placeholder = "Paste Instagram Reel URL here..."
        self._progress_total = 0
        self._progress_current = 0
        self.download_audio = tk.BooleanVar(value=False)
        self.current_post = None
        self.instaloader_context = None
        self._url_check_id = None

        self.setup_ui()
    
    def setup_ui(self):
        # Modern themed styling
        style = ttk.Style()
        style.theme_use('clam')
        
        # Modern color palette
        primary_color = '#2563eb'      # Modern blue
        primary_hover = '#1d4ed8'      # Darker blue
        text_dark = '#1f2937'          # Dark gray
        text_light = '#6b7280'         # Light gray
        bg_light = '#f9fafb'           # Very light gray
        border_color = '#e5e7eb'       # Border gray
        success_color = '#059669'      # Green
        
        # Configure styles
        style.configure('Header.TLabel', font=('Segoe UI', 24, 'bold'), foreground=text_dark, background='#ffffff')
        style.configure('Subheader.TLabel', font=('Segoe UI', 11, 'bold'), foreground=text_dark, background='#ffffff')
        style.configure('Sub.TLabel', font=('Segoe UI', 9), foreground=text_light, background='#ffffff')
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'), background=primary_color, foreground='white')
        style.map('Accent.TButton', background=[('active', primary_hover), ('pressed', primary_hover)])
        
        style.configure('Secondary.TButton', font=('Segoe UI', 9), background='#f3f4f6', foreground=text_dark)
        style.map('Secondary.TButton', background=[('active', '#e5e7eb')])
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=(24, 24, 24, 24))
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 24), sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(header_frame, text="Instagram Reel Downloader", style='Header.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(header_frame, text="Download reels with audio and captions", style='Sub.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(4, 0))

        # URL input section - Card style
        url_card = tk.Frame(main_frame, bg=bg_light, bd=1, relief=tk.FLAT)
        url_card.grid(row=1, column=0, columnspan=2, pady=(0, 16), sticky=(tk.W, tk.E))
        url_card.configure(highlightthickness=1, highlightbackground=border_color)
        
        url_label = ttk.Label(url_card, text="Reel URL", style='Subheader.TLabel', background=bg_light)
        url_label.pack(anchor=tk.W, padx=16, pady=(12, 6))

        # URL input with placeholder behavior
        self.url_text = tk.Text(url_card, height=4, wrap=tk.WORD, font=('Segoe UI', 10), 
                                relief=tk.FLAT, bd=0, bg='#ffffff', fg=text_light, padx=12, pady=10)
        self.url_text.pack(padx=12, pady=(0, 12), fill=tk.BOTH, expand=True)
        self.url_text.insert(1.0, self._placeholder)
        self.url_text.bind('<FocusIn>', self._clear_placeholder)
        self.url_text.bind('<FocusOut>', self._restore_placeholder)
        self.url_text.bind('<KeyRelease>', self._on_url_change)
        
        url_card.columnconfigure(0, weight=1)

        # Download path section
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 16))

        ttk.Label(path_frame, text="Save to:", style='Subheader.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 6))

        path_entry = ttk.Entry(path_frame, textvariable=self.download_path, font=('Segoe UI', 9))
        path_entry.grid(row=1, column=0, padx=(0, 8), sticky=(tk.W, tk.E))

        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_folder, style='Secondary.TButton')
        browse_btn.grid(row=1, column=1)

        path_frame.columnconfigure(0, weight=1)

        # Options and buttons frame
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=3, column=0, columnspan=2, pady=(0, 16), sticky=(tk.W, tk.E))
        
        # Audio checkbox
        self.audio_checkbox = ttk.Checkbutton(options_frame, text="Extract audio as MP3", variable=self.download_audio)
        self.audio_checkbox.pack(side=tk.LEFT, padx=(0, 20))

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 16), sticky=tk.W)

        self.download_btn = ttk.Button(button_frame, text="Download", command=self.start_download, style='Accent.TButton')
        self.download_btn.pack(side=tk.LEFT, padx=(0, 8))

        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_urls, style='Secondary.TButton')
        clear_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_download, state='disabled', style='Secondary.TButton')
        self.stop_btn.pack(side=tk.LEFT)

        # Progress section
        self.progress_var = tk.StringVar(value="Ready")
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var, style='Sub.TLabel')
        progress_label.grid(row=5, column=0, columnspan=2, pady=(0, 6), sticky=tk.W)

        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', length=700)
        self.progress_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 16))

        # Content display section (two columns)
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))

        # Caption card
        caption_card = tk.Frame(content_frame, bg=bg_light, bd=1, relief=tk.FLAT)
        caption_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        caption_card.configure(highlightthickness=1, highlightbackground=border_color)
        
        caption_label = ttk.Label(caption_card, text="Caption / Description", style='Subheader.TLabel', background=bg_light)
        caption_label.pack(anchor=tk.W, padx=12, pady=(12, 8))

        self.caption_text = scrolledtext.ScrolledText(caption_card, height=15, width=45, wrap=tk.WORD, 
                                                       font=('Segoe UI', 9), relief=tk.FLAT, bd=0, bg='#ffffff', fg=text_dark)
        self.caption_text.pack(padx=12, pady=(0, 12), fill=tk.BOTH, expand=True)
        self.caption_text.configure(state='disabled')

        # Log card
        log_card = tk.Frame(content_frame, bg=bg_light, bd=1, relief=tk.FLAT)
        log_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        log_card.configure(highlightthickness=1, highlightbackground=border_color)
        
        log_label = ttk.Label(log_card, text="Download Log", style='Subheader.TLabel', background=bg_light)
        log_label.pack(anchor=tk.W, padx=12, pady=(12, 8))

        self.log_text = scrolledtext.ScrolledText(log_card, height=15, width=45, wrap=tk.WORD, 
                                                   font=('Segoe UI', 8), relief=tk.FLAT, bd=0, bg='#1f2937', fg='#d1d5db')
        self.log_text.pack(padx=12, pady=(0, 12), fill=tk.BOTH, expand=True)
        self.log_text.configure(state='normal')

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            self.download_path.set(folder)
    
    def clear_urls(self):
        self.url_text.delete(1.0, tk.END)
        self.url_text.insert(1.0, self._placeholder)
        self.url_text.configure(foreground='#6b6f76')
        self.clear_caption()
    
    def clear_caption(self):
        """Clear the caption display"""
        def _update():
            self.caption_text.configure(state='normal')
            self.caption_text.delete(1.0, tk.END)
            self.caption_text.configure(state='disabled')
        
        self.root.after(0, _update)
    
    def _on_url_change(self, event=None):
        """Handle URL changes and auto-fetch caption"""
        if self._url_check_id:
            self.root.after_cancel(self._url_check_id)
        
        # Delay to avoid excessive processing while typing
        self._url_check_id = self.root.after(800, self._fetch_caption_from_url)
    
    def _fetch_caption_from_url(self):
        """Extract shortcode and fetch caption in background"""
        try:
            url_text = self.url_text.get(1.0, tk.END).strip()
            
            if not url_text or url_text == self._placeholder:
                self.clear_caption()
                return
            
            # Extract shortcode from URL
            url_parts = url_text.rstrip('/').split('/')
            if 'reel' not in url_parts:
                self.clear_caption()
                return
            
            shortcode_index = url_parts.index('reel') + 1
            if shortcode_index >= len(url_parts):
                self.clear_caption()
                return
            
            shortcode = url_parts[shortcode_index]
            
            # Fetch caption in a background thread
            fetch_thread = threading.Thread(target=self._fetch_and_display_caption, args=(shortcode,))
            fetch_thread.daemon = True
            fetch_thread.start()
        
        except Exception:
            self.clear_caption()
    
    def _fetch_and_display_caption(self, shortcode):
        """Fetch caption from Instagram and display it"""
        try:
            if not self.instaloader_context:
                L = instaloader.Instaloader(
                    download_pictures=False,
                    download_videos=False,
                    download_video_thumbnails=False,
                    download_geotags=False,
                    download_comments=False,
                    save_metadata=False
                )
                self.instaloader_context = L.context
            else:
                L = instaloader.Instaloader()
                L.context = self.instaloader_context
            
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            self.display_caption(post)
        
        except Exception as e:
            self.log_message(f"⚠ Could not fetch caption: {str(e)[:50]}")
    
    
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
            elif line and not line.startswith('Paste'):
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
        self.progress_var.set(f"Downloading {len(urls)} reel(s)...")
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
                    
                    # Display caption/description
                    self.display_caption(post)
                    
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
                            
                            # Download audio if checkbox is enabled
                            if self.download_audio.get():
                                self.progress_var.set(f"Downloading {i}/{len(urls)}: Extracting audio...")
                                self.extract_audio(video_path, shortcode)
                            
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
    def display_caption(self, post):
        """Display the caption/description of the reel in the caption text box"""
        def _update():
            self.caption_text.configure(state='normal')
            self.caption_text.delete(1.0, tk.END)
            
            caption = post.caption if post.caption else "No caption available"
            self.caption_text.insert(1.0, caption)
            self.caption_text.configure(state='disabled')
        
        self.root.after(0, _update)
    
    def extract_audio(self, video_path, shortcode):
        """Extract audio from video file using ffmpeg"""
        try:
            import subprocess
            
            audio_filename = f"{shortcode}.mp3"
            audio_path = os.path.join(self.download_path.get(), audio_filename)
            
            # Check if ffmpeg is installed
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            except FileNotFoundError:
                self.log_message("⚠ FFmpeg not installed. Skipping audio extraction.")
                self.log_message("  Install FFmpeg from: https://ffmpeg.org/download.html")
                return
            
            # Extract audio using ffmpeg
            command = [
                'ffmpeg',
                '-i', video_path,
                '-q:a', '0',
                '-map', 'a',
                '-y',  # Overwrite output file
                audio_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message(f"✓ Audio extracted: {audio_filename}")
            else:
                self.log_message(f"⚠ Failed to extract audio: {result.stderr}")
        
        except Exception as e:
            self.log_message(f"⚠ Error extracting audio: {str(e)}")
    
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