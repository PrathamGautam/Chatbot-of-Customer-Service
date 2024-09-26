import streamlit as st
from pymongo import MongoClient
import pandas as pd
import datetime

# MongoDB connection setup
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client['customer_service_db']
    collection = db['customer_queries']
except Exception as e:
    st.error(f"Error connecting to MongoDB: {e}")
    st.stop()

# Initialize session state variables
if 'chat_data' not in st.session_state:
    st.session_state['chat_data'] = []
if 'step' not in st.session_state:
    st.session_state['step'] = 0
if 'user_responses' not in st.session_state:
    st.session_state['user_responses'] = {}

# Function to store data in MongoDB
def store_data(ticket_data):
    try:
        # Ensure date fields are converted to strings if necessary
        if 'date_of_purchase' in ticket_data and isinstance(ticket_data['date_of_purchase'], (datetime.date, datetime.datetime)):
            ticket_data['date_of_purchase'] = str(ticket_data['date_of_purchase'])
        
        collection.insert_one(ticket_data)
        st.success("Data successfully inserted into MongoDB.")
    except Exception as e:
        st.error(f"Error inserting data into MongoDB: {e}")

# Function to display chat history
def display_chat_history():
    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.chat_data:
            st.write(f"**User:** {chat['question']}")
            st.write(f"**Response:** {chat['response']}")
        st.divider()

# Function to handle chatbot conversation
def handle_chatbot_conversation():
    questions = [
        "What is your name?",
        "What is your email?",
        "What is your age?",
        "What is your gender? (Male/Female/Other)",
        "What product did you purchase?",
        "When did you purchase the product? (YYYY-MM-DD)",
        "Describe the problem you're facing.",
        "Ticket Type (General Inquiry, Technical Support, Billing):",
        "Ticket Subject:",
        "Resolution (if any):",
        "Ticket Priority (Low, Medium, High):",
        "Ticket Channel (Email, Chat, Phone):",
        "First Response Time:",
        "Time to Resolution:",
        "Customer Satisfaction Rating (1-5):"
    ]
    
    if st.session_state.step < len(questions):
        # Ask the next question
        question = questions[st.session_state.step]
        user_response = st.text_input(f"{question}", key=f"input_{st.session_state.step}")

        # Button styled as an arrow to send responses
        if st.button("➤", key=f"send_button_{st.session_state.step}") and user_response:
            # Store user response and move to the next question
            st.session_state.user_responses[st.session_state.step] = user_response
            
            # Log the question and response for chat history
            st.session_state.chat_data.append({
                "question": question,
                "response": user_response
            })
            
            st.session_state.step += 1

    else:
        # When all questions have been answered, store the data
        if st.button("Submit All"):
            # Collect all user responses
            ticket_data = {
                "ticket_id": st.session_state.chat_data[-1]["response"],  # Get last ticket ID response if provided
                "name": st.session_state.user_responses.get(0),
                "email": st.session_state.user_responses.get(1),
                "age": st.session_state.user_responses.get(2),
                "gender": st.session_state.user_responses.get(3),
                "product_purchased": st.session_state.user_responses.get(4),
                "date_of_purchase": st.session_state.user_responses.get(5),
                "problem_description": st.session_state.user_responses.get(6),
                "ticket_type": st.session_state.user_responses.get(7),
                "ticket_subject": st.session_state.user_responses.get(8),
                "resolution": st.session_state.user_responses.get(9),
                "ticket_priority": st.session_state.user_responses.get(10),
                "ticket_channel": st.session_state.user_responses.get(11),
                "first_response_time": st.session_state.user_responses.get(12),
                "time_to_resolution": st.session_state.user_responses.get(13),
                "customer_satisfaction_rating": st.session_state.user_responses.get(14),
                "submitted_at": datetime.datetime.now()  # This is optional; if you don't want it displayed, it can be removed
            }

            store_data(ticket_data)
            st.session_state.step = 0  # Reset for the next conversation
            st.session_state.user_responses.clear()  # Clear previous responses

# Function to display data from MongoDB in table form
def display_database_entries():
    try:
        # Retrieve all data from the collection
        data = list(collection.find({}, {"_id": 0}))  # Exclude the _id field for cleaner output
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df)  # Display as a table
        else:
            st.info("No data found in the database.")
    except Exception as e:
        st.error(f"Error fetching data from MongoDB: {e}")

# Sidebar for page navigation
page = st.sidebar.selectbox("Select a page", ["Chatbot", "Database"])

if page == "Chatbot":
    st.image("2.jpeg", caption="Welcome to the Chatbot", use_column_width=True)
    st.header("Customer Service Chatbot")
    display_chat_history()
    handle_chatbot_conversation()
elif page == "Database":
    st.header("Database Entries")
    display_database_entries()
