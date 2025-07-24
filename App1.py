import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, filedialog
import threading
import queue
import json
import os
import requests
import itertools
from datetime import datetime
import webbrowser
import re

# --- Configuration ---
API_KEY_GLOBAL = os.getenv('PERPLEXITY_API_KEY', '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')
BASE_URL = "https://api.perplexity.ai"

AVAILABLE_MODELS = [
    "sonar-small-online", "sonar-medium-online", "sonar-pro", "sonar-deep-research",
    "sonar-reasoning-pro", "sonar-reasoning", "sonar", "sonar-small-chat", "sonar-medium-chat",
    "llama-3-sonar-small-32k-chat", "llama-3-sonar-small-32k-online",
    "llama-3-sonar-large-32k-chat", "llama-3-sonar-large-32k-online",
    "codellama-70b-instruct", "mistral-7b-instruct", "mixtral-8x7b-instruct",
    "llama-3-8b-instruct", "llama-3-70b-instruct", "r1-1776",
    "pplx-7b-online", "pplx-70b-online", "pplx-7b-chat", "pplx-70b-chat",
]

# Conversation templates
CONVERSATION_TEMPLATES = {
    "General Assistant": "You are a helpful and concise AI assistant.",
    "Code Helper": "You are an expert programmer. Provide clear, well-commented code examples and explanations.",
    "Research Assistant": "You are a research assistant. Provide detailed, well-sourced information with citations when possible.",
    "Creative Writer": "You are a creative writing assistant. Help with storytelling, character development, and creative ideas.",
    "Technical Explainer": "You are a technical expert who explains complex concepts in simple, understandable terms.",
    "Problem Solver": "You are a problem-solving expert. Break down complex problems into manageable steps.",
}

# --- Enhanced PerplexityAPI Class ---
class PerplexityAPI:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key cannot be empty.")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.request_count = 0
        self.last_request_time = None

    def _handle_response_error(self, response: requests.Response):
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", response.text)
        except json.JSONDecodeError:
            error_message = response.text
        
        # Enhanced error messages
        if response.status_code == 401:
            error_message = "Invalid API key. Please check your API key and try again."
        elif response.status_code == 429:
            error_message = "Rate limit exceeded. Please wait a moment before trying again."
        elif response.status_code == 500:
            error_message = "Server error. Please try again later."
        
        raise requests.exceptions.HTTPError(
            f"API request failed with status {response.status_code}: {error_message}",
            response=response
        )

    def chat_completion(self, model, messages, stream=False, max_tokens=None, temperature=None,
                        top_p=None, top_k=None, presence_penalty=None, frequency_penalty=None,
                        timeout=60):
        endpoint = f"{BASE_URL}/chat/completions"
        payload = {
            "model": model, "messages": messages, "stream": stream
        }
        
        # Add optional parameters if they have a value
        if max_tokens is not None: payload["max_tokens"] = max_tokens
        if temperature is not None: payload["temperature"] = temperature
        if top_p is not None: payload["top_p"] = top_p
        if top_k is not None: payload["top_k"] = top_k
        if presence_penalty is not None: payload["presence_penalty"] = presence_penalty
        if frequency_penalty is not None: payload["frequency_penalty"] = frequency_penalty
        
        self.request_count += 1
        self.last_request_time = datetime.now()
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload, stream=stream, timeout=timeout)
            response.raise_for_status()
            if stream:
                return self._handle_streamed_response(response)
            else:
                return response.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                self._handle_response_error(e.response)
            raise

    def _handle_streamed_response(self, response: requests.Response):
        try:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        json_str = decoded_line[len('data: '):]
                        if json_str.strip() == "[DONE]":
                            yield {"done": True}
                            return
                        try:
                            chunk = json.loads(json_str)
                            yield chunk
                        except json.JSONDecodeError:
                            print(f"Warning: Could not decode JSON chunk: {json_str}")
        except Exception as e:
            print(f"Error while processing stream: {e}")
            yield {"error": str(e)}
        finally:
            response.close()

# --- Enhanced GUI Application ---
class PerplexityGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Perplexity AI GUI Client - Enhanced Edition")
        self.geometry("1200x800")
        self.configure(bg="#2B2B2B")
        
        # Initialize variables
        self.api_client = None
        self.conversation_history = []
        self.response_queue = queue.Queue()
        self.last_message_was_thinking = False
        self.thinking_animation_job = None
        self.thinking_text_options = ["Thinking.", "Thinking..", "Thinking..."]
        self.thinking_text_cycle = itertools.cycle(self.thinking_text_options)
        self.last_ai_response_content = ""
        self.conversation_sessions = {}  # Store multiple conversation sessions
        self.current_session_id = "default"
        self.auto_save_enabled = True
        
        self._setup_styles()
        self._setup_menu()
        self._setup_widgets()
        self._load_api_key()
        self._load_settings()
        
        # Auto-save timer
        self._schedule_auto_save()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')

        # Enhanced color scheme with better visibility
        main_bg = "#2B2B2B"
        frame_bg = "#3C3C3C"
        text_area_bg = "#1E1E1E"  # Darker background for better contrast
        text_fg = "#E8E8E8"  # Brighter text
        entry_bg = "#333333"
        button_bg = "#007ACC"
        button_fg = "#FFFFFF"
        button_active_bg = "#005FA3"
        label_fg = "#DDDDDD"  # Brighter labels
        accent_color = "#FF6B35"

        self.configure(bg=main_bg)
        style.configure("TFrame", background=main_bg)
        style.configure("Content.TFrame", background=frame_bg)
        style.configure("TLabel", background=main_bg, foreground=label_fg, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=main_bg, foreground=text_fg, font=("Segoe UI", 12, "bold"))  # Larger headers
        style.configure("TButton", background=button_bg, foreground=button_fg, font=("Segoe UI", 10, "bold"), borderwidth=1, relief="raised", padding=5)
        style.map("TButton",
                  background=[('active', button_active_bg), ('pressed', button_active_bg)],
                  relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        style.configure("Accent.TButton", background=accent_color, foreground=button_fg)
        style.map("Accent.TButton", background=[('active', '#E55A2B')])
        style.configure("TEntry", fieldbackground=entry_bg, foreground=text_fg, insertcolor=text_fg, font=("Segoe UI", 10), borderwidth=1, relief="sunken")
        style.configure("TCombobox", fieldbackground=entry_bg, foreground=text_fg, selectbackground=button_bg, font=("Segoe UI", 10), arrowcolor=text_fg)
        self.option_add("*TCombobox*Listbox*Background", entry_bg)
        self.option_add("*TCombobox*Listbox*Foreground", text_fg)
        self.option_add("*TCombobox*Listbox*selectBackground", button_bg)
        self.option_add("*TCombobox*Listbox*selectForeground", button_fg)
        style.configure("Control.TCheckbutton", background=main_bg, foreground=label_fg, font=("Segoe UI", 10))
        style.map("Control.TCheckbutton", indicatorcolor=[('selected', button_bg)], background=[('active', frame_bg)])
        
        # Simplified LabelFrame style - more compatible
        try:
            style.configure("TLabelFrame", background=main_bg, relief="groove", borderwidth=1)
            style.configure("TLabelFrame.Label", background=main_bg, foreground=text_fg, font=("Segoe UI", 10, "bold"))
        except:
            # Fallback if TLabelFrame styling fails
            pass

        # Enhanced text styling with better visibility
        self.text_bg = text_area_bg
        self.text_fg = text_fg
        self.user_fg = "#4FC3F7"  # Brighter blue for better visibility
        self.assistant_fg = "#81C784"  # Changed to green for much better contrast
        self.system_fg = "#FFB74D"  # Orange for system messages
        self.error_fg = "#F44747"
        self.accent_fg = accent_color

    def _setup_menu(self):
        menubar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.text_bg, fg=self.text_fg)
        file_menu.add_command(label="New Conversation", command=self._new_conversation, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Save Chat", command=self._save_chat_history, accelerator="Ctrl+S")
        file_menu.add_command(label="Load Chat", command=self._load_chat_history, accelerator="Ctrl+O")
        file_menu.add_command(label="Export as Text", command=self._export_as_text, accelerator="Ctrl+E")
        file_menu.add_command(label="Export as HTML", command=self._export_as_html)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self._show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.text_bg, fg=self.text_fg)
        edit_menu.add_command(label="Copy Last Response", command=self._copy_last_response, accelerator="Ctrl+C")
        edit_menu.add_command(label="Clear Chat", command=self._clear_chat, accelerator="Ctrl+L")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find in Chat", command=self._find_in_chat, accelerator="Ctrl+F")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.text_bg, fg=self.text_fg)
        tools_menu.add_command(label="Word Count", command=self._show_word_count)
        tools_menu.add_command(label="API Usage Stats", command=self._show_api_stats)
        tools_menu.add_command(label="Validate API Key", command=self._validate_api_key)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.text_bg, fg=self.text_fg)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        help_menu.add_command(label="Perplexity API Docs", command=lambda: webbrowser.open("https://docs.perplexity.ai/"))
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menubar)
        
        # Keyboard bindings
        self.bind_all("<Control-s>", lambda event: self._save_chat_history())
        self.bind_all("<Control-o>", lambda event: self._load_chat_history())
        self.bind_all("<Control-n>", lambda event: self._new_conversation())
        self.bind_all("<Control-l>", lambda event: self._clear_chat())
        self.bind_all("<Control-e>", lambda event: self._export_as_text())
        self.bind_all("<Control-f>", lambda event: self._find_in_chat())
        self.bind_all("<Control-c>", lambda event: self._copy_last_response())

    def _create_labeled_frame(self, parent, text, **kwargs):
        """Create a labeled frame with fallback for styling issues."""
        frame = ttk.Frame(parent, style="Content.TFrame", **kwargs)
        if text:
            label = ttk.Label(frame, text=text, style="Header.TLabel")
            label.pack(anchor="w", padx=5, pady=(0,5))
        return frame