from pyrogram import Client

# Ganti dengan data Anda
api_id = 37939380  # ganti dengan api_id Anda
api_hash = "6f433e2da0f5b0ed5466566bfcc9907c"  # ganti dengan api_hash Anda
phone_number = "+6285180944898"  # nomor telepon

app = Client("my_session", api_id=api_id, api_hash=api_hash, phone_number=phone_number)

async def main():
    await app.start()
    print("Session string Anda:")
    print(await app.export_session_string())
    await app.stop()

app.run(main())