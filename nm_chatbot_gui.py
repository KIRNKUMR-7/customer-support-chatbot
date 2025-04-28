import tkinter as tk
from tkinter import scrolledtext
import re
import random
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from fuzzywuzzy import fuzz

# ---------- CONFIGURATIONS ---------- #

synonyms = {
    "mobile number": "phone_number",
    "phone number": "phone_number",
    "contact number": "phone_number",
    "number": "phone_number",
    "refund": "refund_process",
    "order": "order_details",
    "delivery address": "change_address",
    "address": "change_address",
    "phone no": "change_phone_number",
    "manage": "manage_orders"
}

smalltalk_responses = {
    "how are you": "I'm doing great! Thanks for asking. How can I assist you today? 😊",
    "thank you": "You're very welcome! Always happy to help. 🙏",
    "thanks": "My pleasure! If you need anything else, just ask! 🙌",
    "who are you": "I am your E-Shop Support Assistant 🤖, available 24/7 to assist you!",
    "what's your name": "You can call me E-Shop Bot 🤖!"
}

positive_words = ["thank", "thanks", "great", "awesome", "good", "amazing"]
negative_words = ["bad", "angry", "upset", "worst", "disappointed", "hate"]

memory = {
    "last_intent": None
}

# ---------- FUNCTIONS ---------- #

def normalize_text(text):
    for word, replacement in synonyms.items():
        text = text.replace(word, replacement)
    return text.lower()

def preprocess_text(text):
    text = normalize_text(text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\W', ' ', text)
    text = text.strip()
    return text

def detect_sentiment(text):
    text = text.lower()
    if any(word in text for word in negative_words):
        return "negative"
    elif any(word in text for word in positive_words):
        return "positive"
    else:
        return "neutral"

def predict_intent(user_text):
    preprocessed = preprocess_text(user_text)
    if preprocessed in smalltalk_responses:
        return 'smalltalk', smalltalk_responses[preprocessed]
    
    text_vector = vectorizer.transform([preprocessed])
    intent_encoded = classifier.predict(text_vector)
    predicted_intent = label_encoder.inverse_transform(intent_encoded)[0]
    
    highest_score = 0
    matched_example = None
    for example in examples:
        score = fuzz.ratio(preprocessed, preprocess_text(example))
        if score > highest_score:
            highest_score = score
            matched_example = example
    
    if highest_score > 70:
        return predicted_intent, None
    else:
        return 'unknown', None

def dynamic_suggestions(intent):
    suggestions = {
        "order_details": ["Track your order", "Change delivery address"],
        "refund_process": ["Check refund status", "Contact refund team"],
        "manage_orders": ["Cancel an order", "Edit your order"],
        "change_address": ["Track updated address order"],
        "change_phone_number": ["Verify new number"],
    }
    return suggestions.get(intent, [])

# ---------- DATA SETUP ---------- #

examples = [
    "I want your phone number",
    "Can I get your mobile number?",
    "Hi, how are you?",
    "I need help",
    "Exit chat",
    "I want a refund",
    "Where is my order?",
    "Change my delivery address",
    "Update my phone no",
    "Manage my orders",
    "bad service",
    "thank you",
    "who are you"
]

intents = [
    'ask_for_phone',
    'ask_for_phone',
    'greeting',
    'help',
    'exit',
    'refund_process',
    'order_details',
    'change_address',
    'change_phone_number',
    'manage_orders',
    'complaint',
    'thanks',
    'identity'
]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(examples)
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(intents)

classifier = MultinomialNB()
classifier.fit(X, y)

# ---------- CHATBOT LOGIC ---------- #

def chatbot_response(user_input):
    sentiment = detect_sentiment(user_input)
    intent = None
    custom_response = None
    
    intent_map = {
        "1": "order_details",
        "2": "refund_process",
        "3": "manage_orders",
        "4": "change_address",
        "5": "change_phone_number",
        "6": "help",
        "7": "exit"
    }
    
    if user_input in intent_map:
        intent = intent_map[user_input]
    else:
        intent, custom_response = predict_intent(user_input)
    
    response = ""
    suggestions = []
    
    if sentiment == "negative":
        response = "😥 I'm sorry to hear that. We will try to improve your experience!"
    elif intent == 'ask_for_phone':
        response = "📞 You can reach us at 1800-123-4567. 📞"
    elif intent == 'greeting':
        response = "👋 Hello again! How can I assist you further?"
        suggestions = list(dynamic_suggestions('greeting'))
    elif intent == 'help':
        response = "💬 Connecting you to a support agent... Please wait..."
    elif intent == 'refund_process':
        response = "💸 Your refund request is being processed. You will hear from us soon!"
        suggestions = dynamic_suggestions('refund_process')
    elif intent == 'order_details':
        response = "📦 Your order is on its way! Expected delivery: 2-3 days."
        suggestions = dynamic_suggestions('order_details')
    elif intent == 'change_address':
        response = "🏡 You can change your delivery address under 'My Profile > Address Book'."
        suggestions = dynamic_suggestions('change_address')
    elif intent == 'change_phone_number':
        response = "📱 To update your phone number, visit 'My Profile' > 'Edit Phone Number'."
        suggestions = dynamic_suggestions('change_phone_number')
    elif intent == 'manage_orders':
        response = "🛒 Go to 'My Orders' section to manage or cancel your orders."
        suggestions = dynamic_suggestions('manage_orders')
    elif intent == 'smalltalk':
        response = custom_response
    elif intent == 'thanks':
        response = "🙏 Always happy to help! Have a great day! 🌟"
    elif intent == 'identity':
        response = "🤖 I am E-Shop Bot, here to support you anytime!"
    elif intent == 'exit':
        response = "👋 Thank you for visiting! We hope to see you again soon. 🌟"
    else:
        response = "🤔 I'm not sure I understood that. Please choose from the menu:"
        suggestions = [
            "Order Details 📦",
            "Refund Process 💸",
            "Manage Orders 🛒",
            "Change Delivery Address 🏡",
            "Update Phone Number 📱",
            "Talk to Support Agent 🧑‍💻",
            "Exit Chat 🚪"
        ]
    
    memory['last_intent'] = intent
    return response, suggestions

# ---------- GUI ---------- #

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("E-Shop AI Support Assistant 🤖")
        self.root.geometry("500x600")
        
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', font=("Arial", 12))
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.user_input = tk.Entry(self.entry_frame, font=("Arial", 12))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.user_input.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)
        
        self.suggestions_frame = tk.Frame(root)
        self.suggestions_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        
        self.show_welcome_message()
    
    def show_welcome_message(self):
        welcome_text = "🤖 Welcome to E-Shop AI Support Assistant! (Powered by Kiran's Py ChatBot🚀)\n"
        welcome_text += "Please type your message or select an option below.\n"
        self.append_message(welcome_text, "bot")
        self.show_suggestions([
            "Order Details 📦",
            "Refund Process 💸",
            "Manage Orders 🛒",
            "Change Delivery Address 🏡",
            "Update Phone Number 📱",
            "Talk to Support Agent 🧑‍💻",
            "Exit Chat 🚪"
        ])
    
    def append_message(self, message, sender):
        self.chat_area.config(state='normal')
        if sender == "user":
            self.chat_area.insert(tk.END, f"You: {message}\n", "user")
        else:
            self.chat_area.insert(tk.END, f"Bot: {message}\n", "bot")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)
    
    def clear_suggestions(self):
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
    
    def show_suggestions(self, suggestions):
        self.clear_suggestions()
        for suggestion in suggestions:
            btn = tk.Button(self.suggestions_frame, text=suggestion, command=lambda s=suggestion: self.on_suggestion_click(s))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    def on_suggestion_click(self, suggestion):
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, suggestion)
        self.send_message()
    
    def send_message(self, event=None):
        user_text = self.user_input.get().strip()
        if not user_text:
            return
        self.append_message(user_text, "user")
        self.user_input.delete(0, tk.END)
        response, suggestions = chatbot_response(user_text)
        self.append_message(response, "bot")
        if suggestions:
            self.show_suggestions(suggestions)
        else:
            self.clear_suggestions()

if __name__ == "__main__":
    root = tk.Tk()
    gui = ChatbotGUI(root)
    root.mainloop()
