import subprocess
import time
import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext
from chat_interface import ChatInterface
import threading
import queue

class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Chat Interface")
        self.root.geometry("800x600")
        
        # Initialize chat as None
        self.chat = None
        
        # Configure dark theme colors
        self.bg_color = "#1a1a1a"  # Dark background
        self.text_color = "#4ae1dc"  # Greenish-blue text
        self.input_bg = "#2b2b2b"  # Dark grey for input background
        
        # Configure fonts
        self.chat_font = ("Segoe UI", 12)  # Larger, modern font for chat
        self.input_font = ("Segoe UI", 11)  # Slightly smaller for input
        
        # Configure root theme
        self.root.configure(bg=self.bg_color)
        style = ttk.Style()
        style.configure("Custom.TFrame", background=self.bg_color)
        style.configure("Custom.TButton", 
                       background=self.bg_color, 
                       foreground=self.text_color,
                       bordercolor=self.text_color,
                       font=self.input_font)
        
        # Create a custom style for the Entry widget
        self.root.option_add("*TEntry*Background", self.input_bg)
        self.root.option_add("*TEntry*Foreground", self.text_color)  # Match the chat text color
        style.configure("Custom.TEntry", 
                       fieldbackground=self.input_bg,
                       foreground=self.text_color,
                       insertcolor=self.text_color,  # Cursor color
                       font=self.input_font)
        
        # Message queue for thread-safe GUI updates
        self.msg_queue = queue.Queue()
        
        # Create and configure main container
        self.main_container = ttk.Frame(root, padding="10", style="Custom.TFrame")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Create chat display with dark theme
        self.chat_display = scrolledtext.ScrolledText(
            self.main_container, 
            wrap=tk.WORD, 
            height=20,
            bg=self.bg_color,
            fg=self.text_color,
            insertbackground=self.text_color,  # Cursor color
            selectbackground=self.text_color,  # Selection background
            selectforeground=self.bg_color,    # Selection text color
            font=self.chat_font,               # Larger font
            padx=10,                           # Add padding for better readability
            pady=10
        )
        self.chat_display.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create input field with dark theme
        self.input_field = tk.Entry(
            self.main_container,
            font=self.input_font,
            bg=self.input_bg,
            fg=self.text_color,
            insertbackground=self.text_color,  # Cursor color
            relief="solid",
            bd=1,  # Border width
            highlightthickness=1,
            highlightbackground=self.text_color,  # Border color
            highlightcolor=self.text_color,  # Focus border color
            insertwidth=2  # Make cursor more visible
        )
        self.input_field.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.input_field.focus_set()  # Give focus to input field
        
        # Bind Enter key to send message
        self.input_field.bind('<Return>', lambda e: self.send_message())
        
        # Create buttons frame
        self.buttons_frame = ttk.Frame(self.main_container, style="Custom.TFrame")
        self.buttons_frame.grid(row=1, column=1, sticky=(tk.E))
        
        # Create buttons with dark theme
        self.send_button = ttk.Button(
            self.buttons_frame, 
            text="Send", 
            command=self.send_message,
            style="Custom.TButton",
            padding="5 3"  # Add some padding to buttons
        )
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        self.new_session_button = ttk.Button(
            self.buttons_frame, 
            text="New Session", 
            command=self.new_session,
            style="Custom.TButton",
            padding="5 3"  # Add some padding to buttons
        )
        self.new_session_button.pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(0, weight=1)
        
        # Initialize chat interface
        self.initialize_chat()
        
        # Start message processing
        self.process_messages()

    def initialize_chat(self):
        def setup():
            try:
                self.append_to_chat("Checking Ollama server...\n")
                if not check_ollama_running():
                    self.append_to_chat("Starting Ollama server...\n")
                    if not start_ollama():
                        self.append_to_chat("Failed to start Ollama. Please start it manually.\n")
                        return
                else:
                    self.append_to_chat("Ollama server is running.\n")
                
                self.append_to_chat("Checking model availability...\n")
                if not ensure_model_pulled():
                    self.append_to_chat("Failed to ensure model availability.\n")
                    return
                self.append_to_chat("Model is available.\n")
                
                self.append_to_chat("Initializing chat interface...\n")
                try:
                    self.chat = ChatInterface()
                    self.append_to_chat("Chat interface initialized successfully!\n")
                except Exception as e:
                    self.append_to_chat(f"Error initializing chat interface: {str(e)}\n")
                    return
                
                self.append_to_chat("Chat interface ready! You can start chatting.\n")
                
                # Enable input on the main thread
                self.root.after(0, lambda: [
                    self.input_field.config(state='normal'),
                    self.send_button.config(state='normal'),
                    self.new_session_button.config(state='normal'),
                    self.input_field.focus_set()
                ])
            except Exception as e:
                self.append_to_chat(f"Initialization error: {str(e)}\n")
        
        # Start initialization in a separate thread
        threading.Thread(target=setup, daemon=True).start()

    def send_message(self):
        if self.chat is None:
            self.append_to_chat("Please wait for initialization to complete...\n")
            return
            
        message = self.input_field.get().strip()
        if not message:
            return
            
        self.input_field.delete(0, tk.END)
        self.append_to_chat(f"\nYou: {message}\n\n")
        
        # Process message in a separate thread
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()

    def process_message(self, message):
        if self.chat is None:
            self.msg_queue.put("Chat interface not ready. Please wait...\n")
            return
            
        try:
            response = self.chat.chat(message)
            self.msg_queue.put(f"Assistant: {response}\n\n")
        except Exception as e:
            self.msg_queue.put(f"Error: {str(e)}\n\n")
            if not check_ollama_running():
                self.msg_queue.put("Ollama server appears to be down. Attempting to restart...\n")
                if start_ollama():
                    self.msg_queue.put("Ollama restarted successfully! Please try your message again.\n\n")
                else:
                    self.msg_queue.put("Failed to restart Ollama. Please check your installation.\n\n")

    def new_session(self):
        self.chat.new_session()
        self.append_to_chat("\nStarted new session.\n\n")

    def append_to_chat(self, message):
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, message)
        self.chat_display.see(tk.END)
        self.chat_display.configure(state='disabled')

    def process_messages(self):
        try:
            while True:
                message = self.msg_queue.get_nowait()
                self.append_to_chat(message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_messages)

def check_ollama_running():
    print("Checking if Ollama process exists...")
    try:
        result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq ollama.exe"], capture_output=True, text=True)
        if "ollama.exe" in result.stdout:
            print("Ollama process found")
            return True
        print("Ollama process not found")
        return False
    except Exception as e:
        print(f"Error checking Ollama process: {e}")
        return False

def start_ollama():
    print("Attempting to start Ollama server...")
    try:
        subprocess.Popen(["ollama", "serve"], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        print("Ollama server process started")
        
        # Wait for server to be ready
        max_attempts = 5
        for attempt in range(max_attempts):
            print(f"Checking server readiness (attempt {attempt + 1}/{max_attempts})...")
            try:
                import ollama
                models = ollama.list()
                print("Server is responsive!")
                return True
            except Exception as e:
                print(f"Server not ready yet: {e}")
                time.sleep(2)
        print("Failed to verify server readiness")
        return False
    except Exception as e:
        print(f"Error starting Ollama: {e}")
        return False

def ensure_model_pulled(model_name="qwq:latest"):
    print(f"Checking if model {model_name} is available...")
    try:
        import ollama
        models = ollama.list()
        print("Available models:", [m.get('name', '') for m in models['models']])
        
        if any(m.get('name', '') == model_name for m in models['models']):
            print(f"Model {model_name} is already pulled")
            return True
            
        print(f"Pulling model {model_name}...")
        ollama.pull(model_name)
        print(f"Successfully pulled {model_name}")
        return True
    except Exception as e:
        print(f"Error checking/pulling model: {e}")
        return False

def main():
    root = tk.Tk()
    app = ChatGUI(root)
    
    print("\nStarting initialization...")
    if not check_ollama_running():
        print("Starting Ollama server...")
        if not start_ollama():
            print("Failed to start Ollama server")
            return
        
    print("\nChecking model availability...")
    if not ensure_model_pulled():
        print("Failed to ensure model availability")
        return
        
    print("\nInitializing chat interface...")
    root.mainloop()

if __name__ == "__main__":
    main()
