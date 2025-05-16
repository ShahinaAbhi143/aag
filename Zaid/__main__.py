import asyncio
import importlib
import os
from pyrogram import Client, idle
from Zaid.helper import join
from Zaid import clients, app, ids

# 🔄 Auto module discovery
def find_modules():
    modules = []
    base_path = os.path.join(os.path.dirname(__file__), "modules")
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_path)
                module = rel_path.replace(os.sep, ".")[:-3]
                modules.append(module)
    return modules

async def start_bot():
    await app.start()
    print("LOG: Bot token verified, booting...")

    # 🧠 Import all modules dynamically
    all_modules = find_modules()
    for mod in all_modules:
        try:
            importlib.import_module(f"Zaid.modules.{mod}")
            print(f"✅ Successfully imported module: {mod}")
        except Exception as e:
            print(f"❌ Failed to import {mod}: {e}")

    # 🚀 Start all clients
    for cli in clients:
        try:
            await cli.start()
            me = await cli.get_me()
            await join(cli)
            print(f"🔥 Started client: {me.first_name}")
            ids.append(me.id)
        except Exception as e:
            print(f"⚠️ Client start failed: {e}")

    await idle()

if __name__ == "__main__":
    asyncio.run(start_bot())
