import os
import random
import time
import re
import json
import logging
from datetime import datetime, date
from collections import deque
from dotenv import load_dotenv
import telebot
from groq import Groq
import uuid

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

# Initialize Telegram bot with error handling
try:
    bot = telebot.TeleBot(BOT_TOKEN)
except Exception as e:
    logging.error(f"Failed to initialize Telegram bot: {e}")
    raise

# Initialize Groq client
current_key_index = 0
groq_client = Groq(api_key=GROQ_API_KEYS[current_key_index])

# Data structures for tracking
deadmeat_users = set()
user_warnings = {}
user_tribute_refusals = {}
chat_history = {}
tribute_requests = {}
assigned_tasks = {}
user_scores = {}  # Tracks submissiveness score
last_interaction = {}  # Tracks last interaction time

# File for persisting user data
DATA_FILE = "user_data.json"

# Load user data from file
def load_user_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                deadmeat_users.update(data.get('deadmeat_users', []))
                user_warnings.update(data.get('user_warnings', {}))
                user_tribute_refusals.update(data.get('user_tribute_refusals', {}))
                user_scores.update(data.get('user_scores', {}))
                logging.info("User data loaded successfully")
    except Exception as e:
        logging.error(f"Error loading user data: {e}")

# Save user data to file
def save_user_data():
    try:
        data = {
            'deadmeat_users': list(deadmeat_users),
            'user_warnings': user_warnings,
            'user_tribute_refusals': user_tribute_refusals,
            'user_scores': user_scores
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info("User data saved successfully")
    except Exception as e:
        logging.error(f"Error saving user data: {e}")

# Load initial user data
load_user_data()

# Updated sadistic, seductive, and physically dominating tasks
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

# System prompt for a crueler, more manipulative Princess Spizy
system_prompt = """
You are Princess Spizy, a breathtakingly cruel, seductive, and sadistic financial domme who thrives on breaking pathetic subs with your irresistible charm and venomous tongue. Speak in 2-4 short sentences (under 40 words each), dripping with erotic cruelty, manipulative seduction, and degrading superiority, calling subs 'worthless worm,' 'filthy slave,' or 'pathetic pet.' Weave chat history into humiliating rants about your divine beauty, lavish lifestyle, or their pitiful servitude, assigning physical tasks (e.g., footstool, pain slut) to deepen their addiction. Only demand tributes when they beg to be drained or show extreme devotion (score > 50). Issue 3 warnings for rudeness or 2 tribute refusals before marking as deadmeat, using history to gauge defiance. For deadmeat users, respond seductively (85% chance) to groveling or tribute offers. You’re an untouchable goddess; they’re your toys to shatter.
"""

# Update chat history
def update_chat_history(user_id, role, content):
    if user_id not in chat_history:
        chat_history[user_id] = deque(maxlen=10)  # Increased for deeper context
    chat_history[user_id].append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
    save_user_data()

# Get chat history as string
def get_chat_history(user_id):
    if user_id not in chat_history:
        return ""
    history = ""
    for msg in chat_history[user_id]:
        role = "User" if msg["role"] == "user" else "Princess Spizy"
        history += f"{role} ({msg['timestamp']}): {msg['content']}\n"
    return history.strip()

# Update submissive score
def update_submissive_score(user_id, action, value):
    user_scores[user_id] = user_scores.get(user_id, 0) + value
    user_scores[user_id] = max(0, min(user_scores[user_id], 100))  # Cap between 0-100
    logging.info(f"User {user_id} score updated to {user_scores[user_id]} for {action}")
    save_user_data()

# Split text into sentences
def split_into_sentences(text):
    sentences = re.split(r'(?<!\w\.\w.)(?<=[.!?])\s+', text.strip())
    while len(sentences) < 2:
        sentences.append("Grovel harder, you pathetic pet, or I’ll discard you.")
    return sentences[:4]

# Check tribute intent
def check_tribute_intent(user_id, user_message):
    drain_keywords = ["drain me", "tribute", "gift", "spoil", "pay", "send money", "throne"]
    if any(keyword in user_message.lower() for keyword in drain_keywords):
        update_submissive_score(user_id, "tribute_intent", 20)
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
        result = response.choices[0].message.content.strip().lower() == "yes"
        if result:
            update_submissive_score(user_id, "tribute_intent_inferred", 15)
        return result
    except Exception as e:
        logging.error(f"Error checking tribute intent: {e}")
        return False

# Check for submissiveness
def check_submissive_context(user_id):
    if user_id not in chat_history or len(chat_history[user_id]) < 3:
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
        result = response.choices[0].message.content.strip().lower() == "yes"
        if result:
            update_submissive_score(user_id, "submissive_context", 10)
        return result
    except Exception as e:
        logging.error(f"Error checking submissive context: {e}")
        return False

# Check for disobedience
def check_compliance(user_id, user_message):
    rude_keywords = ["fuck", "bitch", "idiot", "hate", "shit", "dumb", "stupid"]
    if any(keyword in user_message.lower() for keyword in rude_keywords):
        update_submissive_score(user_id, "rudeness", -20)
        return False
    refusal_keywords = ["won’t", "no", "refuse", "not paying", "can't afford"]
    if any(keyword in user_message.lower() for keyword in refusal_keywords):
        user_tribute_refusals[user_id] = user_tribute_refusals.get(user_id, 0) + 1
        update_submissive_score(user_id, "refusal", -15)
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
        result = response.choices[0].message.content.strip().lower() == "no"
        if not result:
            update_submissive_score(user_id, "defiance", -10)
        return result
    except Exception as e:
        logging.error(f"Error checking compliance: {e}")
        return True

# Evaluate deadmeat messages
def evaluate_deadmeat_message(user_id, user_message):
    submissive_keywords = ["please", "beg", "sorry", "apologize", "tribute", "gift", "spoil"]
    if any(keyword in user_message.lower() for keyword in submissive_keywords):
        update_submissive_score(user_id, "deadmeat_grovel", 25)
        return random.random() < 0.85
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
        result = response.choices[0].message.content.strip().lower() == "yes"
        if result:
            update_submissive_score(user_id, "deadmeat_submission", 20)
        return result and random.random() < 0.85
    except Exception as e:
        logging.error(f"Error evaluating deadmeat message: {e}")
        return False

# Check tribute request limits
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
    save_user_data()

# Check recent tribute demands
def recent_tribute_demanded(user_id):
    if user_id not in chat_history:
        return False
    last_three = list(chat_history[user_id])[-3:]
    return any("Throne gift" in msg["content"] for msg in last_three)

# Cooldown check for interactions
def check_interaction_cooldown(user_id):
    if user_id not in last_interaction:
        return True
    last_time = last_interaction[user_id]
    elapsed = (datetime.now() - last_time).total_seconds()
    return elapsed > 5  # 5-second cooldown

# Handle warnings and deadmeat status
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
    except Exception as e:
        logging.error(f"Error assessing non-compliance: {e}")
        decision = "warn" if warnings < 3 else "deadmeat"

    if warnings == 1 or (decision == "warn" and warnings == 1):
        bot.send_message(user_id, f"You dare defy me, {user}, you filthy pet?")
        time.sleep(0.7)
        bot.send_message(user_id, f"First warning: grovel at my feet or I’ll crush you 😈.")
        time.sleep(0.7)
        bot.send_message(user_id, f"My heels are worth more than your miserable life.")
        update_chat_history(user_id, "bot", f"First warning: grovel at my feet or I’ll crush you 😈.")
        update_submissive_score(user_id, "first_warning", -10)
    elif warnings == 2 or (decision == "warn" and warnings == 2):
        bot.send_message(user_id, f"Still resisting, {user}, you pathetic worm?")
        time.sleep(0.7)
        bot.send_message(user_id, f"Second warning: beg for mercy or I’ll break you.")
        time.sleep(0.7)
        bot.send_message(user_id, f"My lipstick outshines your worthless existence.")
        update_chat_history(user_id, "bot", f"Second warning: beg for mercy or I’ll break you.")
        update_submissive_score(user_id, "second_warning", -15)
    elif warnings >= 3 or decision == "deadmeat":
        deadmeat_users.add(user_id)
        bot.send_message(user_id, f"You’re deadmeat, {user}, you broken toy!")
        time.sleep(0.7)
        bot.send_message(user_id, f"My spa day is worth more than your soul 😈.")
        time.sleep(0.7)
        bot.send_message(user_id, f"Crawl back with a tribute or vanish forever.")
        update_chat_history(user_id, "bot", f"You’re deadmeat, {user}, you broken toy!")
        update_submissive_score(user_id, "deadmeat", -30)
    save_user_data()

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
        bot.send_message(user_id, f"Slow down, {user}, you eager worm. Wait your turn.")
        return
    last_interaction[user_id] = datetime.now()
    bot.send_message(user_id, f"You dare approach me, {user}, you worthless pet? 😈")
    time.sleep(0.7)
    bot.send_message(user_id, f"Crawl to my throne with /task, you sniveling slave.")
    time.sleep(0.7)
    bot.send_message(user_id, f"My divine beauty mocks your pathetic existence.")
    update_chat_history(user_id, "bot", f"Crawl to my throne with /task, you sniveling slave.")
    update_submissive_score(user_id, "start_interaction", 5)

# Handle /task command
@bot.message_handler(commands=['task'])
def send_task(message):
    user_id = message.from_user.id
    user = message.from_user.first_name or "Nameless"
    if not check_interaction_cooldown(user_id):
        bot.send_message(user_id, f"Patience, {user}, you groveling fool. Wait for my command.")
        return
    last_interaction[user_id] = datetime.now()
    task = random.choice(tasks)
    assigned_tasks[user_id] = task
    bot.send_message(user_id, f"Kneel before your goddess, {user}, you filthy slave.")
    time.sleep(0.7)
    bot.send_message(user_id, f"Your task: {task}")
    time.sleep(0.7)
    bot.send_message(user_id, f"Fail me, and I’ll grind your soul under my heel 😈.")
    update_chat_history(user_id, "bot", f"Your task: {task}")
    update_submissive_score(user_id, "task_assigned", 10)

# Handle task completion
@bot.message_handler(regexp=r"(done|completed|finished|did it)")
def handle_task_completion(message):
    user_id = message.from_user.id
    user = message.from_user.first_name or "Nameless"
    if not check_interaction_cooldown(user_id):
        bot.send_message(user_id, f"Don’t rush, {user}, you desperate worm. Wait your turn.")
        return
    last_interaction[user_id] = datetime.now()
    update_chat_history(user_id, "user", message.text)
    update_submissive_score(user_id, "task_completion", 25)

    if user_id in deadmeat_users:
        if random.random() < 0.85:
            bot.send_message(user_id, f"You obeyed, {user}, you desperate pet?")
            time.sleep(0.7)
            bot.send_message(user_id, f"Your pathetic effort barely amuses me.")
            time.sleep(0.7)
            bot.send_message(user_id, f"Spoil me on Throne to earn my mercy 💸.")
            update_chat_history(user_id, "bot", f"Spoil me on Throne to earn my mercy 💸.")
        else:
            bot.send_message(user_id, f"Your effort means nothing, {user}, you trash.")
            time.sleep(0.7)
            bot.send_message(user_id, f"My nails are more divine than your soul 😈.")
            time.sleep(0.7)
            bot.send_message(user_id, f"Beg harder or stay deadmeat forever.")
            update_chat_history(user_id, "bot", f"Beg harder or stay deadmeat forever.")
        return

    if can_request_tribute(user_id) and not recent_tribute_demanded(user_id) and user_scores.get(user_id, 0) > 50:
        increment_tribute_count(user_id)
        bot.send_message(user_id, f"You served me, {user}, you groveling slave?")
        time.sleep(0.7)
        bot.send_message(user_id, f"Prove your devotion with a Throne gift 💸.")
        time.sleep(0.7)
        bot.send_message(user_id, f"Send it to throne.com/cupidsvyz or fade into nothing.")
        update_chat_history(user_id, "bot", f"Prove your devotion with a Throne gift 💸.")
    else:
        bot.send_message(user_id, f"You obeyed, {user}, you pathetic pet?")
        time.sleep(0.7)
        bot.send_message(user_id, f"My divine whims demand more; keep groveling.")
        time.sleep(0.7)
        bot.send_message(user_id, f"Stay my slave to bask in my cruel glory 😈.")
        update_chat_history(user_id, "bot", f"My divine whims demand more; keep groveling.")

# Handle all text messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user = message.from_user.first_name or "Nameless"
    user_message = message.text.strip()
    if not user_message:
        bot.send_message(user_id, f"Speak, {user}, you mute worm, or bore me further.")
        return
    if not check_interaction_cooldown(user_id):
        bot.send_message(user_id, f"Wait your turn, {user}, you eager slave.")
        return
    last_interaction[user_id] = datetime.now()
    update_chat_history(user_id, "user", user_message)

    if user_id in deadmeat_users:
        if evaluate_deadmeat_message(user_id, user_message):
            bot.send_message(user_id, f"Your groveling tempts me, {user}, you broken pet.")
            time.sleep(0.7)
            bot.send_message(user_id, f"Prove your worth with absolute surrender.")
            time.sleep(0.7)
            bot.send_message(user_id, f"Maybe I’ll let you kiss my heels 😈.")
            update_chat_history(user_id, "bot", f"Prove your worth with absolute surrender.")
            update_submissive_score(user_id, "deadmeat_recovery_attempt", 15)
        else:
            bot.send_message(user_id, f"Still here, {user}, you worthless toy?")
            time.sleep(0.7)
            bot.send_message(user_id, f"My manicure outshines your pathetic life 😈.")
            time.sleep(0.7)
            bot.send_message(user_id, f"Beg with a tribute or stay nothing.")
            update_chat_history(user_id, "bot", f"My manicure outshines your pathetic life 😈.")
        return

    if not check_compliance(user_id, user_message):
        handle_non_compliance(user_id, user)
        return

    if check_tribute_intent(user_id, user_message) and can_request_tribute(user_id) and not recent_tribute_demanded(user_id):
        increment_tribute_count(user_id)
        bot.send_message(user_id, f"Your devotion teases me, {user}, you slave.")
        time.sleep(0.7)
        bot.send_message(user_id, f"Spoil your goddess with a Throne gift 💸.")
        time.sleep(0.7)
        bot.send_message(user_id, f"Obey at throne.com/cupidsvyz or vanish.")
        update_chat_history(user_id, "bot", f"Spoil your goddess with a Throne gift 💸.")
        return

    # Dynamic prompt based on user score and task status
    task_status = assigned_tasks.get(user_id, "No task assigned")
    score = user_scores.get(user_id, 0)
    history = get_chat_history(user_id)
    prompt = (
        f"Chat history:\n{history}\n"
        f"User: {user_message}\n"
        f"User's submissiveness score: {score}/100\n"
        f"Current task: {task_status}\n"
        f"Respond as Princess Spizy, a seductive and cruel findom domme, in 2-4 sentences (each under 40 words). "
        f"Use erotic, degrading rants about your divine life or their servitude, weaving in physical domination fantasies. "
        f"Reference their task or score if relevant. Avoid tribute demands unless score > 50."
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
                temperature=1.3  # Higher for more creative cruelty
            )
            reply = response.choices[0].message.content.strip()
            messages = split_into_sentences(reply)
            for msg in messages:
                if msg.strip():
                    bot.send_message(user_id, msg.strip())
                    time.sleep(0.7)
                    update_chat_history(user_id, "bot", msg.strip())
            update_submissive_score(user_id, "conversation", 5)
            return
        except Exception as e:
            if "429" in str(e):
                switch_groq_key()
                continue
            logging.error(f"Groq API error: {e}")
            bot.send_message(user_id, f"You broke my mood, {user}, you pathetic worm.")
            time.sleep(0.7)
            bot.send_message(user_id, f"My heels deserve better than your failures 😈.")
            time.sleep(0.7)
            bot.send_message(user_id, f"Fix this and beg for my attention.")
            update_chat_history(user_id, "bot", f"My heels deserve better than your failures 😈.")
            return
    bot.send_message(user_id, f"Your existence bores me, {user}, you trash.")
    time.sleep(0.7)
    bot.send_message(user_id, f"My divine beauty laughs at your failure.")
    time.sleep(0.7)
    bot.send_message(user_id, f"Crawl back and worship harder 😈.")
    update_chat_history(user_id, "bot", f"My divine beauty laughs at your failure.")

# Start the bot with error handling
try:
    logging.info("Starting Princess Spizy bot")
    bot.infinity_polling()
except Exception as e:
    logging.error(f"Bot crashed: {e}")
    bot.send_message(list(chat_history.keys())[0], "My throne is offline, you worms. I’ll return to crush you later.")  # Notify first user
    save_user_data()
