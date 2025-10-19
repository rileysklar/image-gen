# DALL-E 3 Image Generator

A Python CLI tool for generating images using OpenAI's DALL-E 3 API with iterative prompt refinement capabilities.

## Features

- 🎨 Generate high-quality images using DALL-E 3
- 🔄 Iterative prompt refinement - build on previous prompts
- 💾 Session persistence - remembers your last generation
- 🔒 Secure API key management via environment variables
- 📏 Support for DALL-E 3's native resolution (1792x1024)

## Prerequisites

- Python 3.7+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rileysklar/image-gen.git
cd image-gen
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run the script:
```bash
python3 image-gen.py
```

### First Run
You'll be prompted to enter an image description:
```
Enter your image prompt: a futuristic cityscape at sunset
```

### Iterating on Previous Prompts
On subsequent runs, the tool will show your previous prompt and offer to iterate:
```
--- Previous Session ---
Prompt: a futuristic cityscape at sunset
Image: https://...

Iterate on previous prompt? (y/n): y

Previous prompt: a futuristic cityscape at sunset
Enter modifications (or press Enter to reuse): with flying cars
```

The new prompt becomes: "a futuristic cityscape at sunset with flying cars"

## Project Structure

```
image-gen/
├── image-gen.py              # Main application
├── requirements.txt          # Python dependencies
├── .env                      # API keys (not tracked)
├── .gitignore               # Git ignore rules
├── image-gen-history.json   # Session history (not tracked)
└── README.md                # This file
```

## Configuration

### Image Size
The default size is `1792x1024`. To change it, modify line 45 in `image-gen.py`:

Supported DALL-E 3 sizes:
- `1024x1024` (square)
- `1024x1792` (portrait)
- `1792x1024` (landscape)

### Model
Currently uses `dall-e-3`. Can be changed to `dall-e-2` if needed (line 42).

## API Costs

DALL-E 3 pricing (as of 2024):
- Standard (1024x1024): $0.040 per image
- HD (1024x1792 or 1792x1024): $0.080 per image

Monitor your usage at [OpenAI Usage Dashboard](https://platform.openai.com/usage).

## Security

- API keys are stored in `.env` and excluded from version control
- Never commit `.env` or `image-gen-history.json` files
- Rotate API keys regularly and restrict permissions in OpenAI dashboard

## Error Handling

Common issues:

**API Key Not Found:**
```
Ensure your .env file exists and contains:
OPENAI_API_KEY=your_actual_key
```

**Rate Limit Errors:**
```
Wait a few seconds between requests or upgrade your OpenAI plan
```

**Invalid Size:**
```
Use only supported sizes: 1024x1024, 1024x1792, or 1792x1024
```

## Development

### Running Tests
```bash
# Add tests in the future
pytest tests/
```

### Code Style
This project follows PEP 8 guidelines. Format code with:
```bash
black image-gen.py
```

### Linting
```bash
pylint image-gen.py
flake8 image-gen.py
```

## Future Enhancements

- [ ] Add command-line arguments for non-interactive mode
- [ ] Support for image variations and edits
- [ ] Save generated images locally
- [ ] View history of all past generations
- [ ] Batch generation support
- [ ] Quality settings (standard vs HD)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Acknowledgments

- Built with [OpenAI's DALL-E 3 API](https://platform.openai.com/docs/guides/images)
- Uses [python-dotenv](https://github.com/theskumar/python-dotenv) for environment management

## Contact

Riley Sklar - [@rileysklar](https://github.com/rileysklar)

Project Link: [https://github.com/rileysklar/image-gen](https://github.com/rileysklar/image-gen)

