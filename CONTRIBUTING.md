# 🎵 Auro - Discord Music Bot

A powerful and open-source Discord music bot built with [discord.py](https://github.com/Rapptz/discord.py) and [pomice](https://github.com/cloudwithax/pomice). It supports smooth music playback, queue management, and more.

---

## 🚀 Features

- 🎶 **Music Playback** - Stream music directly to Discord
- 📜 **Queue System** - Manage multiple songs in queue
- 🔁 **Loop / Repeat** - Repeat songs or entire queue
- 🔊 **High-Quality Audio** - Crystal clear sound
- 🔗 **Streaming Support** - YouTube, Spotify, and more

---

## ⚙️ Setup

### 1. Install Dependencies

```bash
pip install discord.py pomice syncedlyrics python-dotenv black
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
TOKEN=your_discord_bot_token_here
```

### 3. Configure Lavalink

Update the node configuration in `core/auro.py`:

```python
await pomice.NodePool.create_node(
    host='localhost',
    port=2333,
    password='yourpass',
    secure=False
)
```

### 4. Run the Bot

```bash
python main.py
```

---

## 🧹 Code Formatting

This project uses [Black](https://black.readthedocs.io/) for code formatting.

**Format code:**
```bash
black .
```

**Check formatting:**
```bash
black --check .
```

---

## 🫂 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Commit** your changes with clear messages:
   ```bash
   git commit -m "Add: your feature description"
   ```
4. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request** and describe your changes

### 📌 Guidelines

- Follow [Black](https://black.readthedocs.io/) formatting standards
- Keep code clean, readable, and well-documented
- Test your changes before submitting
- Write clear, descriptive commit messages
- Ensure your PR addresses an existing issue or includes a clear description

---

## 🐞 Issues & Feedback

Found a bug or have an idea? Please use [GitHub Issues](https://github.com/ilynivin/Auro/issues) to:

- Report bugs with detailed reproduction steps
- Suggest new features with use cases
- Ask questions about the project

---

## 📄 License

This project is licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](LICENSE).

You are free to use, modify, and distribute this software, but any modifications must also be open source under the same license.

---

## ❤️ Support

If you like this project, consider giving it a ⭐ on [GitHub](https://github.com/ilynivin/Auro)!

For questions or support, feel free to [open an issue](https://github.com/ilynivin/Auro/issues) or reach out to the community.