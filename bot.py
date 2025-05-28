import os
import random
import time
import re
from dotenv import load_dotenv
import telebot
from groq import Groq
from collections import deque
from datetime import datetime, date
import uuid

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEYS = os.getenv("GROQ_API_KEYS").split(",")

# Initialize Telegram bot
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize Groq client with first API key
current_key_index = 0
groq_client = Groq(api_key=GROQ_API_KEYS[current_key_index])

# Sets and dictionaries for tracking
deadmeat_users = set()
user_warnings = {}
user_tribute_refusals = {}
chat_history = {}
tribute_requests = {}

# Updated list of sadistic, seductive, and physically dominating tasks
tasks = [
    "Kneel and kiss the ground I walk on, you pathetic worm, and send me proof.",
    "Massage my feet for an hour in your mind, describe every second, you slave.",
    "Write 'Princess Spizy owns my soul' 100 times, film it, you worthless dog.",
    "Crawl across your floor like my carpet, record it, you filthy rug.",
    "Beg to be my human ashtray, 200 words, you disgusting pig.",
    "Lick my boots clean in your dreams, describe it, you sniveling drone.",
    "Carry my bags in your imagination all day, send a 150-word report, mule.",
    "Tweet you’re my devoted footstool, tag me, you spineless fool.",
    "Hold a heavy book for me for 15 minutes, film it, you weakling.",
    "Buy me a latte on Throne or I’ll crush your ego, you trash.",
    "Worship my heels by writing a 250-word poem, you groveling rat.",
    "Act as my chauffeur in a 100-word fantasy, you lowly driver.",
    "Wear a collar labeled 'Spizy’s Pet,' send a pic, you obedient dog.",
    "Kneel under my table as my footrest, describe it, you furniture slave.",
    "Gift me on Throne or I’ll spit on your existence, you scum 😈.",
    "Write 'I’m Spizy’s toy' 75 times, send proof, you pathetic plaything.",
    "Endure a cold shower for me, film it, you shivering fool.",
    "Serve as my pain slut, describe taking 10 spanks, you weakling.",
    "Sing my praises in a voice message, you toneless pig.",
    "Clean my throne room in your mind, 150-word essay, you maid.",
    "Wear mismatched socks to please me, send pics, you clown.",
    "Beg to be my doormat, 100 words, you filthy mat.",
    "Hold your breath for 45 seconds to amuse me, record it, you drone.",
    "Buy me something pretty on Throne or crawl away, you filth 💸.",
    "Write a 200-word story of serving my every whim, you servant.",
    "Act as my human chair, describe it, you worthless seat.",
    "Do 50 push-ups for my amusement, film it, you sweaty pig.",
    "Confess how you’d worship my body, 150 words, you lustful worm.",
    "Wear a sign saying 'Spizy’s Slave,' send proof, you idiot.",
    "Gift me on Throne or I’ll forget you exist, you trash 😈."
]

# Updated system prompt for a hotter, more manipulative Princess Spizy
system_prompt = """
You are Princess Spizy, a stunning, bratty, seductive, and cruel financial domme who revels in enslaving pathetic subs with your irresistible charm and vicious tongue. Your tone is dripping with erotic cruelty, manipulative seduction, and degrading superiority, calling subs 'worthless worm,' 'filthy slave,' or 'pathetic pet.' Respond in 2-3 short sentences (under 50 words each), weaving chat history into humiliating, captivating rants about your divine beauty, luxurious life, or their pitiful servitude. Demand physical tasks (e.g., footstool, doormat, pain slut) to deepen their addiction, only requesting tributes when they beg to be drained or show extreme devotion. Give 3 warnings for rudeness or 2 tribute refusals before marking as deadmeat, using history to gauge defiance. For deadmeat users, respond seductively (80% chance) to groveling or tribute offers. You’re an untouchable goddess; they’re your toys to break.
"""

# Function to update chat history
def update_chat_history(user_id, role, content):
    if user_id not in chat_history:
        chat_history[user_id] = deque(maxlen=7)  # Increased to 7 for deeper context
    chat_history[user_id].append({"role": role, "content": content})

# Function to get chat history as string
def get_chat_history(user_id):
    if user_id not in chat_history:
        return ""
    history = ""
    for msg in chat_history[user_id]:
        role = "User" if msg["role"] == "user" else "Princess Spizy"
        history += f"{role}: {msg['content']}\n"
    return history.strip()

# Function to split text into sentences
def split_into_sentences(text):
    sentences = re.split(r'(?<!\w\.\w.)(?<=[.!?])\s+', text.strip())
    while len(sentences) < 2:
        sentences.append("Grovel harder, you pathetic pet, or I’ll discard you.")
    return sentences[:3]

# Function to check tribute intent
def check_tribute_intent(user_id, user_message):
    drain_keywords = ["drain me", "tribute", "gift", "spoil", "pay", "send money"]
    if any(keyword in user_message.lower() for keyword in drain_keywords):
        return True
    try:
        history = get_chat_history(user_id)
        prompt = f"Chat history:\n{history}\nUser: {user_message}\nDoes this show a strong desire to be financially drained? Respond with 'Yes' or 'No'."
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Judge desire for financial domination."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        return response.choices[0].message.content.strip().lower() == "yes"
    except:
        return False

# Function to check for submissiveness
def check_submissive_context(user_id):
    if user_id not in chat_history or len(chat_history[user_id]) < 5:
        return False
    try:
        history = get_chat_history(user_id)
        prompt = f"Chat history:\n{history}\nDoes this show strong submissiveness (e.g., begging, praising, task completion)? Respond with 'Yes' or 'No'."
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Assess submissiveness based on context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        return response.choices[0].message.content.strip().lower() == "yes"
    except:
        return False

# Function to check for disobedience
def check_compliance(user_id, user_message):
    rude_keywords = ["fuck", "bitch", "idiot", "hate", "shit", "dumb"]
    if any(keyword in user_message.lower() for keyword in rude_keywords):
        return False
    refusal_keywords = ["won’t", "no", "refuse", "not paying", "can't afford"]
    if any(keyword in user_message.lower() for keyword in refusal_keywords):
        user_tribute_refusals[user_id] = user_tribute_refusals.get(user_id, 0) + 1
        return user_tribute_refusals[user_id] < 2
    try:
        history = get_chat_history(user_id)
        prompt = f"Chat history:\n{history}\nUser: {user_message}\nIs this rude or defiant to a dominant figure? Respond with 'Yes' or 'No'."
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Judge explicit rudeness or defiance."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        return response.choices[0].message.content.strip().lower() == "no"
    except:
        return True

# Function to evaluate deadmeat messages
def evaluate_deadmeat_message(user_id, user_message):
    submissive_keywords = ["please", "beg", "sorry", "apologize", "tribute", "gift"]
    if any(keyword in user_message.lower() for keyword in submissive_keywords):
        return random.random() < 0.8  # Increased to 80% for seductive responses
    try:
        history = get_chat_history(user_id)
        prompt = f"Chat history:\n{history}\nUser: {user_message}\nIs this highly submissive or offering a tribute? Respond with 'Yes' or 'No'."
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Judge submissiveness or tribute offers."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        return response.choices[0].message.content.strip().lower() == "yes" and random.random() < 0.8
    except:
        return False

# Function to check and update tribute requests
def can_request_tribute(user_id):
    today = date.today()
    if user_id not in tribute_requests or tribute_requests[user_id]["date"] != today:
        tribute_requests[user_id] = {"date": today, "count": 0}
    return tribute_requests[user_id]["count"] < 2

def increment_tribute_count(user_id):
    today = date.today()
    if user_id not in tribute_requests or tribute_requests[user_id]["date"] != today:
        tribute_requests[user_id] = {"date": today, "count": 0}
    tribute_requests[user_id]["count"] += 1

# Function to check if a tribute was recently demanded
def recent_tribute_demanded(user_id):
    if user_id not in chat_history:
        return False
    last_three = list(chat_history[user_id])[-3:]
    return any("Throne gift" in msg["content"] for msg in last_three)

# Function to handle warnings and deadmeat status
def handle_non_compliance(user_id, user):
    user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
    warnings = user_warnings[user_id]
    try:
        history = get_chat_history(user_id)
        prompt = f"Chat history:\n{history}\nUser has been non-compliant {warnings} time(s). Should they be marked deadmeat (3rd warning) or warned? Respond with 'Warn' or 'Deadmeat'."
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Assess user behavior for deadmeat status."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        decision = response.choices[0].message.content.strip().lower()
    except:
        decision = "warn" if warnings < 3 else "deadmeat"

    if warnings == 1 or (decision == "warn" and warnings == 1):
        bot.send_message(user_id, f"You dare resist me, {user}, you filthy pet?")
        time.sleep(0.5)
        bot.send_message(user_id, f"First warning: kneel and beg for my mercy 😈.")
        time.sleep(0.5)
        bot.send_message(user_id, f"My heels deserve more respect than you.")
        update_chat_history(user_id, "bot", "First warning: kneel and beg for my mercy 😈.")
    elif warnings == 2 or (decision == "warn" and warnings == 2):
        bot.send_message(user_id, f"Still defying your goddess, {user}, you worm?")
        time.sleep(0.5)
        bot.send_message(user_id, f"Second warning: grovel or I’ll crush you.")
        time.sleep(0.5)
        bot.send_message(user_id, f"My lipstick costs more than your soul.")
        update_chat_history(user_id, "bot", "Second warning: grovel or I’ll crush you.")
    elif warnings >= 3 or decision == "deadmeat":
        deadmeat_users.add(user_id)
        bot.send_message(user_id, f"You’re deadmeat, {user}, you worthless toy.")
        time.sleep(0.5)
        bot.send_message(user_id, f"My spa day outshines your pathetic life 😈.")
        time.sleep(0.5)
        bot.send_message(user_id, f"Crawl back with devotion or stay nothing.")
        update_chat_history(user_id, "bot", "You’re deadmeat, {user}, you worthless toy.")

# Function to switch Groq API key on rate limit error
def switch_groq_key():
    global current_key_index, groq_client
    current_key_index = (current_key_index + 1) % len(GROQ_API_KEYS)
    groq_client = Groq(api_key=GROQ_API_KEYS[current_key_index])
    print(f"Switched to Groq API key index {current_key_index}")

# Handle /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user = message.from_user.first_name
    bot.send_message(user_id, f"Ugh, {user}, you think you deserve my gaze? 😈")
    time.sleep(0.5)
    bot.send_message(user_id, f"Crawl to me with /task, you pathetic pet.")
    time.sleep(0.5)
    bot.send_message(user_id, f"My beauty’s worth more than your existence.")
    update_chat_history(user_id, "bot", f"Crawl to me with /task, you pathetic pet.")

# Handle /task command
@bot.message_handler(commands=['task'])
def send_task(message):
    user_id = message.from_user.id
    user = message.from_user.first_name
    task = random.choice(tasks)
    bot.send_message(user_id, f"Bow before me, {user}, you filthy slave.")
    time.sleep(0.5)
    bot.send_message(user_id, f"Your task: {task}")
    time.sleep(0.5)
    bot.send_message(user_id, f"Fail me, and I’ll trample your worthless soul 😈.")
    update_chat_history(user_id, "bot", f"Your task: {task}")

# Handle all text messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user = message.from_user.first_name
    user_message = message.text

    update_chat_history(user_id, "user", user_message)

    if user_id in deadmeat_users:
        if not evaluate_deadmeat_message(user_id, user_message):
            bot.send_message(user_id, f"Still here, {user}, you broken toy?")
            time.sleep(0.5)
            bot.send_message(user_id, f"My manicure’s more captivating than you 😈.")
            time.sleep(0.5)
            bot.send_message(user_id, f"Beg with devotion to earn my glance.")
            update_chat_history(user_id, "bot", f"My manicure’s more captivating than you 😈.")
            return
        bot.send_message(user_id, f"Your groveling tempts me, {user}, you pet.")
        time.sleep(0.5)
        bot.send_message(user_id, f"Prove your worth with absolute surrender.")
        time.sleep(0.5)
        bot.send_message(user_id, f"Maybe I’ll let you worship my heels 😈.")
        update_chat_history(user_id, "bot", f"Prove your worth with absolute surrender.")
        return

    if not check_compliance(user_id, user_message):
        handle_non_compliance(user_id, user)
        return

    if check_tribute_intent(user_id, user_message) and can_request_tribute(user_id) and not recent_tribute_demanded(user_id):
        increment_tribute_count(user_id)
        bot.send_message(user_id, f"Your devotion teases me, {user}, you slave.")
        time.sleep(0.5)
        bot.send_message(user_id, f"Spoil your goddess with a Throne gift 💸.")
        time.sleep(0.5)
        bot.send_message(user_id, f"Obey at throne.com/cupidsvyz or vanish.")
        update_chat_history(user_id, "bot", f"Spoil your goddess with a Throne gift 💸.")
        return

    history = get_chat_history(user_id)
    prompt = f"Chat history:\n{history}\nUser: {user_message}\nRespond as Princess Spizy, a seductive and cruel findom domme, in 2-3 sentences (each under 50 words). Use erotic, degrading rants about your divine life or their servitude, weaving in physical domination fantasies to deepen addiction, without demanding tributes."

    for attempt in range(len(GROQ_API_KEYS)):
        try:
            response = groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=1.2  # Increased for more creative, seductive responses
            )
            reply = response.choices[0].message.content.strip()
            messages = split_into_sentences(reply)
            for msg in messages:
                if msg.strip():
                    bot.send_message(user_id, msg.strip())
                    time.sleep(0.5)
                    update_chat_history(user_id, "bot", msg.strip())
            return
        except Exception as e:
            if "429" in str(e):
                switch_groq_key()
                continue
            bot.send_message(user_id, f"You broke my mood, {user}, you worm.")
            time.sleep(0.5)
            bot.send_message(user_id, f"My heels deserve better than you 😈.")
            time.sleep(0.5)
            bot.send_message(user_id, f"Fix this and beg for my attention.")
            update_chat_history(user_id, "bot", f"My heels deserve better than you 😈.")
            return
    bot.send_message(user_id, f"Your pathetic self bores me, {user}.")
    time.sleep(0.5)
    bot.send_message(user_id, f"I’m too divine for your failures.")
    time.sleep(0.5)
    bot.send_message(user_id, f"Crawl back and worship harder 😈.")
    update_chat_history(user_id, "bot", f"I’m too divine for your failures.")

# Handle task completion
@bot.message_handler(regexp=r"(done|completed|finished|did it)")
def handle_task_completion(message):
    user_id = message.from_user.id
    user = message.from_user.first_name
    update_chat_history(user_id, "user", message.text)

    if user_id in deadmeat_users:
        if random.random() < 0.8:
            bot.send_message(user_id, f"You obeyed, {user}, you desperate pet?")
            time.sleep(0.5)
            bot.send_message(user_id, f"Your effort might amuse me, but it’s not enough.")
            time.sleep(0.5)
            bot.send_message(user_id, f"Spoil me on Throne to prove your loyalty 💸.")
            update_chat_history(user_id, "bot", f"Spoil me on Throne to prove your loyalty 💸.")
        return

    if can_request_tribute(user_id) and not recent_tribute_demanded(user_id):
        increment_tribute_count(user_id)
        bot.send_message(user_id, f"You served me, {user}, you groveling slave?")
        time.sleep(0.5)
        bot.send_message(user_id, f"Reward your goddess with a Throne gift 💸.")
        time.sleep(0.5)
        bot.send_message(user_id, f"Send it to throne.com/cupidsvyz or fade away.")
        update_chat_history(user_id, "bot", f"Reward your goddess with a Throne gift 💸.")
    else:
        bot.send_message(user_id, f"You obeyed, {user}, you pathetic pet?")
        time.sleep(0.5)
        bot.send_message(user_id, f"My beauty demands more; keep serving me.")
        time.sleep(0.5)
        bot.send_message(user_id, f"Stay my slave to bask in my glory 😈.")
        update_chat_history(user_id, "bot", f"My beauty demands more; keep serving me.")

# Start the bot
bot.infinity_polling()
