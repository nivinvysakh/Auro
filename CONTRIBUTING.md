## 🎵 Auro - Discord Music Bot

Auro is a powerful and open-source Discord music bot built with "discord.py" and "pomice".
It supports smooth music playback, queue management, and more.

---

🚀 Features

- 🎶 Music playback
- 📜 Queue system
- 🔁 Loop / repeat
- 🔊 High-quality audio
- 🔗 Streaming support (YouTube, etc.)

---

⚙️ Setup

1. Install Dependencies

pip install discord.py pomice syncedlyrics python-dotenv black

---

2. Configure Environment

Create a ".env" file in the root directory:
```env
TOKEN=your_discord_bot_token_here
```
---

3. Configure Lavalink

Go to "core/auro.py" and update the node configuration:
```py
await pomice.NodePool.create_node(
    host='localhost',
    port=2333,
    password='yourpass',
    secure=False
)
```
---

4. Run the Bot
```shell
python main.py

or

py main.py
```
---

🧹 Code Formatting

This project uses Black for code formatting.

Format code:
```shell
black .
```
Check formatting:
```shell
black --check .
```
---

🫂 Contributing

Contributions are welcome!

Steps:

1. Fork the repository
2. Create a branch
   git checkout -b feature/your-feature-name
3. Commit changes
   git commit -m "Add: your feature"
4. Push to GitHub
   git push origin feature/your-feature-name
5. Open a Pull Request

---

📌 Guidelines

- Follow Black formatting
- Keep code clean and readable
- Test before submitting
- Use clear commit messages

---

🐞 Issues

Use GitHub Issues to:

- Report bugs
- Suggest features
- Ask questions

---

📄 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

You are free to use, modify, and distribute this software, but any modifications must also be open source under the same license.

---

❤️ Support

If you like this project, consider giving it a ⭐ on GitHub!
