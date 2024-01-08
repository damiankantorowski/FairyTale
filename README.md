
# Fairy Tale
Tells you a fairy tale.
- [Features](#features)
- [Instalation](#instalation)
 - [Usage](#usage)
## Features
This package is a ChatGPT-driven fairy tales writer. It uses OpenAI's [Assistants API](https://platform.openai.com/docs/assistants/) to create a task specific chatbot and ask it to generate multiple fairy tales on topics given by the user. The obtained text is saved in a pdf file using [fpdf2](https://github.com/py-pdf/fpdf2) library.
## Instalation
Use pip to install this package to your environment.
You can do it either from source code directory:

    cd fairy_tale
    pip install .
Or a release whl file:

	pip install fairy_tale-1.0-py3-none-any.whl
## Usage
Firstly, you'll need an [OpenAI API key](https://platform.openai.com/api-keys). For convenience you can store it in  environment variable like so:

**Windows**

	setx OPENAI_API_KEY "<your_key>"
**Linux/MacOS**

	echo "export OPENAI_API_KEY="<your_key>" >> ~/.zshrc
	source ~/.zshrc
To start the program, navigate to a directory you want a PDF file to be saved to and run the main script:

	fairy_tale -topics [TOPIC, ...] -key [YOUR_KEY]
If you don't specify topics in an argument, you will be asked to enter them at runtime.
Giving key is also optional, provided you have set OPENAI_API_KEY varible beforehand.
You can also start the script from source code directory:

	cd fairy_tale
    python fairy_tale.py -topics example
When the execution completes, a "Fairy tales.pdf" file will be created in your current directory.
