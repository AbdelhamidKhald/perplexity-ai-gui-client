"""
Configuration file for Perplexity AI GUI Client
Enhanced Edition v2.0

Modify these settings to customize the application behavior and appearance.
"""

# API Configuration
DEFAULT_MODEL = "sonar"  # Default model to select on startup
API_TIMEOUT = 60  # Timeout for API requests in seconds
MAX_RETRIES = 3  # Maximum number of retries for failed requests

# UI Configuration
WINDOW_TITLE = "Perplexity AI GUI Client - Enhanced Edition"
WINDOW_SIZE = "1200x800"  # Default window size (width x height)
FONT_FAMILY = "Segoe UI"  # Primary font family
FONT_SIZE = 11  # Base font size

# Theme Colors (Dark Theme)
COLORS = {
    "main_bg": "#2B2B2B",
    "frame_bg": "#3C3C3C", 
    "text_area_bg": "#252526",
    "text_fg": "#CCCCCC",
    "entry_bg": "#333333",
    "button_bg": "#007ACC",
    "button_fg": "#FFFFFF",
    "button_active_bg": "#005FA3",
    "label_fg": "#BBBBBB",
    "accent_color": "#FF6B35",
    "user_fg": "#60AFFF",
    "assistant_fg": "#C586C0", 
    "system_fg": "#6A9955",
    "error_fg": "#F44747"
}

# Conversation Templates
CONVERSATION_TEMPLATES = {
    "General Assistant": "You are a helpful and concise AI assistant.",
    "Code Helper": "You are an expert programmer. Provide clear, well-commented code examples and explanations.",
    "Research Assistant": "You are a research assistant. Provide detailed, well-sourced information with citations when possible.",
    "Creative Writer": "You are a creative writing assistant. Help with storytelling, character development, and creative ideas.",
    "Technical Explainer": "You are a technical expert who explains complex concepts in simple, understandable terms.",
    "Problem Solver": "You are a problem-solving expert. Break down complex problems into manageable steps.",
    "Data Analyst": "You are a data analysis expert. Help interpret data, create visualizations, and provide insights.",
    "Marketing Expert": "You are a marketing professional. Provide strategic advice on branding, campaigns, and customer engagement.",
    "Academic Tutor": "You are an academic tutor. Explain concepts clearly and help with learning and understanding.",
    "Business Consultant": "You are a business consultant. Provide strategic advice on operations, growth, and decision-making."
}

# Default Model Parameters
DEFAULT_PARAMETERS = {
    "max_tokens": 512,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 0,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.1
}

# Auto-save Configuration
AUTO_SAVE_ENABLED = True  # Enable auto-save by default
AUTO_SAVE_INTERVAL = 300000  # Auto-save interval in milliseconds (5 minutes)
AUTO_SAVE_DIRECTORY = "auto_saves"  # Directory for auto-saved conversations

# Export Configuration
EXPORT_FORMATS = {
    "json": {"extension": ".json", "name": "JSON files"},
    "txt": {"extension": ".txt", "name": "Text files"},
    "html": {"extension": ".html", "name": "HTML files"}
}

# Keyboard Shortcuts
SHORTCUTS = {
    "new_conversation": "<Control-n>",
    "save_chat": "<Control-s>",
    "load_chat": "<Control-o>",
    "export_text": "<Control-e>",
    "clear_chat": "<Control-l>",
    "find_in_chat": "<Control-f>",
    "copy_response": "<Control-c>",
    "send_message": "<Control-Return>",
    "new_line": "<Shift-Return>"
}

# Feature Flags
FEATURES = {
    "enable_timestamps": True,
    "enable_word_count": True,
    "enable_api_stats": True,
    "enable_search": True,
    "enable_export": True,
    "enable_templates": True,
    "enable_auto_save": True,
    "enable_session_management": True,
    "enable_regenerate": True,
    "enable_api_validation": True
}

# Advanced Settings
ADVANCED = {
    "max_conversation_history": 1000,  # Maximum messages to keep in memory
    "thinking_animation_speed": 500,   # Thinking animation speed in milliseconds
    "stream_chunk_delay": 50,          # Delay between stream chunks in milliseconds
    "api_key_mask_char": "*",          # Character to use for masking API key
    "debug_mode": False,               # Enable debug logging
    "check_updates": True              # Check for application updates
}

# File Paths
PATHS = {
    "api_key_file": "pplx_api_key.txt",
    "settings_file": "settings.json",
    "auto_save_dir": "auto_saves",
    "export_dir": "exports",
    "logs_dir": "logs"
}

# Available Models (can be updated as new models are released)
AVAILABLE_MODELS = [
    "sonar-small-online", "sonar-medium-online", "sonar-pro", "sonar-deep-research",
    "sonar-reasoning-pro", "sonar-reasoning", "sonar", "sonar-small-chat", "sonar-medium-chat",
    "llama-3-sonar-small-32k-chat", "llama-3-sonar-small-32k-online",
    "llama-3-sonar-large-32k-chat", "llama-3-sonar-large-32k-online",
    "codellama-70b-instruct", "mistral-7b-instruct", "mixtral-8x7b-instruct",
    "llama-3-8b-instruct", "llama-3-70b-instruct", "r1-1776",
    "pplx-7b-online", "pplx-70b-online", "pplx-7b-chat", "pplx-70b-chat",
]

# Model Descriptions (for tooltips or help)
MODEL_DESCRIPTIONS = {
    "sonar": "Balanced model for general conversations",
    "sonar-pro": "Advanced model with enhanced capabilities",
    "sonar-deep-research": "Specialized for research and analysis",
    "sonar-reasoning-pro": "Advanced reasoning capabilities",
    "llama-3-70b-instruct": "Large language model for complex tasks",
    "codellama-70b-instruct": "Specialized for code generation and programming"
}

# Validation Rules
VALIDATION = {
    "max_tokens_range": (1, 4096),
    "temperature_range": (0.0, 2.0),
    "top_p_range": (0.0, 1.0),
    "top_k_range": (0, 100),
    "penalty_range": (-2.0, 2.0)
}

# Error Messages
ERROR_MESSAGES = {
    "api_key_empty": "API key cannot be empty. Please enter a valid Perplexity AI API key.",
    "api_key_invalid": "Invalid API key. Please check your API key and try again.",
    "model_not_available": "Selected model is not available. Please choose a different model.",
    "parameter_out_of_range": "Parameter value is out of valid range. Please check the limits.",
    "network_error": "Network error occurred. Please check your internet connection.",
    "rate_limit": "Rate limit exceeded. Please wait a moment before trying again.",
    "server_error": "Server error occurred. Please try again later."
}

# Success Messages
SUCCESS_MESSAGES = {
    "api_key_set": "API key set and saved successfully.",
    "chat_saved": "Chat saved successfully.",
    "chat_loaded": "Chat loaded successfully.",
    "chat_exported": "Chat exported successfully.",
    "settings_saved": "Settings saved successfully."
}

# Help Text
HELP_TEXT = {
    "api_key": "Enter your Perplexity AI API key. You can get one from https://www.perplexity.ai/",
    "model": "Select the AI model to use for conversations. Different models have different capabilities.",
    "template": "Choose a conversation template to set the AI's behavior and expertise.",
    "max_tokens": "Maximum number of tokens in the response (1-4096)",
    "temperature": "Controls randomness in responses (0.0-2.0). Higher = more creative",
    "top_p": "Nucleus sampling parameter (0.0-1.0). Controls diversity of responses",
    "top_k": "Top-k sampling parameter (0-100). 0 disables top-k sampling",
    "presence_penalty": "Reduces repetition (-2.0 to 2.0). Higher = less repetition",
    "frequency_penalty": "Reduces frequency of repeated phrases (-2.0 to 2.0)"
}