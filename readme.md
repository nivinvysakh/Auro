> [!WARNING]
>
> ### 🛑 Project Archived / Discontinued
>
> **Auro** is no longer actively maintained due to persistent upstream platform blocks, IP rate limits, and audio stream extraction restrictions.
>
> This repository is archived and remains public strictly as a code archive and architectural reference (demonstrating asynchronous audio streaming, custom Discord UI pagination, transliteration pipelines, and full-stack integration). Feel free to fork or adapt any utility modules for your own projects.
>
> This project took me around 2–3 years in planning, designing, and developing. Since Auro was in a private repository for a long time and was originally scheduled to be released publicly in September 2026, I am concluding my journey as a bot developer and will not be making more bots in the future. Moving forward, I will be focusing on Web and Cloud Development. I am proud to have shown constant dedication to this project with 270+ commits across branches. Thank you! 🙏💖

# Auro 🌙

<img align="right" src="/img/auro.svg" width=200 alt="Auro Bot Icon"/>

A minimalist, high-performance music engine for Discord.

### ✨ Features

- **Audio** — High-fidelity streaming via Lavalink.
- **Lyrics** — Real-time synced LRC lyrics with position tracking.
- **Filters** — Built-in Nightcore, 8D Rotation, and Vaporwave.
- **Control** — Precision seeking (`mm:ss`) and smooth playback.
- **Pfs** - Play a song from a user's spotify activity on discord.

<br clear="right"/>

## 🛠️ Setup

1. **Install dependencies**:
   <br><br>
   ```bash
   pip install -r requirements.txt
   ```
   <br><br>
2. **Configure environment**:
   Create a `.env` file with your Discord bot token.
   <br><br>
   ```env
   TOKEN=your_discord_bot_token_here
   client_id="Spotify client_id"
   client_secret="Spotify client_secret"
   ```
   <br><br>
3. **Lavalink Server Configuration**:
   Go to `core/auro.py` and update the lavalink server details the place where you edit the Node connection is given below:
   <br><br>
   ```python
   await pomice.NodePool.create_node(
       host='localhost',
       port=2333,
       password='yourpass',
       secure = False
   )
   ```
   <br><br>

> [!note]
> Make sure you have **Java 21 +** installed and **python 3.10+** to run the bot.
>
> **Firestore Integration (Optional)** : This module pushes the bot's live status to a Firestore database every 60 seconds to power an external bot landing page.
>
> Place your Firebase service account credentials in the root directory as `firebase_key.json`.
>
> If you do not require a web-based status display, you can ignore the `Auro/Status` folder. The bot will function perfectly as a standalone music player without it.
> &nbsp;

> [!CAUTION]
> **Spotify Support:** You must provide Spotify credentials for the bot to parse Spotify URLs. If these variables are missing, the bot will return an error when attempting to play Spotify tracks and will only support direct YouTube or SoundCloud links.
> &nbsp;

1. **Run the bot**:
   <br><br>
   `bash
python main.py or py main.py
`
   > [!important]
   > Make sure your Lavalink server is running before starting the bot.
   > &nbsp;

> [!tip]
> Make sure you see the `Lavalink is ready` message in the console before using music commands.

## 🫂 Contributing

Auro is an open-source project. Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

- ✨ **Wall of Fame:** Check out our [Contributors Registry](./contributors.md) to see the legends helping Auro grow.

<br>

1. **Fork** the repository
2. **Create** your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your Changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a pull request

## 🎶 License

Auro is licensed under the AGPL-3.0 License. See the LICENSE file for more details.

<p align="left">

![Python](https://img.shields.io/badge/python-3776AB?style=plastic&logo=python&logoColor=white)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Lavalink](https://img.shields.io/badge/lavalink-757575?style=plastic&logo=cog&logoColor=white)
![Discord.py](https://img.shields.io/badge/discord.py-5865F2?style=plastic&logo=discord&logoColor=white)
![License](https://img.shields.io/badge/license-AGPL--v3-red?style=plastic)
![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-brightgreen)

_Made with 💖 by Nivin_

</p>
