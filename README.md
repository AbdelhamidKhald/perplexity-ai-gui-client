# Perplexity AI GUI Client - Enhanced Edition v2.0

A sophisticated desktop application for interacting with Perplexity AI's language models through an intuitive graphical user interface.

## 🚀 Features

- **Enhanced Chat Interface** - Improved visibility with better colors, larger fonts, and navigation controls
- **Chat History Navigation** - Top/Bottom buttons, scroll position indicator, and smooth scrolling
- **Adjustable Font Size** - Real-time font size control (10pt to 20pt) for better readability
- **Modern Dark Theme UI** - Professional, eye-friendly interface with high contrast
- **Multiple AI Models** - Support for 23+ Perplexity AI models including Sonar, LLaMA, and specialized models
- **Conversation Templates** - Pre-configured prompts for different use cases (coding, research, creative writing, etc.)
- **Real-time Streaming** - Live response streaming for immediate feedback
- **Advanced Parameters** - Fine-tune model behavior with temperature, top-p, penalties, etc.
- **Session Management** - Multiple conversation sessions with auto-save functionality
- **Export Options** - Save conversations as JSON, TXT, or HTML
- **Search & Navigation** - Find content within conversations
- **Keyboard Shortcuts** - Efficient navigation with hotkeys
- **API Usage Tracking** - Monitor request counts and usage statistics

## 📋 Requirements

- **Python 3.7+** (Recommended: Python 3.9+)
- **Internet Connection** for API calls
- **Perplexity AI API Key** ([Get one here](https://www.perplexity.ai/))

## 🛠️ Installation & Setup

### Quick Start (Windows)

1. **Double-click `launch.bat`** - This will automatically:
   - Check Python installation
   - Install dependencies
   - Launch the application

### Manual Setup

1. **Clone or download** this repository
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set your API key:**
   - Option A: Create `pplx_api_key.txt` and paste your API key
   - Option B: Set environment variable `PERPLEXITY_API_KEY`
   - Option C: Use the "Set Key" button in the application

4. **Run the application:**
   ```bash
   python launch.py
   ```

## 🔧 Validation & Testing

### Run Tests
```bash
python test_app.py
```

### Validate Complete Setup
```bash
python validate_setup.py
```
This checks:
- All required files
- Directory structure
- API key validity
- Network connectivity

## 📖 Usage

### Basic Usage
1. **Launch** the application using `launch.bat` or `python launch.py`
2. **Set API Key** if not already configured
3. **Choose a Model** from the dropdown (default: "sonar")
4. **Select Template** for conversation context
5. **Type your message** and press Ctrl+Enter or click Send

### Advanced Features

#### Conversation Templates
- **General Assistant** - Balanced, helpful responses
- **Code Helper** - Programming assistance with examples
- **Research Assistant** - Detailed, well-sourced information
- **Creative Writer** - Storytelling and creative content
- **Technical Explainer** - Complex concepts simplified
- **Problem Solver** - Step-by-step problem breakdown

#### Model Parameters
- **Max Tokens** (1-4096) - Response length limit
- **Temperature** (0.0-2.0) - Creativity level
- **Top P** (0.0-1.0) - Response diversity
- **Top K** (0-100) - Vocabulary restriction
- **Presence/Frequency Penalty** (-2.0 to 2.0) - Repetition control

#### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New conversation |
| `Ctrl+S` | Save chat |
| `Ctrl+O` | Load chat |
| `Ctrl+E` | Export as text |
| `Ctrl+L` | Clear chat |
| `Ctrl+F` | Find in chat |
| `Ctrl+C` | Copy last response |
| `Ctrl+Enter` | Send message |
| `Shift+Enter` | New line in input |

## 📁 Project Structure

```
perplexity.ai/
├── App1.py              # Main application code
├── config.py            # Configuration settings
├── launch.py            # Python launcher with checks
├── launch.bat           # Windows batch launcher
├── test_app.py          # Test suite
├── validate_setup.py    # Setup validation script
├── requirements.txt     # Python dependencies
├── pplx_api_key.txt    # API key storage (optional)
├── settings.json       # User preferences
└── auto_saves/         # Auto-saved conversations (created automatically)
```

## 🔧 Configuration

### Environment Variables
- `PERPLEXITY_API_KEY` - Your Perplexity AI API key

### Configuration Files
- `config.py` - Application settings and defaults
- `settings.json` - User preferences (auto-saved)
- `pplx_api_key.txt` - API key storage

### Auto-Save
Conversations are automatically saved every 5 minutes to the `auto_saves/` directory. You can disable this in Settings or by unchecking "Auto-save conversations".

## 🎨 Customization

### Themes
The application uses a modern dark theme by default. Colors and fonts can be customized in `config.py`:

```python
COLORS = {
    "main_bg": "#2B2B2B",
    "text_fg": "#CCCCCC",
    "accent_color": "#FF6B35",
    # ... more colors
}
```

### Adding New Templates
Add new conversation templates in `config.py`:

```python
CONVERSATION_TEMPLATES = {
    "Your Template": "Your system prompt here...",
    # ... existing templates
}
```

## 🐛 Troubleshooting

### Common Issues

**"API key not set"**
- Ensure you have a valid Perplexity AI API key
- Check that `pplx_api_key.txt` exists or environment variable is set
- Use the "Validate API Key" option in the Tools menu

**"tkinter not found"**
- On Ubuntu/Debian: `sudo apt-get install python3-tk`
- On CentOS/RHEL: `sudo yum install tkinter`
- On macOS: Reinstall Python with tkinter support

**"requests module not found"**
- Run: `pip install -r requirements.txt`

**Application won't start**
- Run `python test_app.py` to diagnose issues
- Check Python version with `python --version`
- Ensure you're in the correct directory

### Getting Help
1. Run the test suite: `python test_app.py`
2. Run validation: `python validate_setup.py`
3. Check the console output for error messages
4. Verify your API key is valid using Tools → Validate API Key

## 📊 API Usage & Costs

- Monitor usage with Tools → API Usage Stats
- Different models have different costs
- Streaming responses don't cost extra
- Response length affects token usage

## 🔒 Security Notes

- API keys are stored locally in `pplx_api_key.txt`
- No data is sent to third parties (only Perplexity AI)
- Conversations are saved locally only
- Use environment variables for enhanced security in production

## 🚀 Performance Tips

- Use streaming for faster response perception
- Adjust max tokens to control response length
- Lower temperature for more focused responses
- Use appropriate models for your use case

## 📝 Version History

### v2.0 - Enhanced Edition
- Modern dark theme UI
- Multiple conversation templates
- Advanced parameter controls
- Auto-save functionality
- Enhanced export options
- Improved error handling
- Comprehensive testing suite

### v1.0 - Initial Release
- Basic GUI implementation
- Single model support
- Simple conversation flow

## 📄 License

This project is provided as-is for educational and personal use. Please refer to Perplexity AI's terms of service for API usage guidelines.

## 🤝 Contributing

Feel free to fork this project and submit improvements. Key areas for enhancement:
- Additional conversation templates
- Theme customization options
- Plugin system for extensions
- Multi-language support

---

**Note**: This application requires a valid Perplexity AI API key. Visit [Perplexity AI](https://www.perplexity.ai/) to obtain one.