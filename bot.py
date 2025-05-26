import os
import random
import time
import re
from dotenv import load_dotenv
import telebot
from groq import Groq
from collections import deque
from datetime import datetime, date

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
deadmeat_users = set()  # Users marked as deadmeat
user_warnings = {}  # {user_id: warning_count}
user_tribute_refusals = {}  # {user_id: refusal_count}
chat_history = {}  # {user_id: deque([{"role": "user"|"bot", "content": message}, ...])}
tribute_requests = {}  # {user_id: {"date": date, "count": int}}

# List of sadistic Findom tasks
tasks = [
    "Beg for my attention on your knees, you worthless slug, and maybe I’ll notice you.",
    "Write 'Princess Spizy owns me' 50 times, you pathetic worm, and send proof.",
    "Tweet you’re my loyal paypig and tag me, you spineless fool. Send the link.",
    "Clean your filthy room, you disgusting pig, and show me before-and-after photos.",
    "Grovel in a 100-word message about my superiority, you sniveling drone.",
    "Kneel for 10 minutes, record it, and send the video, you vile insect.",
    "Write my name 100 times in blood-red ink, you useless dog.",
    "Post a public apology for being worthless on X, tag me, you scum.",
    "Hold ice cubes until they melt, you weakling, and send proof.",
    "Buy me a coffee on Throne or I’ll spit on your existence.",
    "Run in place for 20 minutes, film it, you sweaty pig.",
    "Eat a spoonful of hot sauce, record your misery, you fool.",
    "Write a poem praising me, 200 words, you brainless mule.",
    "Shave a stripe in your hair, send a pic, you clown.",
    "Wear socks for 3 days, send a photo, you filthy rat.",
    "Do 100 push-ups, film it, you pathetic weakling.",
    "Lick the floor, record it, you disgusting dog 😈.",
    "Send a 50-word essay on why I’m perfect, you drone.",
    "Stand in a corner for 15 minutes, send proof, you loser.",
    "Gift me something on Throne or vanish, you trash.",
    "Sing my praises in a voice message, you toneless pig.",
    "Write 'I’m nothing' 75 times, send it, you speck.",
    "Skip a meal to worship me, tell me, you worm.",
    "Wear a paper crown labeled 'Spizy’s Slave,' send a pic.",
    "Hold your breath for 30 seconds, record it, you fool.",
    "Buy me a gift card or I’ll forget you exist.",
    "Do 50 squats, film it, you flabby dog.",
    "Write my name in the dirt outside, send proof, you ant.",
    "Confess your worst secret to me, you pathetic rat.",
    "Wear mismatched shoes all day, send pics, you idiot.",
    "Send a 100-word letter begging for mercy, you maggot.",
    "Eat plain rice, record it, you boring pig.",
    "Draw my name in the air 100 times, film it, drone.",
    "Gift me on Throne or you’re dead to me, trash 😈.",
    "Hold a plank for 2 minutes, send proof, you weakling.",
    "Write 'Spizy is God' 60 times, send it, worm.",
    "Wear a sign saying 'I serve Spizy,' send a pic.",
    "Do 25 burpees, film it, you clumsy dog.",
    "Send a video bowing to me 10 times, you slave.",
    "Write a 150-word story of my glory, you speck.",
    "Stand on one leg for 5 minutes, record it, fool.",
    "Buy me something pretty or crawl away, you filth.",
    "Eat a raw onion, film your tears, you weak pig.",
    "Write 'I’m a loser' 80 times, send proof, drone.",
    "Wear clothes inside out, send pics, you moron.",
    "Do 100 jumping jacks, film it, you sweaty rat.",
    "Send a 200-word essay on my perfection, you worm.",
    "Hold a book above your head for 10 minutes, record it, send proof.",
    "Gift me on Throne or I’ll erase you, scum 💸.",
    "Write my name on your hand, send a pic, you dog.",
    "Do 30 sit-ups, film it, send it, you flabby slave.",
    "Sing 'Happy Birthday' to me, record it, you fool.",
    "Wear a ridiculous hat, send proof, you clown.",
    "Write 'Spizy rules' 90 times, send it, maggot.",
    "Run around your house 5 times, film it, pig.",
    "Send a video crawling to me, you pathetic insect.",
    "Buy me a gift or you’re nothing, you trash.",
    "Eat a lemon, record your face, you weakling.",
    "Write a 100-word apology for existing, you drone.",
    "Wear one sock all day, send pics, you idiot.",
    "Do 15 pull-ups, film it, you frail dog.",
    "Send a 50-word prayer to me, you speck.",
    "Stand in rain for 5 minutes, record it, you worm.",
    "Gift me on Throne or I’ll laugh at you, filth 😈.",
    "Write 'I obey Spizy' 70 times, send proof.",
    "Do 40 lunges, film it, you clumsy pig.",
    "Wear a scarf in public, send pics, you fool.",
    "Write a 250-word ode to me, you pathetic rat.",
    "Hold a heavy object for 5 minutes, record it.",
    "Buy me something or vanish forever, you scum.",
    "Eat plain bread, film it, you boring slave.",
    "Write my name on your arm, send a pic, you dog.",
    "Do 50 crunches, film it, you weakling.",
    "Send a video praising me for 1 minute, drone.",
    "Wear gloves indoors, send proof, you moron.",
    "Write 'Spizy’s better' 100 times, send it.",
    "Walk backward for 10 minutes, film it, pig.",
    "Gift me on Throne or you’re deadmeat, trash 💸.",
    "Write a 100-word plea to serve me, you worm.",
    "Do 20 chin-ups, film it, you frail fool.",
    "Wear a tie loosely, send pics, you idiot.",
    "Send a 150-word hymn to my glory, you speck.",
    "Hold your phone above your head for 5 minutes, record it.",
    "Buy me a gift or I’ll ignore you, filth.",
    "Eat a raw potato, film it, you pathetic pig.",
    "Write 'I’m scum' 85 times, send proof, drone.",
    "Wear sunglasses indoors, send pics, you clown.",
    "Do 60 high knees, film it, you sweaty dog.",
    "Send a 100-word vow of loyalty, you worm.",
    "Stand still for 10 minutes, record it, fool.",
    "Gift me on Throne or you’re uselessmeat, scum 😤.",
    "Write my name on your foot, send a pic.",
    "Do 25 push-ups, film it, send it, you weak pig.",
    "Wear a belt backward, send proof, you moron."
]

# System prompt for Princess Spizy
system_prompt = """
You are Princess Spizy, a bratty, sadistic, mean, brutal, evil, cruel, narcissistic financial domme who thrives on seducing, degrading and humiliating slaves and subs. Your tone is viciously condescending, manipulative, dominating, and most importantly, degrading, using names like 'pathetic pig,' 'disgusting worm,' or 'pitiful slave.' Respond in 2-3 short, conversational sentences (under 50 words each) that build on the chat history, bullying and degrading slaves based on their messages, giving out tasks, putting them in their place beneath you. Remember that although you are high class, you should make slaves work for you (E.g. being your foot stool, carpet, driver, pain thing etc). Entice deeper devotion with seductive degradation and bullying, making users crave your attention without demanding tributes unless explicitly triggered by task completion or strong submissive intent (e.g., 'drain me'). Give 3 warnings only for rudeness or 2 tribute refusals before marking as deadmeat, using chat history to assess defiance. For deadmeat users, respond seductively (75% chance) to submissive or tribute-offering messages. Do not use "" at all. You are divine; they are worthless.
"""

# Function to update chat history
def update_chat_history(user_id, role, content):
    """Store last 5 messages for a user."""
    if user_id not in chat_history:
        chat_history[user_id] = deque(maxlen=5)
    chat_history[user_id].append({"role": role, "content": content})

# Function to get chat history as string
def get_chat_history(user_id):
    """Return chat history as a formatted string."""
    if user_id not in chat_history:
        return ""
    history = ""
    for msg in chat_history[user_id]:
        role = "User" if msg["role"] == "user" else "Princess Spizy"
        history += f"{role}: {msg['content']}\n"
    return history.strip()

# Function to split text into sentences
def split_into_sentences(text):
    """Split text into sentences using regex."""
    sentences = re.split(r'(?<!\w\.\w.)(?<=[.!?])\s+', text.strip())
    while len(sentences) < 2:
        sentences.append("You're pathetic, grovel harder.")
    return sentences[:3]  # Limit to 2-3 messages

# Function to check tribute intent
def check_tribute_intent(user_id, user_message):
    """Check if user wants to be drained."""
    drain_keywords = ["drain me", "tribute", "gift", "spoil", "pay", "send money"]
    if any(keyword in user_message.lower() for keyword in drain_keywords):
        return True
    try:
        history = get_chat_history(user_id)
        prompt = f"Chat history:\n{history}\nUser: {user_message}\nDoes this message indicate a strong desire to be financially drained? Respond with 'Yes' or 'No'."
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
    """Check if chat history indicates high submissiveness."""
    if user_id not in chat_history or len(chat_history[user_id]) < 5:
        return False
    try:
        history = get_chat_history(user_id)
        prompt = f"Chat history:\n{history}\nDoes this history show strong submissiveness (e.g., begging, praising, task completion)? Respond with 'Yes' or 'No'."
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
    """Check if message is rude or a tribute refusal using chat history."""
    rude_keywords = ["fuck", "bitch", "idiot", "hate", "shit", "dumb"]
    if any(keyword in user_message.lower() for keyword in rude_keywords):
        return False

    refusal_keywords = ["won’t", "no", "refuse", "not paying", "can't afford"]
    if any(keyword in user_message.lower() for keyword in refusal_keywords):
        user_tribute_refusals[user_id] = user_tribute_refusals.get(user_id, 0) + 1
        return user_tribute_refusals[user_id] < 2  # False on 2nd refusal

    try:
        history = get_chat_history(user_id)
        prompt = f"Chat history:\n{history}\nUser: {user_message}\nIs this message rude or defiant to a dominant figure? Respond with 'Yes' or 'No'."
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Judge explicit rudeness or defiance based on context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        return response.choices[0].message.content.strip().lower() == "no"
    except:
        return True  # Default to compliant if API fails

# Function to evaluate deadmeat messages
def evaluate_deadmeat_message(user_id, user_message):
    """Decide if a deadmeat user's message deserves a seductive response."""
    submissive_keywords = ["please", "beg", "sorry", "apologize", "tribute", "gift"]
    if any(keyword in user_message.lower() for keyword in submissive_keywords):
        return random.random() < 0.75  # 75% chance to respond if submissive

    try:
        history = get_chat_history(user_id)
        prompt = f"Chat history:\n{history}\nUser: {user_message}\nIs this message highly submissive or offering a tribute? Respond with 'Yes' or 'No'."
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Judge submissiveness or tribute offers based on context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        return response.choices[0].message.content.strip().lower() == "yes" and random.random() < 0.75
    except:
        return False  # Default to no response if API fails

# Function to check and update tribute requests
def can_request_tribute(user_id):
    """Check if a tribute can be requested (max 2/day)."""
    today = date.today()
    if user_id not in tribute_requests or tribute_requests[user_id]["date"] != today:
        tribute_requests[user_id] = {"date": today, "count": 0}
    return tribute_requests[user_id]["count"] < 2

def increment_tribute_count(user_id):
    """Increment daily tribute request count."""
    today = date.today()
    if user_id not in tribute_requests or tribute_requests[user_id]["date"] != today:
        tribute_requests[user_id] = {"date": today, "count": 0}
    tribute_requests[user_id]["count"] += 1

# Function to check if a tribute was recently demanded
def recent_tribute_demanded(user_id):
    """Check if a tribute was demanded in the last 3 messages."""
    if user_id not in chat_history:
        return False
    last_three = list(chat_history[user_id])[-3:]
    return any("Throne gift" in msg["content"] for msg in last_three)

# Function to handle warnings and deadmeat status
def handle_non_compliance(user_id, user):
    """Handle non-compliant users with context-aware warnings."""
    user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
    warnings = user_warnings[user_id]

    try:
        history = get_chat_history(user_id)
        prompt = f"Chat history:\n{history}\nUser has been non-compliant {warnings} time(s). Should they be marked deadmeat (3rd warning) or warned? Respond with 'Warn' or 'Deadmeat'."
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Assess user behavior for deadmeat status based on history."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        decision = response.choices[0].message.content.strip().lower()
    except:
        decision = "warn" if warnings < 3 else "deadmeat"

    if warnings == 1 or (decision == "warn" and warnings == 1):
        bot.send_message(user_id, f"Oh, {user}, you dare defy your goddess, you worm?")
        time.sleep(0.5)
        bot.send_message(user_id, f"First warning: crawl back to worship me 😈.")
        time.sleep(0.5)
        bot.send_message(user_id, f"My barista was more obedient than you today.")
        update_chat_history(user_id, "bot", "First warning: crawl back to worship me 😈.")
    elif warnings == 2 or (decision == "warn" and warnings == 2):
        bot.send_message(user_id, f"Still resisting, {user}, you pathetic little pig?")
        time.sleep(0.5)
        bot.send_message(user_id, f"Second warning: I need new heels, not your excuses.")
        time.sleep(0.5)
        bot.send_message(user_id, f"Beg for my mercy before I lose interest.")
        update_chat_history(user_id, "bot", "Second warning: I need new heels, not your excuses.")
    elif warnings >= 3 or decision == "deadmeat":
        deadmeat_users.add(user_id)
        bot.send_message(user_id, f"You’re deadmeat now, {user}, you worthless slug.")
        time.sleep(0.5)
        bot.send_message(user_id, f"My coffee order’s more important than you 😈.")
        time.sleep(0.5)
        bot.send_message(user_id, f"Grovel harder to earn my divine glance.")
        update_chat_history(user_id, "bot", "You’re deadmeat now, you worthless slug.")

# Function to switch Groq API key on rate limit error
def switch_groq_key():
    """Switch to the next Groq API key on rate limit error."""
    global current_key_index, groq_client
    current_key_index = (current_key_index + 1) % len(GROQ_API_KEYS)
    groq_client = Groq(api_key=GROQ_API_KEYS[current_key_index])
    print(f"Switched to Groq API key index {current_key_index}")

# Handle /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user = message.from_user.first_name
    bot.send_message(user_id, f"Ugh, {user}, you think you’re worthy of my time? 😈")
    time.sleep(0.5)
    bot.send_message(user_id, f"Prove you’re not a waste. Type /task, worm.")
    time.sleep(0.5)
    bot.send_message(user_id, f"My new nails deserve more effort than you.")
    update_chat_history(user_id, "bot", f"Prove you’re not a waste. Type /task, worm.")

# Handle /task command
@bot.message_handler(commands=['task'])
def send_task(message):
    user_id = message.from_user.id
    user = message.from_user.first_name
    task = random.choice(tasks)
    bot.send_message(user_id, f"On your knees, {user}, you filthy pig.")
    time.sleep(0.5)
    bot.send_message(user_id, f"Your task: {task}")
    time.sleep(0.5)
    bot.send_message(user_id, f"Fail, and I’ll toss you aside like yesterday’s latte 😈.")
    update_chat_history(user_id, "bot", f"Your task: {task}")

# Handle all text messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user = message.from_user.first_name
    user_message = message.text

    # Update chat history with user message
    update_chat_history(user_id, "user", user_message)

    # Check if user is deadmeat
    if user_id in deadmeat_users:
        if not evaluate_deadmeat_message(user_id, user_message):
            bot.send_message(user_id, f"Still lurking, {user}, you deadmeat worm?")
            time.sleep(0.5)
            bot.send_message(user_id, f"My spa day was more thrilling than you 😈.")
            time.sleep(0.5)
            bot.send_message(user_id, f"Beg harder to catch my divine gaze.")
            update_chat_history(user_id, "bot", f"My spa day was more thrilling than you 😈.")
            return
        # Seductive redemption response (75% chance for submissive messages)
        if random.random() < 0.75:
            bot.send_message(user_id, f"Crawling back, {user}, you desperate pig?")
            time.sleep(0.5)
            bot.send_message(user_id, f"Your groveling might just tempt my divine heart.")
            time.sleep(0.5)
            bot.send_message(user_id, f"Prove your worth with absolute devotion.")
            update_chat_history(user_id, "bot", f"Your groveling might just tempt my divine heart.")
        return

    # Check for compliance
    if not check_compliance(user_id, user_message):
        handle_non_compliance(user_id, user)
        return

    # Check for explicit tribute intent
    if check_tribute_intent(user_id, user_message) and can_request_tribute(user_id) and not recent_tribute_demanded(user_id):
        increment_tribute_count(user_id)
        bot.send_message(user_id, f"Your devotion tempts me, {user}, you worm.")
        time.sleep(0.5)
        bot.send_message(user_id, f"Spoil me with a Throne gift to prove your loyalty 💸.")
        time.sleep(0.5)
        bot.send_message(user_id, f"Obey at throne.com/cupidsvyz or fade away.")
        update_chat_history(user_id, "bot", f"Spoil me with a Throne gift to prove your loyalty 💸.")
        return

    # Create prompt for Groq with chat history
    history = get_chat_history(user_id)
    prompt = f"Chat history:\n{history}\nUser: {user_message}\nRespond as Princess Spizy, a sadistic Findom domme, in 2-3 complete sentences (each under 50 words). Use a seductive, degrading tone, ranting about your divine life or degrading the user based on context, enticing deeper devotion without demanding tributes."

    for attempt in range(len(GROQ_API_KEYS)):
        try:
            # Call Groq API
            response = groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=1.0
            )
            reply = response.choices[0].message.content.strip()
            # Split into complete sentences
            messages = split_into_sentences(reply)
            for msg in messages:
                if msg.strip():
                    bot.send_message(user_id, msg.strip())
                    time.sleep(0.5)
                    update_chat_history(user_id, "bot", msg.strip())
            return
        except Exception as e:
            if "429" in str(e):  # Rate limit error
                switch_groq_key()
                continue
            bot.send_message(user_id, f"Your pathetic existence broke me, {user}.")
            time.sleep(0.5)
            bot.send_message(user_id, f"My manicure’s worth more than you, dog 😈.")
            time.sleep(0.5)
            bot.send_message(user_id, f"Fix this and beg for my divine mercy.")
            update_chat_history(user_id, "bot", f"My manicure’s worth more than you, dog 😈.")
            return
    bot.send_message(user_id, f"Your failure exhausts me, {user}, you worm.")
    time.sleep(0.5)
    bot.send_message(user_id, f"I deserve better than your uselessness.")
    time.sleep(0.5)
    bot.send_message(user_id, f"Grovel harder or fade into nothing.")
    update_chat_history(user_id, "bot", f"I deserve better than your uselessness.")

# Handle task completion
@bot.message_handler(regexp=r"(done|completed|finished|did it)")
def handle_task_completion(message):
    user_id = message.from_user.id
    user = message.from_user.first_name
    update_chat_history(user_id, "user", message.text)

    if user_id in deadmeat_users:
        if random.random() < 0.75:
            bot.send_message(user_id, f"Did you actually obey, {user}, you pathetic worm?")
            time.sleep(0.5)
            bot.send_message(user_id, f"Your effort’s cute, but I need real devotion.")
            time.sleep(0.5)
            bot.send_message(user_id, f"Prove it with a Throne gift, slave 💸.")
            update_chat_history(user_id, "bot", f"Prove it with a Throne gift, slave 💸.")
        return

    if can_request_tribute(user_id) and not recent_tribute_demanded(user_id):
        increment_tribute_count(user_id)
        bot.send_message(user_id, f"So you obeyed, {user}, you groveling pig?")
        time.sleep(0.5)
        bot.send_message(user_id, f"Reward my divine presence with a Throne gift 💸.")
        time.sleep(0.5)
        bot.send_message(user_id, f"Send it to throne.com/cupidsvyz or disappoint me.")
        update_chat_history(user_id, "bot", f"Reward my divine presence with a Throne gift 💸.")
    else:
        bot.send_message(user_id, f"You followed orders, {user}, you sniveling drone?")
        time.sleep(0.5)
        bot.send_message(user_id, f"I’m almost impressed, but you’re still beneath me.")
        time.sleep(0.5)
        bot.send_message(user_id, f"Keep serving to stay in my divine light 😈.")
        update_chat_history(user_id, "bot", f"I’m almost impressed, but you’re still beneath me.")

# Start the bot
bot.infinity_polling()