import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import json
import random
import re

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')


class NLPChatbot:
    """AI Chatbot with Natural Language Processing capabilities."""
    
    def __init__(self, intents_file='intents.json'):
        """Initialize the chatbot with intents from JSON file."""
        self.lemmatizer = WordNetLemmatizer()
        self.intents = self._load_intents(intents_file)
        self.conversation_history = []
        
    def _load_intents(self, intents_file):
        """Load intents from JSON file."""
        try:
            with open(intents_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            print(f"✓ Intents loaded successfully: {len(data['intents'])} intents found")
            return data
        except FileNotFoundError:
            print(f"✗ Error: {intents_file} not found!")
            return None
        except json.JSONDecodeError:
            print(f"✗ Error: Invalid JSON format in {intents_file}")
            return None
    
    def _preprocess_text(self, text):
        """Preprocess text by cleaning, tokenizing and lemmatizing."""
        # Lowercase
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # Tokenize
        tokens = word_tokenize(text)
        # Lemmatize
        lemmatized = [self.lemmatizer.lemmatize(word) for word in tokens]
        return ' '.join(lemmatized)
    
    def _calculate_similarity(self, user_text, pattern_text):
        """Calculate word overlap similarity between user input and pattern."""
        user_words = set(user_text.split())
        pattern_words = set(pattern_text.split())
        
        if not user_words or not pattern_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = user_words.intersection(pattern_words)
        union = user_words.union(pattern_words)
        
        return len(intersection) / len(union)
    
    def predict_intent(self, user_input):
        """Predict the intent of user input using pattern matching."""
        if self.intents is None:
            return None, 0.0
        
        preprocessed_input = self._preprocess_text(user_input)
        
        best_match_score = 0.0
        best_match_intent = None
        
        # Check each intent's patterns
        for intent in self.intents['intents']:
            for pattern in intent['patterns']:
                preprocessed_pattern = self._preprocess_text(pattern)
                
                # Calculate similarity
                similarity = self._calculate_similarity(preprocessed_input, preprocessed_pattern)
                
                # Update best match if this is better
                if similarity > best_match_score:
                    best_match_score = similarity
                    best_match_intent = intent['tag']
        
        return best_match_intent, best_match_score
    
    def get_response(self, intent):
        """Get a random response for the predicted intent."""
        if self.intents is None:
            return "Sorry, I'm not configured properly."
        
        for intent_data in self.intents['intents']:
            if intent_data['tag'] == intent:
                return random.choice(intent_data['responses'])
        
        return "I'm not sure how to respond to that. Can you rephrase?"
    
    def chat(self, user_input, confidence_threshold=0.2):
        """Process user input and generate chatbot response."""
        # Predict intent
        intent, confidence = self.predict_intent(user_input)
        
        # Store in conversation history
        self.conversation_history.append({
            'user': user_input,
            'intent': intent,
            'confidence': confidence
        })
        
        # Generate response based on confidence
        if confidence >= confidence_threshold:
            response = self.get_response(intent)
        else:
            response = "I'm not entirely sure about that. Could you provide more details?"
        
        return response
    
    def get_conversation_history(self):
        """Get the conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("✓ Conversation history cleared")


def start_interactive_chat():
    """Start an interactive chat session with the user."""
    print("\n" + "="*60)
    print("        AI CHATBOT WITH NATURAL LANGUAGE PROCESSING")
    print("="*60)
    print("Welcome! I'm your AI Chatbot Assistant.")
    print("Type 'exit' to quit, 'history' to see chat history.")
    print("="*60 + "\n")
    
    # Initialize chatbot
    chatbot = NLPChatbot('intents.json')
    
    if chatbot.intents is None:
        print("Cannot start chatbot without intents data!")
        return
    
    print("Chatbot is ready! Start chatting...\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            # Handle special commands
            if user_input.lower() == 'exit':
                print("\nBot: Thanks for chatting with me! Goodbye! 👋")
                break
            elif user_input.lower() == 'history':
                history = chatbot.get_conversation_history()
                if history:
                    print("\n--- Conversation History ---")
                    for i, exchange in enumerate(history, 1):
                        print(f"{i}. User: {exchange['user']}")
                        print(f"   Intent: {exchange['intent']} (Confidence: {exchange['confidence']:.2f})")
                    print("----------------------------\n")
                else:
                    print("No conversation history yet!\n")
                continue
            elif not user_input:
                print("Please say something!\n")
                continue
            
            # Get chatbot response
            response = chatbot.chat(user_input, confidence_threshold=0.2)
            print(f"Bot: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nBot: Thanks for chatting! Goodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            continue


if __name__ == "__main__":
    start_interactive_chat()
