> [!NOTE]
> Make sure you have Java 21 + installed and python 3.10+ to run the bot.



# Auro 🌙

<img align="right" src="/img/auro.svg" width=200 alt="Auro Bot Icon"/>

A minimalist, high-performance music engine for Discord.

### ✨ Features
- **Audio** — High-fidelity streaming via Lavalink.
- **Lyrics** — Real-time synced LRC lyrics with position tracking.
- **Filters** — Built-in Nightcore, 8D Rotation, and Vaporwave.
- **Control** — Precision seeking (`mm:ss`) and smooth playback.

<br clear="right"/>

## 🛠️ Setup
1. **Install dependencies**:
   ```bash
   pip install discord.py pomice syncedlyrics python-dotenv spotipy 
   ```
2. **Configure environment**:
    Create a `.env` file with your Discord bot token.
    ```env
    TOKEN=your_discord_bot_token_here
    ```
3. **Lavalink Server Configuration**:
    Go to `core/auro.py` and update the lavalink server details the place where you edit the Node connection is given below:
    ```python
    await pomice.NodePool.create_node(
        host='localhost',
        port=2333,
        password='yourpass',
        secure = False
    )
    ```
4. **Run the bot**:
    ```bash
    python main.py
    ```
    or 
    ```bash
    py main.py
    ```

> [!important]
> Make sure your Lavalink server is running before starting the bot.

> [!tip]
> Make sure you see the `Lavalink is ready` message in the console before using music commands.

## 🫂 Contributing
Auro is an open-source project. Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
<br>

1. **Fork** the repository
2. **Create** your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your Changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a pull request

## 🎶 License
Auro is licensed under the AGPL-3.0 License. See the LICENSE file for more details.

---

<p align="center">
Made with 💖 by Nivin
</p>
