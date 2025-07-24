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

CONVERSATION_TEMPLATES = {
    "General Assistant": "You are a helpful and concise AI assistant.",
    "Code Helper": "You are an expert programmer. Provide clear, well-commented code examples and explanations.",
    "Research Assistant": "You are a research assistant. Provide detailed, well-sourced information with citations when possible.",
    "Creative Writer": "You are a creative writing assistant. Help with storytelling, character development, and creative ideas.",
    "Technical Explainer": "You are a technical expert who explains complex concepts in simple, understandable terms.",
    "Problem Solver": "You are a problem-solving expert. Break down complex problems into manageable steps.",
}

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
        payload = {"model": model, "messages": messages, "stream": stream}
        
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

class PerplexityGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Perplexity AI GUI Client - Enhanced Edition")
        self.geometry("1200x800")
        self.configure(bg="#2B2B2B")
        
        self.api_client = None
        self.conversation_history = []
        self.response_queue = queue.Queue()
        self.last_message_was_thinking = False
        self.thinking_animation_job = None
        self.thinking_text_options = ["Thinking.", "Thinking..", "Thinking..."]
        self.thinking_text_cycle = itertools.cycle(self.thinking_text_options)
        self.last_ai_response_content = ""
        self.conversation_sessions = {}
        self.current_session_id = "default"
        self.auto_save_enabled = True
        
        self._setup_styles()
        self._setup_menu()
        self._setup_widgets()
        self._load_api_key()
        self._load_settings()
        self._schedule_auto_save()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        
        main_bg = "#2B2B2B"
        frame_bg = "#3C3C3C"
        text_area_bg = "#1E1E1E"
        text_fg = "#E8E8E8"
        entry_bg = "#333333"
        button_bg = "#007ACC"
        button_fg = "#FFFFFF"
        button_active_bg = "#005FA3"
        label_fg = "#DDDDDD"
        accent_color = "#FF6B35"

        self.configure(bg=main_bg)
        style.configure("TFrame", background=main_bg)
        style.configure("Content.TFrame", background=frame_bg)
        style.configure("TLabel", background=main_bg, foreground=label_fg, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=main_bg, foreground=text_fg, font=("Segoe UI", 12, "bold"))
        style.configure("TButton", background=button_bg, foreground=button_fg, font=("Segoe UI", 10, "bold"), borderwidth=1, relief="raised", padding=5)
        style.map("TButton", background=[('active', button_active_bg), ('pressed', button_active_bg)], relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        style.configure("Accent.TButton", background=accent_color, foreground=button_fg)
        style.map("Accent.TButton", background=[('active', '#E55A2B')])
        style.configure("TEntry", fieldbackground=entry_bg, foreground=text_fg, insertcolor=text_fg, font=("Segoe UI", 10), borderwidth=1, relief="sunken")
        style.configure("TCombobox", fieldbackground=entry_bg, foreground=text_fg, selectbackground=button_bg, font=("Segoe UI", 10), arrowcolor=text_fg)
        style.configure("Control.TCheckbutton", background=main_bg, foreground=label_fg, font=("Segoe UI", 10))
        style.map("Control.TCheckbutton", indicatorcolor=[('selected', button_bg)], background=[('active', frame_bg)])
        
        self.text_bg = text_area_bg
        self.text_fg = text_fg
        self.user_fg = "#4FC3F7"
        self.assistant_fg = "#81C784"
        self.system_fg = "#FFB74D"
        self.error_fg = "#F44747"
        self.accent_fg = accent_color

    def _setup_menu(self):
        menubar = tk.Menu(self)
        
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
        
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.text_bg, fg=self.text_fg)
        edit_menu.add_command(label="Copy Last Response", command=self._copy_last_response, accelerator="Ctrl+C")
        edit_menu.add_command(label="Clear Chat", command=self._clear_chat, accelerator="Ctrl+L")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find in Chat", command=self._find_in_chat, accelerator="Ctrl+F")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.text_bg, fg=self.text_fg)
        tools_menu.add_command(label="Word Count", command=self._show_word_count)
        tools_menu.add_command(label="API Usage Stats", command=self._show_api_stats)
        tools_menu.add_command(label="Validate API Key", command=self._validate_api_key)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.text_bg, fg=self.text_fg)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        help_menu.add_command(label="Perplexity API Docs", command=lambda: webbrowser.open("https://docs.perplexity.ai/"))
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menubar)
        
        self.bind_all("<Control-s>", lambda event: self._save_chat_history())
        self.bind_all("<Control-o>", lambda event: self._load_chat_history())
        self.bind_all("<Control-n>", lambda event: self._new_conversation())
        self.bind_all("<Control-l>", lambda event: self._clear_chat())
        self.bind_all("<Control-e>", lambda event: self._export_as_text())
        self.bind_all("<Control-f>", lambda event: self._find_in_chat())
        self.bind_all("<Control-c>", lambda event: self._copy_last_response())

    def _create_labeled_frame(self, parent, text, **kwargs):
        frame = ttk.Frame(parent, style="Content.TFrame", **kwargs)
        if text:
            label = ttk.Label(frame, text=text, style="Header.TLabel")
            label.pack(anchor="w", padx=5, pady=(0,5))
        return frame

    def _setup_widgets(self):
        main_container = ttk.Frame(self, padding="10 10 10 10", style="TFrame")
        main_container.pack(expand=True, fill=tk.BOTH)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # Top Controls
        top_controls_frame = ttk.Frame(main_container, style="TFrame", padding="0 0 0 10")
        top_controls_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,10))
        
        # API Key section
        api_frame = self._create_labeled_frame(top_controls_frame, text="API Configuration", padding="5")
        api_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        
        ttk.Label(api_frame, text="API Key:", style="TLabel").pack(side=tk.LEFT, padx=(0,5))
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=30, font=("Segoe UI", 9), show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=(0,5), expand=True, fill=tk.X)
        self.set_api_key_button = ttk.Button(api_frame, text="Set", command=self._set_api_key, width=5)
        self.set_api_key_button.pack(side=tk.LEFT, padx=(0,5))
        self.toggle_key_button = ttk.Button(api_frame, text="👁", command=self._toggle_api_key_visibility, width=3)
        self.toggle_key_button.pack(side=tk.LEFT)

        # Model and template section
        model_frame = self._create_labeled_frame(top_controls_frame, text="Model & Template", padding="5")
        model_frame.pack(side=tk.RIGHT, padx=(10,0))
        
        ttk.Label(model_frame, text="Model:", style="TLabel").pack(side=tk.LEFT, padx=(0,5))
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(model_frame, textvariable=self.model_var, values=AVAILABLE_MODELS, state="readonly", width=25, font=("Segoe UI", 9))
        if AVAILABLE_MODELS: self.model_dropdown.set(AVAILABLE_MODELS[6])
        self.model_dropdown.pack(side=tk.LEFT, padx=(0,10))
        
        ttk.Label(model_frame, text="Template:", style="TLabel").pack(side=tk.LEFT, padx=(0,5))
        self.template_var = tk.StringVar()
        self.template_dropdown = ttk.Combobox(model_frame, textvariable=self.template_var, values=list(CONVERSATION_TEMPLATES.keys()), state="readonly", width=20, font=("Segoe UI", 9))
        self.template_dropdown.set("General Assistant")
        self.template_dropdown.bind("<<ComboboxSelected>>", self._on_template_change)
        self.template_dropdown.pack(side=tk.LEFT)

        # Main Content Area
        main_paned_window = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        main_paned_window.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0,10))

        # Left Panel: Enhanced Chat Display
        left_panel = ttk.Frame(main_paned_window, style="Content.TFrame")
        
        chat_header_label = ttk.Label(left_panel, text="Chat Display", style="Header.TLabel")
        chat_header_label.pack(anchor="w", padx=10, pady=(5,0))

        chat_header = ttk.Frame(left_panel, style="Content.TFrame")
        chat_header.pack(fill=tk.X, padx=10, pady=5)
        
        self.session_label = ttk.Label(chat_header, text="Session: Default", style="Header.TLabel")
        self.session_label.pack(side=tk.LEFT)
        
        nav_frame = ttk.Frame(chat_header, style="Content.TFrame")
        nav_frame.pack(side=tk.RIGHT)
        
        ttk.Button(nav_frame, text="⬆️ Top", command=self._scroll_to_top, width=8).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(nav_frame, text="⬇️ Bottom", command=self._scroll_to_bottom, width=8).pack(side=tk.LEFT, padx=(0,5))
        
        self.message_count_label = ttk.Label(nav_frame, text="Messages: 0", style="TLabel")
        self.message_count_label.pack(side=tk.LEFT, padx=(10,0))

        # Chat display container
        chat_container = ttk.Frame(left_panel, style="Content.TFrame")
        chat_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=(0,10))

        self.chat_display = tk.Text(chat_container, wrap=tk.WORD, state=tk.DISABLED,
                                   bg=self.text_bg, fg=self.text_fg, relief=tk.SOLID,
                                   font=("Segoe UI", 13), insertbackground=self.text_fg,
                                   padx=15, pady=15, borderwidth=1, selectbackground="#404040")
        
        scroll_frame = ttk.Frame(chat_container, style="Content.TFrame")
        scroll_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5,0))
        
        self.scroll_position_label = ttk.Label(scroll_frame, text="100%", style="TLabel", font=("Segoe UI", 8))
        self.scroll_position_label.pack(pady=(0,5))
        
        self.chat_scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=self._on_scroll)
        self.chat_scrollbar.pack(fill=tk.Y, expand=True)
        
        self.chat_display.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        self.chat_display.config(yscrollcommand=self._on_text_scroll)
        self.chat_scrollbar.config(command=self.chat_display.yview)
        
        self.chat_display.bind("<MouseWheel>", self._on_mousewheel)
        self.chat_display.bind("<Button-4>", self._on_mousewheel)
        self.chat_display.bind("<Button-5>", self._on_mousewheel)
        
        self._configure_chat_tags()
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "🔧 Chat display initialized successfully!\n", "system")
        self.chat_display.config(state=tk.DISABLED)
        
        main_paned_window.add(left_panel, weight=3)

        # Right Panel
        right_panel_outer = self._create_labeled_frame(main_paned_window, text="Right Panel", padding=10)
        right_panel_outer.pack_propagate(False)

        # System prompt
        prompt_frame = self._create_labeled_frame(right_panel_outer, text="System Prompt", padding="5")
        prompt_frame.pack(fill=tk.X, pady=(0,10))
        
        self.system_prompt_text = tk.Text(prompt_frame, height=4, wrap=tk.WORD,
                                          bg=self.text_bg, fg=self.text_fg, insertbackground=self.text_fg,
                                          font=("Segoe UI", 11), relief=tk.SOLID, borderwidth=1, padx=8, pady=8)
        self.system_prompt_text.insert(tk.END, CONVERSATION_TEMPLATES["General Assistant"])
        self.system_prompt_text.pack(fill=tk.X)

        # Parameters
        params_labelframe = self._create_labeled_frame(right_panel_outer, text="Model Parameters", padding="5")
        params_labelframe.pack(fill=tk.X, pady=(0,10))

        params_container = ttk.Frame(params_labelframe, style="Content.TFrame")
        params_container.pack(fill=tk.X, padx=5, pady=5)

        param_fields = [
            ("Max Tokens:", "max_tokens_var", "512"), ("Temperature:", "temp_var", "0.7"),
            ("Top P:", "top_p_var", "0.9"), ("Top K:", "top_k_var", "0"),
            ("Presence Penalty:", "presence_penalty_var", "0.0"),
            ("Frequency Penalty:", "frequency_penalty_var", "0.1")
        ]

        for i, (label_text, var_name, default_value) in enumerate(param_fields):
            ttk.Label(params_container, text=label_text, style="TLabel").grid(row=i, column=0, sticky=tk.W, pady=2, padx=2)
            setattr(self, var_name, tk.StringVar(value=default_value))
            entry = ttk.Entry(params_container, textvariable=getattr(self, var_name), width=8, font=("Segoe UI", 9))
            entry.grid(row=i, column=1, sticky="ew", pady=2, padx=2)
        params_container.grid_columnconfigure(1, weight=1)

        # Controls
        controls_frame = self._create_labeled_frame(right_panel_outer, text="Controls", padding="5")
        controls_frame.pack(fill=tk.X, pady=(0,10))
        
        self.stream_var = tk.BooleanVar(value=True)
        self.stream_check = ttk.Checkbutton(controls_frame, text="Stream Response", variable=self.stream_var, style="Control.TCheckbutton")
        self.stream_check.pack(anchor=tk.W, pady=2)
        
        self.auto_save_var = tk.BooleanVar(value=True)
        self.auto_save_check = ttk.Checkbutton(controls_frame, text="Auto-save conversations", variable=self.auto_save_var, style="Control.TCheckbutton")
        self.auto_save_check.pack(anchor=tk.W, pady=2)
        
        # Font size control
        font_frame = ttk.Frame(controls_frame, style="Content.TFrame")
        font_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(font_frame, text="Chat Font Size:", style="TLabel").pack(side=tk.LEFT)
        self.font_size_var = tk.StringVar(value="13")
        font_size_combo = ttk.Combobox(font_frame, textvariable=self.font_size_var, values=["10", "11", "12", "13", "14", "15", "16", "18", "20"], 
                                      state="readonly", width=5, font=("Segoe UI", 9))
        font_size_combo.pack(side=tk.LEFT, padx=(5,5))
        font_size_combo.bind("<<ComboboxSelected>>", self._on_font_size_change)
        
        ttk.Button(font_frame, text="Apply", command=self._apply_font_size, width=6).pack(side=tk.LEFT, padx=(5,0))

        # Action buttons
        actions_frame = self._create_labeled_frame(right_panel_outer, text="Actions", padding="5")
        actions_frame.pack(fill=tk.X)
        
        self.copy_last_button = ttk.Button(actions_frame, text="Copy Last Response", command=self._copy_last_response)
        self.copy_last_button.pack(fill=tk.X, pady=2)

        self.regenerate_button = ttk.Button(actions_frame, text="Regenerate Response", command=self._regenerate_last_response)
        self.regenerate_button.pack(fill=tk.X, pady=2)

        self.clear_chat_button = ttk.Button(actions_frame, text="Clear Chat", command=self._clear_chat)
        self.clear_chat_button.pack(fill=tk.X, pady=2)
        
        self.new_session_button = ttk.Button(actions_frame, text="New Session", command=self._new_conversation, style="Accent.TButton")
        self.new_session_button.pack(fill=tk.X, pady=2)
        
        main_paned_window.add(right_panel_outer, weight=1)
        
        def _set_paned_window_size():
            try:
                window_width = self.winfo_width()
                if window_width > 100:
                    chat_width = int(window_width * 0.6)
                    main_paned_window.sashpos(0, chat_width)
                else:
                    main_paned_window.sashpos(0, 600)
            except:
                main_paned_window.sashpos(0, 600)
        
        self.after(100, _set_paned_window_size)

        # Bottom Input Area
        bottom_frame = ttk.Frame(main_container, style="TFrame", padding="5 5 0 0")
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        input_header = ttk.Frame(bottom_frame, style="TFrame")
        input_header.pack(fill=tk.X, pady=(0,5))
        
        ttk.Label(input_header, text="Your Message:", style="Header.TLabel").pack(side=tk.LEFT)
        self.char_count_label = ttk.Label(input_header, text="0 characters", style="TLabel")
        self.char_count_label.pack(side=tk.RIGHT)

        input_container = ttk.Frame(bottom_frame, style="TFrame")
        input_container.pack(fill=tk.BOTH, expand=True)

        self.user_input = tk.Text(input_container, height=3, wrap=tk.WORD,
                                   bg=self.text_bg, fg=self.text_fg, insertbackground=self.text_fg,
                                   font=("Segoe UI", 13), relief=tk.SOLID, borderwidth=1, padx=8, pady=8)
        self.user_input.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0,10))
        self.user_input.bind("<Return>", self._on_send_message_enter)
        self.user_input.bind("<Shift-Return>", self._on_shift_enter)
        self.user_input.bind("<KeyRelease>", self._update_char_count)
        self.user_input.focus_set()

        button_container = ttk.Frame(input_container, style="TFrame")
        button_container.pack(side=tk.RIGHT, fill=tk.Y)

        self.send_button = ttk.Button(button_container, text="Send\n(Ctrl+Enter)", command=self._on_send_message, style="Accent.TButton")
        self.send_button.pack(fill=tk.BOTH, expand=True)
        
        self.after(100, self._process_response_queue)

    def _configure_chat_tags(self):
        self.chat_display.tag_configure("user", foreground=self.user_fg, font=("Segoe UI", 13, "bold"))
        self.chat_display.tag_configure("assistant", foreground=self.assistant_fg, font=("Segoe UI", 13))
        self.chat_display.tag_configure("system", foreground=self.system_fg, font=("Segoe UI", 11, "italic"))
        self.chat_display.tag_configure("error", foreground=self.error_fg, font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_configure("thinking", foreground="#FFD54F", font=("Segoe UI", 12, "italic"))
        self.chat_display.tag_configure("timestamp", foreground="#999999", font=("Segoe UI", 10))
        self.chat_display.tag_configure("bold", font=("Segoe UI", 13, "bold"))
        
        self.chat_display.tag_configure("user_bg", background="#1A2332", font=("Segoe UI", 13, "bold"))
        self.chat_display.tag_configure("assistant_bg", background="#1A2B1A", font=("Segoe UI", 13))

    # Core functionality methods
    def _load_api_key(self):
        try:
            with open("pplx_api_key.txt", "r") as f:
                key = f.read().strip()
                if key:
                    self.api_key_var.set(key)
                    self._initialize_api_client(key)
                    self._add_message_to_display("System", "✅ API Key loaded successfully! You can start chatting now.", "system")
        except FileNotFoundError:
            loaded_env_key = API_KEY_GLOBAL if API_KEY_GLOBAL != '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' else ""
            self.api_key_var.set(loaded_env_key)
            if loaded_env_key:
                 self._initialize_api_client(loaded_env_key)
                 self._add_message_to_display("System", "✅ API Key loaded from environment! You can start chatting now.", "system")
            else:
                welcome_msg = """🚀 Welcome to Perplexity AI GUI Client - Enhanced Edition!

🎯 Features:
• Enhanced chat visibility with better colors and fonts
• Navigation controls (⬆️ Top / ⬇️ Bottom buttons)
• Adjustable font size for better readability
• Real-time streaming responses
• Multiple AI models and conversation templates

📝 To get started:
1. Set your Perplexity API Key using the 'Set' button above
2. Choose a model and conversation template
3. Start chatting in the input box below!

Need help? Check the Help menu for keyboard shortcuts and tips."""
                self._add_message_to_display("", welcome_msg, "system")

    def _set_api_key(self):
        key = self.api_key_var.get().strip()
        if not key:
            messagebox.showerror("Error", "API Key cannot be empty.")
            return
        self._initialize_api_client(key)
        self._save_api_key(key)
        self._add_message_to_display("", f"API Key set and saved successfully.", "system")

    def _initialize_api_client(self, key: str):
        try:
            self.api_client = PerplexityAPI(api_key=key)
        except ValueError as e:
            messagebox.showerror("API Client Error", str(e))
            self.api_client = None

    def _save_api_key(self, key: str):
        try:
            with open("pplx_api_key.txt", "w") as f:
                f.write(key)
        except IOError:
            messagebox.showerror("Error", "Could not save API key to file.")

    def _toggle_api_key_visibility(self):
        current_show = self.api_key_entry.cget("show")
        if current_show == "*":
            self.api_key_entry.config(show="")
            self.toggle_key_button.config(text="🙈")
        else:
            self.api_key_entry.config(show="*")
            self.toggle_key_button.config(text="👁")

    def _on_template_change(self, event=None):
        selected_template = self.template_var.get()
        if selected_template in CONVERSATION_TEMPLATES:
            self.system_prompt_text.delete("1.0", tk.END)
            self.system_prompt_text.insert("1.0", CONVERSATION_TEMPLATES[selected_template])

    def _update_char_count(self, event=None):
        content = self.user_input.get("1.0", tk.END).strip()
        char_count = len(content)
        word_count = len(content.split()) if content else 0
        self.char_count_label.config(text=f"{char_count} chars, {word_count} words")

    def _update_message_count(self):
        count = len(self.conversation_history)
        self.message_count_label.config(text=f"Messages: {count}")

    def _on_send_message_enter(self, event):
        if event.state & 0x0004:  # Ctrl key
            self._on_send_message()
            return "break"
        return None

    def _on_shift_enter(self, event):
        self.user_input.insert(tk.INSERT, "\n")
        return "break"

    def _add_message_to_display(self, who: str, message: str, tag: str, is_thinking_placeholder=False, show_timestamp=True):
        self.chat_display.config(state=tk.NORMAL)
        start_index = self.chat_display.index(tk.END)

        if self.chat_display.index('end-1c') != "1.0" and self.chat_display.get("end-2c", "end-1c") != "\n":
             self.chat_display.insert(tk.END, "\n")
        
        if show_timestamp and who:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        if who:
            speaker_color = "user" if who == "You" else "assistant"
            self.chat_display.insert(tk.END, f"{who}:\n", (speaker_color, "bold"))
        
        if message.strip():
            lines = message.split('\n')
            for i, line in enumerate(lines):
                if line.strip() or i == 0:
                    indent = "  " if who else ""
                    self.chat_display.insert(tk.END, f"{indent}{line}", tag)
                if i < len(lines) - 1:
                    self.chat_display.insert(tk.END, "\n")
        
        if is_thinking_placeholder:
            end_index = self.chat_display.index(tk.END + "-1c")
            self.thinking_message_indices = (start_index.strip(), end_index.strip())
        
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.config(state=tk.DISABLED)
        
        self.chat_display.see(tk.END)
        self._update_scroll_position()
        self._update_message_count()

    def _on_send_message(self):
        if not self.api_client:
            messagebox.showerror("Setup Required", "API Key not set or client not initialized. Please set your API Key.")
            return

        user_prompt = self.user_input.get("1.0", tk.END).strip()
        if not user_prompt:
            return

        self._add_message_to_display("You", user_prompt, "user")
        self.conversation_history.append({"role": "user", "content": user_prompt})
        self.user_input.delete("1.0", tk.END)
        self.last_ai_response_content = ""

        self.send_button.config(state=tk.DISABLED, text="Sending...")
        self._add_message_to_display("Assistant", next(self.thinking_text_cycle), "thinking", is_thinking_placeholder=True)
        self.last_message_was_thinking = True
        
        thread = threading.Thread(target=self._call_perplexity_api, args=(list(self.conversation_history),))
        thread.daemon = True
        thread.start()

    def _call_perplexity_api(self, current_messages):
        try:
            model = self.model_var.get()
            system_prompt_content = self.system_prompt_text.get("1.0", tk.END).strip()
            
            api_messages = []
            if system_prompt_content:
                api_messages.append({"role": "system", "content": system_prompt_content})
            api_messages.extend(current_messages)

            params = {
                "max_tokens": None, "temperature": None, "top_p": None, "top_k": None,
                "presence_penalty": None, "frequency_penalty": None
            }
            
            try:
                if self.max_tokens_var.get(): params["max_tokens"] = int(self.max_tokens_var.get())
                if self.temp_var.get(): params["temperature"] = float(self.temp_var.get())
                if self.top_p_var.get(): params["top_p"] = float(self.top_p_var.get())
                if self.top_k_var.get(): params["top_k"] = int(self.top_k_var.get())
                if self.presence_penalty_var.get(): params["presence_penalty"] = float(self.presence_penalty_var.get())
                if self.frequency_penalty_var.get(): params["frequency_penalty"] = float(self.frequency_penalty_var.get())
            except ValueError as ve:
                self.response_queue.put({"error": f"Invalid parameter value: {ve}. Using defaults."})
            
            stream_enabled = self.stream_var.get()

            if stream_enabled:
                first_chunk_received = True
                accumulated_response = ""
                for chunk in self.api_client.chat_completion(model=model, messages=api_messages, stream=True, **params):
                    if "error" in chunk:
                        self.response_queue.put(chunk)
                        return
                    if "done" in chunk and chunk["done"]:
                        self.response_queue.put({"stream_done": True, "full_content": accumulated_response})
                        return
                    
                    content_delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if content_delta:
                        accumulated_response += content_delta
                        self.response_queue.put({"stream_chunk": content_delta, "first_chunk": first_chunk_received})
                        if first_chunk_received: 
                            first_chunk_received = False
            else:
                response_data = self.api_client.chat_completion(model=model, messages=api_messages, stream=False, **params)
                self.response_queue.put({"non_stream_response": response_data})

        except requests.exceptions.HTTPError as e:
            self.response_queue.put({"error": f"API Error: {str(e)}"})
        except Exception as e:
            self.response_queue.put({"error": f"Unexpected error in API call: {str(e)}"})

    def _process_response_queue(self):
        try:
            while not self.response_queue.empty():
                message_data = self.response_queue.get_nowait()

                if "stream_chunk" in message_data:
                    self._append_stream_chunk_to_display(message_data["stream_chunk"], message_data["first_chunk"])
                elif "stream_done" in message_data:
                    if self.last_message_was_thinking: 
                        self._clear_thinking_message()
                    self.conversation_history.append({"role": "assistant", "content": message_data["full_content"]})
                    self.last_ai_response_content = message_data["full_content"]
                    self.send_button.config(state=tk.NORMAL, text="Send\n(Ctrl+Enter)")
                    if self.auto_save_var.get():
                        self._auto_save_conversation()
                elif "non_stream_response" in message_data:
                    if self.last_message_was_thinking: 
                        self._clear_thinking_message()
                    response = message_data["non_stream_response"]
                    if response and "choices" in response and response["choices"]:
                        assistant_message = response["choices"][0].get("message", {}).get("content")
                        self.last_ai_response_content = assistant_message
                        self._add_message_to_display("Assistant", assistant_message, "assistant")
                        self.conversation_history.append({"role": "assistant", "content": assistant_message})
                        if "usage" in response:
                            usage = response['usage']
                            usage_text = f"Tokens: Prompt {usage.get('prompt_tokens',0)}, Completion {usage.get('completion_tokens',0)}, Total {usage.get('total_tokens',0)}"
                            self._add_message_to_display("", usage_text, "system")
                    else:
                        self._add_message_to_display("System", "No content in response or unexpected structure.", "error")
                    self.send_button.config(state=tk.NORMAL, text="Send\n(Ctrl+Enter)")
                    if self.auto_save_var.get():
                        self._auto_save_conversation()
                elif "error" in message_data:
                    if self.last_message_was_thinking: 
                        self._clear_thinking_message()
                    self._add_message_to_display("System Error", message_data["error"], "error")
                    self.send_button.config(state=tk.NORMAL, text="Send\n(Ctrl+Enter)")
        except queue.Empty:
            pass
        finally:
            self.after(100, self._process_response_queue)

    def _clear_thinking_message(self):
        if hasattr(self, 'thinking_message_indices') and self.thinking_message_indices:
            self.chat_display.config(state=tk.NORMAL)
            try:
                start_idx_str = self.thinking_message_indices[0]
                line_num = int(float(start_idx_str))
                self.chat_display.delete(f"{line_num}.0", f"{line_num+1}.0")
                
                content_after_delete = self.chat_display.get("1.0", tk.END).strip()
                if content_after_delete and self.chat_display.get("end-2c", "end-1c") == "\n" and self.chat_display.get("end-3c", "end-2c") == "\n":
                    self.chat_display.delete("end-2c", "end-1c")
            except Exception as e:
                print(f"Error clearing thinking message: {e}")
            finally:
                self.chat_display.config(state=tk.DISABLED)
                self.thinking_message_indices = None
        
        self.last_message_was_thinking = False

    def _append_stream_chunk_to_display(self, chunk_text: str, first_chunk: bool):
        if first_chunk and self.last_message_was_thinking:
            self._clear_thinking_message()
            self._add_message_to_display("Assistant", "", "assistant", show_timestamp=True)

        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, chunk_text, ("assistant",))
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        self._update_scroll_position()
        self.last_ai_response_content += chunk_text

    # Navigation and UI helper methods
    def _scroll_to_top(self):
        self.chat_display.see("1.0")
        self._update_scroll_position()
    
    def _scroll_to_bottom(self):
        self.chat_display.see(tk.END)
        self._update_scroll_position()
    
    def _on_scroll(self, *args):
        self.chat_display.yview(*args)
        self._update_scroll_position()
    
    def _on_text_scroll(self, *args):
        self.chat_scrollbar.set(*args)
        self._update_scroll_position()
    
    def _on_mousewheel(self, event):
        if event.delta:
            delta = -1 * (event.delta / 120)
        elif event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = 0
        
        self.chat_display.yview_scroll(int(delta), "units")
        self._update_scroll_position()
    
    def _update_scroll_position(self):
        try:
            top, bottom = self.chat_display.yview()
            if bottom >= 0.99:
                position_text = "Bottom"
            elif top <= 0.01:
                position_text = "Top"
            else:
                position_percent = int((top + (bottom - top) / 2) * 100)
                position_text = f"{position_percent}%"
            
            self.scroll_position_label.config(text=position_text)
        except:
            self.scroll_position_label.config(text="--")

    def _on_font_size_change(self, event):
        new_size = self.font_size_var.get()
        self.chat_display.config(font=("Segoe UI", int(new_size)))
        self._add_message_to_display("System", f"Chat font size set to {new_size}.", "system")

    def _apply_font_size(self):
        new_size = self.font_size_var.get()
        self.chat_display.config(font=("Segoe UI", int(new_size)))
        self._add_message_to_display("System", f"Chat font size set to {new_size}.", "system")

    # Utility methods (simplified versions)
    def _new_conversation(self):
        if self.conversation_history and messagebox.askyesno("New Conversation", "Start a new conversation? Current conversation will be saved."):
            if self.auto_save_var.get():
                self._auto_save_conversation()
            self._clear_chat()
            self.current_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.session_label.config(text=f"Session: {self.current_session_id}")

    def _regenerate_last_response(self):
        if not self.conversation_history:
            messagebox.showwarning("No Messages", "No conversation history to regenerate from.")
            return
        
        if self.conversation_history and self.conversation_history[-1]["role"] == "assistant":
            self.conversation_history.pop()
        
        if self.conversation_history and self.conversation_history[-1]["role"] == "user":
            last_user_message = self.conversation_history.pop()
            self.user_input.delete("1.0", tk.END)
            self.user_input.insert("1.0", last_user_message["content"])
            self._on_send_message()

    def _clear_chat(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear the chat display and current conversation history?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.conversation_history = []
            self.last_ai_response_content = ""
            self._update_message_count()
            self._add_message_to_display("", "Chat cleared.", "system")

    def _copy_last_response(self):
        if self.last_ai_response_content:
            self.clipboard_clear()
            self.clipboard_append(self.last_ai_response_content)
            messagebox.showinfo("Copied", "Last AI response copied to clipboard.")
        else:
            messagebox.showwarning("Nothing to Copy", "No AI response available to copy.")

    def _find_in_chat(self):
        search_term = simpledialog.askstring("Find in Chat", "Enter search term:")
        if search_term:
            content = self.chat_display.get("1.0", tk.END)
            if search_term.lower() in content.lower():
                messagebox.showinfo("Found", f"Found '{search_term}' in chat.")
            else:
                messagebox.showinfo("Not Found", f"'{search_term}' not found in chat.")

    # File operations (simplified)
    def _save_chat_history(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Chat As"
        )
        if not filepath:
            return

        try:
            chat_data = {
                "conversation_history": self.conversation_history,
                "system_prompt": self.system_prompt_text.get("1.0", tk.END).strip(),
                "model": self.model_var.get(),
                "template": self.template_var.get(),
                "session_id": self.current_session_id,
                "saved_at": datetime.now().isoformat()
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(chat_data, f, indent=2)
            self._add_message_to_display("", f"Chat saved to {os.path.basename(filepath)}", "system")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save chat: {e}")

    def _load_chat_history(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Chat From"
        )
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                chat_data = json.load(f)
            
            self.conversation_history = chat_data.get("conversation_history", [])
            system_prompt = chat_data.get("system_prompt", "You are a helpful AI assistant.")
            model_name = chat_data.get("model")
            template_name = chat_data.get("template", "General Assistant")
            session_id = chat_data.get("session_id", "loaded_session")

            self.system_prompt_text.delete("1.0", tk.END)
            self.system_prompt_text.insert("1.0", system_prompt)
            
            if model_name and model_name in AVAILABLE_MODELS:
                self.model_var.set(model_name)
            
            if template_name in CONVERSATION_TEMPLATES:
                self.template_var.set(template_name)
            
            self.current_session_id = session_id
            self.session_label.config(text=f"Session: {session_id}")
            
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            for message in self.conversation_history:
                role = message.get("role")
                content = message.get("content")
                if role == "user":
                    self._add_message_to_display("You", content, "user", show_timestamp=False)
                elif role == "assistant":
                    self._add_message_to_display("Assistant", content, "assistant", show_timestamp=False)
                    self.last_ai_response_content = content
            self.chat_display.config(state=tk.DISABLED)
            self._add_message_to_display("", f"Chat loaded from {os.path.basename(filepath)}", "system")

        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load chat: {e}")

    def _export_as_text(self):
        if not self.conversation_history:
            messagebox.showwarning("No Data", "No conversation to export.")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Chat as Text"
        )
        if not filepath:
            return

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Perplexity AI Conversation Export\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Model: {self.model_var.get()}\n")
                f.write("=" * 50 + "\n\n")
                
                for message in self.conversation_history:
                    role = message.get("role", "").title()
                    content = message.get("content", "")
                    f.write(f"{role}: {content}\n\n")
            
            messagebox.showinfo("Export Complete", f"Chat exported to {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export chat: {e}")

    def _export_as_html(self):
        if not self.conversation_history:
            messagebox.showwarning("No Data", "No conversation to export.")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            title="Export Chat as HTML"
        )
        if not filepath:
            return

        try:
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Perplexity AI Conversation</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ border-bottom: 2px solid #007ACC; padding-bottom: 10px; margin-bottom: 20px; }}
        .message {{ margin: 15px 0; padding: 10px; border-radius: 5px; }}
        .user {{ background: #E3F2FD; border-left: 4px solid #2196F3; }}
        .assistant {{ background: #F3E5F5; border-left: 4px solid #9C27B0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Perplexity AI Conversation</h1>
            <p>Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Model: {self.model_var.get()}</p>
        </div>"""
            
            for message in self.conversation_history:
                role = message.get("role", "")
                content = message.get("content", "").replace('\n', '<br>')
                css_class = "user" if role == "user" else "assistant"
                role_display = "You" if role == "user" else "Assistant"
                
                html_content += f"""
        <div class="message {css_class}">
            <strong>{role_display}:</strong><br>
            {content}
        </div>"""
            
            html_content += """
    </div>
</body>
</html>"""
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            messagebox.showinfo("Export Complete", f"Chat exported to {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export chat: {e}")

    # Settings and info dialogs
    def _show_settings(self):
        settings_window = tk.Toplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg="#2B2B2B")
        settings_window.transient(self)
        settings_window.grab_set()
        
        ttk.Label(settings_window, text="Application Settings", style="Header.TLabel").pack(pady=10)
        
        auto_save_frame = ttk.Frame(settings_window, style="TFrame")
        auto_save_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Checkbutton(auto_save_frame, text="Auto-save conversations", variable=self.auto_save_var, style="Control.TCheckbutton").pack(anchor=tk.W)
        
        theme_frame = ttk.Frame(settings_window, style="Content.TFrame")
        theme_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(theme_frame, text="Appearance", style="Header.TLabel").pack(anchor="w", pady=(0,5))
        ttk.Label(theme_frame, text="Theme: Dark (Default)", style="TLabel").pack(pady=5)
        
        ttk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=20)

    def _show_about(self):
        about_text = """Perplexity AI GUI Client - Enhanced Edition

Version: 2.0
Author: Enhanced by AI Assistant

Features:
• Multiple conversation templates
• Enhanced UI with dark theme
• Export to text and HTML
• Conversation search
• Auto-save functionality
• API usage statistics
• Keyboard shortcuts
• Word count analysis

Built with Python and Tkinter"""
        messagebox.showinfo("About", about_text)

    def _show_shortcuts(self):
        shortcuts_text = """Keyboard Shortcuts:

Ctrl+N - New Conversation
Ctrl+S - Save Chat
Ctrl+O - Load Chat
Ctrl+E - Export as Text
Ctrl+L - Clear Chat
Ctrl+F - Find in Chat
Ctrl+C - Copy Last Response
Ctrl+Enter - Send Message
Shift+Enter - New Line in Input

Mouse:
• Right-click in chat for context menu
• Scroll to navigate chat history"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)

    def _show_word_count(self):
        if not self.conversation_history:
            messagebox.showinfo("Word Count", "No conversation to analyze.")
            return
        
        total_words = 0
        user_words = 0
        assistant_words = 0
        
        for message in self.conversation_history:
            content = message.get("content", "")
            words = len(content.split())
            total_words += words
            
            if message.get("role") == "user":
                user_words += words
            elif message.get("role") == "assistant":
                assistant_words += words
        
        stats = f"""Conversation Statistics:
        
Total Messages: {len(self.conversation_history)}
Total Words: {total_words:,}
Your Words: {user_words:,}
Assistant Words: {assistant_words:,}

Average Words per Message: {total_words / len(self.conversation_history):.1f}"""
        messagebox.showinfo("Word Count", stats)

    def _show_api_stats(self):
        if self.api_client:
            stats = f"""API Usage Statistics:
            
Requests Made: {self.api_client.request_count}
Last Request: {self.api_client.last_request_time.strftime('%Y-%m-%d %H:%M:%S') if self.api_client.last_request_time else 'None'}
Current Model: {self.model_var.get()}
Stream Mode: {'Enabled' if self.stream_var.get() else 'Disabled'}"""
        else:
            stats = "API client not initialized. Please set your API key."
        
        messagebox.showinfo("API Statistics", stats)

    def _validate_api_key(self):
        if not self.api_client:
            messagebox.showerror("No API Key", "Please set your API key first.")
            return
        
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            response = self.api_client.chat_completion(
                model=self.model_var.get(),
                messages=test_messages,
                max_tokens=1,
                stream=False
            )
            if response:
                messagebox.showinfo("API Key Valid", "API key is valid and working!")
            else:
                messagebox.showerror("API Key Invalid", "API key validation failed.")
        except Exception as e:
            messagebox.showerror("API Key Invalid", f"API key validation failed: {str(e)}")

    # Auto-save and settings
    def _auto_save_conversation(self):
        if not self.conversation_history or not self.auto_save_var.get():
            return
        
        try:
            auto_save_dir = "auto_saves"
            if not os.path.exists(auto_save_dir):
                os.makedirs(auto_save_dir)
            
            filename = f"auto_save_{self.current_session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(auto_save_dir, filename)
            
            chat_data = {
                "conversation_history": self.conversation_history,
                "system_prompt": self.system_prompt_text.get("1.0", tk.END).strip(),
                "model": self.model_var.get(),
                "template": self.template_var.get(),
                "session_id": self.current_session_id,
                "auto_saved_at": datetime.now().isoformat()
            }
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(chat_data, f, indent=2)
                
        except Exception as e:
            print(f"Auto-save failed: {e}")

    def _schedule_auto_save(self):
        if self.auto_save_var.get() and self.conversation_history:
            self._auto_save_conversation()
        self.after(300000, self._schedule_auto_save)  # 5 minutes

    def _load_settings(self):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.auto_save_var.set(settings.get("auto_save", True))
        except FileNotFoundError:
            pass

    def _save_settings(self):
        try:
            settings = {"auto_save": self.auto_save_var.get()}
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def on_closing(self):
        if self.auto_save_var.get() and self.conversation_history:
            self._auto_save_conversation()
        self._save_settings()
        self.destroy()

if __name__ == "__main__":
    print("***********************************************************************************")
    print("INFO: Starting Perplexity AI GUI Client - Enhanced Edition v2.0")
    print("WARNING: For production or sensitive environments, ensure your API")
    print("keys are managed securely.")
    print("***********************************************************************************\n")
    
    key_file_exists = os.path.exists("pplx_api_key.txt")
    env_key_set = os.getenv('PERPLEXITY_API_KEY')
    using_placeholder_global = API_KEY_GLOBAL == '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'
    
    if not key_file_exists and not env_key_set and using_placeholder_global:
        print("INFO: No 'pplx_api_key.txt' found and no PERPLEXITY_API_KEY environment variable set.")
        print("      The application will use a placeholder API key by default.")
        print("      Please use the 'Set Key' button in the GUI to provide your valid API key.")
        print("      Your key will be saved to 'pplx_api_key.txt' for future sessions.\n")

    app = PerplexityGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()