# GreenTee Demo

This repository contains a small Flask application that demonstrates how to combine OpenAI's API with Shopify's GraphQL API to create a virtual customer‑service chatbot for an online store.

## Project structure

```
GreenTeeDemo/
└── ChatBot/
    ├── requirements.txt
    └── app/
        ├── app.py
        ├── chatbot.py
        ├── shopify_graphql_api.py
        ├── utils.py
        └── index.html
```

The Flask app (`app.py`) exposes a simple chat endpoint and serves `index.html`, a very basic web interface. The chatbot logic lives in `chatbot.py` and can also be run from the command line.

## Setup

1. Install Python 3.10 or newer.
2. Install the dependencies:

```bash
cd GreenTeeDemo/ChatBot
pip install -r requirements.txt
```

3. Create a `.env` file in `GreenTeeDemo/ChatBot/app/` containing your credentials:

```
OPENAI_API_KEY=your-openai-key
SHOP_URL=your-shop.myshopify.com
SHOP_TOKEN=your-shopify-access-token
```

## Running the demo

Start the Flask server from the `app` directory:

```bash
cd GreenTeeDemo/ChatBot/app
python app.py
```

Visit [http://localhost:5001/](http://localhost:5001/) in your browser to chat with the bot. You can also run the chatbot from the terminal with `python chatbot.py`.

## Ideas for improvement

- Expand or replace the demo product catalog in `chatbot.py` with real product data.
- Add tests and better error handling around the Shopify API calls.
- Enhance the front end for a richer chat experience.

