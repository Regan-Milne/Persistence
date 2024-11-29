import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from chat_interface_dev import ChatInterface
from queue import Queue
import time
import subprocess
import os

def check_ollama_running():
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version")
        return response.status_code == 200
    except:
        return False

def start_ollama():
    try:
        # Attempt to start Ollama
        subprocess.Popen(["ollama", "serve"])
        # Wait for it to start
        time.sleep(2)
        return check_ollama_running()
    except:
        return False

def ensure_model_pulled():
    try:
        import ollama
        models = ollama.list()
        if not any(model.get('name', '').startswith('mistral-nemo') for model in models['models']):
            print("Pulling mistral-nemo model...")
            ollama.pull('mistral-nemo')
        return True
    except Exception as e:
        print(f"Error ensuring model: {str(e)}")
        return False

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
        self.input_bg = "#2b2b2b"  # Slightly lighter than background
        self.button_bg = "#4a4a4a"  # Medium gray for buttons
        self.button_active = "#666666"  # Lighter gray for button hover

        # Configure the root window background
        self.root.configure(bg=self.bg_color)
        
        # Create and configure the main frame
        self.main_frame = tk.Frame(root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            bg=self.bg_color,
            fg=self.text_color,
            font=("Consolas", 10),
            insertbackground=self.text_color
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create bottom frame for input and buttons
        self.bottom_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.bottom_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create input field using tk.Entry for better styling control
        self.input_field = tk.Entry(
            self.bottom_frame,
            bg=self.input_bg,
            fg=self.text_color,
            insertbackground=self.text_color,  # Cursor color
            font=("Consolas", 10),
            relief=tk.FLAT
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Enable input field immediately for testing
        self.input_field.config(state='normal')
        
        # Bind Enter key to send_message
        self.input_field.bind("<Return>", lambda e: self.send_message())
        
        # Create send button
        self.send_button = tk.Button(
            self.bottom_frame,
            text="Send",
            command=self.send_message,
            bg=self.button_bg,
            fg=self.text_color,
            activebackground=self.button_active,
            activeforeground=self.text_color,
            relief=tk.FLAT
        )
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        # Create new session button
        self.new_session_button = tk.Button(
            self.bottom_frame,
            text="New Session",
            command=self.new_session,
            bg=self.button_bg,
            fg=self.text_color,
            activebackground=self.button_active,
            activeforeground=self.text_color,
            relief=tk.FLAT
        )
        self.new_session_button.pack(side=tk.LEFT)
        
        # Initialize message queue and start queue processing
        self.msg_queue = Queue()
        self.process_queue()
        
        # Initialize chat interface
        self.initialize_chat()
        
        # Set focus to input field
        self.input_field.focus_set()
        
        # Print debug info
        print("GUI initialized, input field should be enabled")

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
                    self.send_button.config(state='normal'),
                    self.new_session_button.config(state='normal')
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
        if self.chat:
            self.chat.new_session()
            self.append_to_chat("\n=== New Session Started ===\n\n")

    def append_to_chat(self, message):
        self.msg_queue.put(message)

    def process_queue(self):
        while not self.msg_queue.empty():
            message = self.msg_queue.get()
            self.chat_display.insert(tk.END, message)
            self.chat_display.see(tk.END)
        self.root.after(100, self.process_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGUI(root)
    root.mainloop()
