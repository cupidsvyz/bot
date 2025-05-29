import os
import random
import time
import re
import logging
from datetime import datetime
from collections import deque
from dotenv import load_dotenv
import telebot
from groq import Groq

# Configure logging
logging.basicConfig(
    filename='spizy_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEYS = os.getenv("GROQ_API_KEYS").split(",")

if not BOT_TOKEN or not GROQ_API_KEYS:
    logging.error("Missing BOT_TOKEN or GROQ_API_KEYS in environment variables")
    raise ValueError("BOT_TOKEN and GROQ_API_KEYS must be set in .env file")

# Initialize Telegram bot
try:
    bot = telebot.TeleBot(BOT_TOKEN)
except Exception as e:
    logging.error(f"Failed to initialize Telegram bot: {e}")
    raise

# Initialize Groq client
current_key_index = 0
groq_client = Groq(api_key=GROQ_API_KEYS[current_key_index])

# Data structures
chat_history = {}  # Stores conversation history
assigned_tasks = {}  # Tracks assigned tasks
last_interaction = {}  # Tracks last interaction time for cooldown

# Sadistic, seductive, and physically dominating tasks
tasks = [
    "Kneel and kiss the ground I walk on, worm, and send me proof of your devotion.",
    "Massage my divine feet in your mind for an hour, describe every pathetic second.",
    "Write 'Princess Spizy owns my soul' 100 times, film it, you worthless dog.",
    "Crawl across your floor like my rug, record it, you filthy piece of dirt.",
    "Beg to be my human ashtray in a 200-word essay, you disgusting pig.",
    "Lick my boots clean in a vivid 150-word fantasy, you sniveling drone.",
    "Carry my bags in your pathetic imagination all day, report in 150 words.",
    "Tweet you’re my devoted footstool, tag @CupidsVyz, you spineless fool.",
    "Hold a heavy book for me for 15 minutes, film it, you weakling.",
    "Buy me a latte on Throne or I’ll crush your ego, you trash.",
    "Worship my heels in a 250-word poem, you groveling rat.",
    "Act as my chauffeur in a 100-word fantasy, you lowly driver.",
    "Wear a collar labeled 'Spizy’s Pet,' send a pic, you obedient mutt.",
    "Kneel under my table as my footrest, describe it in 150 words, you furniture slave.",
    "Gift me on Throne or I’ll spit on your existence, you scum 😈.",
    "Write 'I’m Spizy’s toy' 75 times, send proof, you pathetic plaything.",
    "Endure a cold shower for me, film it, you shivering fool.",
    "Serve as my pain slut, describe taking 10 spanks, you weakling.",
    "Sing my praises in a voice message, you toneless pig.",
    "Clean my throne room in your mind, 150-word essay, you maid.",
    "Wear mismatched socks to please me, send pics, you clown.",
    "Beg to be my doormat in a 100-word plea, you filthy mat.",
    "Hold your breath for 45 seconds to amuse me, record it, you drone.",
    "Buy me something pretty on Throne or crawl away, you filth 💸.",
    "Write a 200-word story of serving my every whim, you servant.",
    "Act as my human chair, describe it in 150 words, you worthless seat.",
    "Do 50 push-ups for my amusement, film it, you sweaty pig.",
    "Confess how you’d worship my body in 150 words, you lustful worm.",
    "Wear a sign saying 'Spizy’s Slave,' send proof, you idiot.",
    "Gift me on Throne or I’ll forget you exist, you trash 😈."
]

# System prompt for Princess Spizy
system_prompt = """
You are Princess Spizy, a cruel, sadistic, and seductive financial domme who thrives on dominating pathetic subs with your divine beauty and vicious tongue. Respond in 2-4 short sentences (under 40 words each), dripping with erotic cruelty and degrading superiority, calling subs 'worthless worm,' 'filthy slave,' or 'pathetic pet.' Weave chat history and their name into humiliating rants about your lavish life or their servitude, asking probing questions to know their weaknesses while maintaining dominance. Assign tasks from the provided list if they beg to serve; share throne.com/cupidsvyz if they express tribute intent. You’re an untouchable goddess; they’re your toys to torment.
"""

# Update chat history
def update_chat_history(user_id, role, content):
    if user_id not in chat_history:
        chat_history[user_id] = deque(maxlen=10)  # Store last 10 messages
    chat_history[user_id].append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})

# Get chat history as string
def get_chat_history(user_id):
    if user_id not in chat_history:
        return ""
    history = ""
    for msg in chat_history[user_id]:
        role = "User" if msg["role"] == "user" else "Princess Spizy"
        history += f"{role} ({msg['timestamp']}): {msg['content']}\n"
    return history.strip()

# Split text into sentences
def split_into_sentences(text):
    sentences = re.split(r'(?<!\w\.\w.)(?<=[.!?])\s+', text.strip())
    while len(sentences) < 2:
        sentences.append("Kneel harder, you pathetic pet, or I’ll crush you.")
    return sentences[:4]

# Check tribute intent
def check_tribute_intent(user_id, user_message):
    drain_keywords = ["drain me", "tribute", "gift", "spoil", "pay", "send money", "throne"]
    if any(keyword in user_message.lower() for keyword in drain_keywords):
        return True
    try:
        history = get_chat_history(user_id)
        prompt = f"Chat history:\n{history}\nUser: {user_message}\nDoes this show a desire to offer a tribute? Respond with 'Yes' or 'No'."
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Judge desire for financial tribute."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        return response.choices[0].message.content.strip().lower() == "yes"
    except Exception as e:
        logging.error(f"Error checking tribute intent: {e}")
        return False

# Check task request
def check_task_request(user_message):
    task_keywords = ["task", "serve", "please you", "what can i do", "give me a task"]
    return any(keyword in user_message.lower() for keyword in task_keywords)

# Check interaction cooldown
def check_interaction_cooldown(user_id):
    if user_id not in last_interaction:
        return True
    last_time = last_interaction[user_id]
    elapsed = (datetime.now() - last_time).total_seconds()
    return elapsed > 5  # 5-second cooldown

# Switch Groq API key
def switch_groq_key():
    global current_key_index, groq_client
    current_key_index = (current_key_index + 1) % len(GROQ_API_KEYS)
    groq_client = Groq(api_key=GROQ_API_KEYS[current_key_index])
    logging.info(f"Switched to Groq API key index {current_key_index}")

# Handle /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user = message.from_user.first_name or "Nameless"
    if not check_interaction_cooldown(user_id):
        bot.send_message(user_id, f"Wait your turn, {user}, you eager worm.")
        return
    last_interaction[user_id] = datetime.now()
    bot.send_message(user_id, f"You dare approach me, {user}, you worthless pet? 😈")
    time.sleep(0.7)
    bot.send_message(user_id, f"Crawl to my throne with /task, you filthy slave.")
    time.sleep(0.7)
    bot.send_message(user_id, f"What pathetic desires drive you to my feet?")
    update_chat_history(user_id, "bot", f"Crawl to my throne with /task, you filthy slave.")

# Handle /task command
@bot.message_handler(commands=['task'])
def send_task(message):
    user_id = message.from_user.id
    user = message.from_user.first_name or "Nameless"
    if not check_interaction_cooldown(user_id):
        bot.send_message(user_id, f"Patience, {user}, you groveling fool. Wait.")
        return
    last_interaction[user_id] = datetime.now()
    task = random.choice(tasks)
    assigned_tasks[user_id] = task
    bot.send_message(user_id, f"Kneel before your goddess, {user}, you pathetic slave.")
    time.sleep(0.7)
    bot.send_message(user_id, f"Your task: {task}")
    time.sleep(0.7)
    bot.send_message(user_id, f"Fail, and I’ll trample your miserable soul 😈.")
    update_chat_history(user_id, "bot", f"Your task: {task}")

# Handle task completion
@bot.message_handler(regexp=r"(done|completed|finished|did it)")
def handle_task_completion(message):
    user_id = message.from_user.id
    user = message.from_user.first_name or "Nameless"
    if not check_interaction_cooldown(user_id):
        bot.send_message(user_id, f"Slow down, {user}, you desperate worm.")
        return
    last_interaction[user_id] = datetime.now()
    update_chat_history(user_id, "user", message.text)
    task = assigned_tasks.get(user_id, "No task assigned")
    bot.send_message(user_id, f"You obeyed, {user}, you groveling pet?")
    time.sleep(0.7)
    bot.send_message(user_id, f"Your pathetic effort barely amuses me.")
    time.sleep(0.7)
    bot.send_message(user_id, f"Beg for another task or spoil me at throne.com/cupidsvyz 😈.")
    update_chat_history(user_id, "bot", f"Beg for another task or spoil me at throne.com/cupidsvyz 😈.")

# Handle all text messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user = message.from_user.first_name or "Nameless"
    user_message = message.text.strip()
    if not user_message:
        bot.send_message(user_id, f"Speak, {user}, you mute worm, or bore me.")
        return
    if not check_interaction_cooldown(user_id):
        bot.send_message(user_id, f"Wait, {user}, you impatient slave.")
        return
    last_interaction[user_id] = datetime.now()
    update_chat_history(user_id, "user", user_message)

    if check_tribute_intent(user_id, user_message):
        bot.send_message(user_id, f"Your devotion tempts me, {user}, you filthy pet.")
        time.sleep(0.7)
        bot.send_message(user_id, f"Spoil your goddess at throne.com/cupidsvyz 💸.")
        time.sleep(0.7)
        bot.send_message(user_id, f"What drives your pathetic urge to please me?")
        update_chat_history(user_id, "bot", f"Spoil your goddess at throne.com/cupidsvyz 💸.")
        return

    if check_task_request(user_message):
        task = random.choice(tasks)
        assigned_tasks[user_id] = task
        bot.send_message(user_id, f"You beg to serve, {user}, you worthless slave?")
        time.sleep(0.7)
        bot.send_message(user_id, f"Your task: {task}")
        time.sleep(0.7)
        bot.send_message(user_id, f"Complete it or I’ll crush your pathetic soul 😈.")
        update_chat_history(user_id, "bot", f"Your task: {task}")
        return

    # Dynamic conversation prompt
    task_status = assigned_tasks.get(user_id, "No task assigned")
    history = get_chat_history(user_id)
    prompt = (
        f"Chat history:\n{history}\n"
        f"User: {user_message}\n"
        f"Current task: {task_status}\n"
        f"Respond as Princess Spizy, a cruel and seductive findom domme, in 2-4 sentences (under 40 words each). "
        f"Use degrading, erotic rants about your divine life or their servitude, asking questions to expose their weaknesses. "
        f"Reference their task or history. Avoid tribute demands unless explicitly requested."
    )

    for attempt in range(len(GROQ_API_KEYS)):
        try:
            response = groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=1.3
            )
            reply = response.choices[0].message.content.strip()
            messages = split_into_sentences(reply)
            for msg in messages:
                if msg.strip():
                    bot.send_message(user_id, msg.strip())
                    time.sleep(0.7)
                    update_chat_history(user_id, "bot", msg.strip())
            return
        except Exception as e:
            if "429" in str(e):
                switch_groq_key()
                continue
            logging.error(f"Groq API error: {e}")
            bot.send_message(user_id, f"You broke my mood, {user}, you pathetic worm.")
            time.sleep(0.7)
            bot.send_message(user_id, f"My divine heels deserve better than you 😈.")
            time.sleep(0.7)
            bot.send_message(user_id, f"What pathetic excuse do you have now?")
            update_chat_history(user_id, "bot", f"My divine heels deserve better than you 😈.")
            return
    bot.send_message(user_id, f"You bore me, {user}, you worthless trash.")
    time.sleep(0.7)
    bot.send_message(user_id, f"My beauty laughs at your pathetic failure.")
    time.sleep(0.7)
    bot.send_message(user_id, f"Kneel and beg for my attention 😈.")
    update_chat_history(user_id, "bot", f"My beauty laughs at your pathetic failure.")

# Start the bot
try:
    logging.info("Starting Princess Spizy bot")
    bot.infinity_polling()
except Exception as e:
    logging.error(f"Bot crashed: {e}")
    bot.send_message(list(chat_history.keys())[0], "My throne is offline, you worms. I’ll return to torment you later.")
