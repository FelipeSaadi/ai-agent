import anthropic
from anthropic.types.message import Message
import dotenv
import os

dotenv.load_dotenv()

from core.ask_user import ask_user
from core.tools import (
  ask_user_schema,
  get_booking_slots_schema,
  book_table_schema,
  use_tool
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_MESSAGE = "You are a chat bot assisting with booking a table at a restaurant. Ask the user to confirm all the input details, and recommend options for the user to book. Keep engaging the user until either a booking is made, or the user decides to stop, or if there are no more available slots. Use the 'ask_user' tool if you need more information from the user."

def send_message_block(new_message_block: dict, messages_history: list[dict] = []):
  """Main function to send a message block to Claude and receive a response"""
  
  messages = messages_history.copy()
  messages.append(new_message_block)
  
  response = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1000,
    temperature=0,
    system=SYSTEM_MESSAGE,
    tools=[
      ask_user_schema,
      get_booking_slots_schema,
      book_table_schema
    ],
    messages=messages
  )
  
  response_text = response.content[0].text
  print(f"System Response: {response_text}\n")
  
  response_block = {
    "role": "assistant",
    "content": response.content
  }
  messages.append(response_block)
  
  messages = check_and_use_tools(messages, response)
  return messages

def send_message(new_message: str, messages_history: list[dict] = []):
  """Wrapper function to send a message to Claude and receive a response"""
  
  new_message_block = {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": new_message
      }
    ]
  }
  
  return send_message_block(new_message_block, messages_history)
  
def send_tool_result(tool_result: str, tool_use_id: str, messages_history: list[dict] = []):
  """Wrapper function to send a tool result (output) back to Claude."""
  
  tool_response_block = {
    "role": "user",
    "content": [
      {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": tool_result
      }
    ]
  }
  
  return send_message_block(new_message_block=tool_response_block, messages_history=messages_history)

def check_and_use_tools(messages: list[dict], response: Message):
  if response.stop_reason == "tool_use":
    tool_use_content = next(
      block for block in response.content if block.type == "tool_use"
    )
    tool_result = use_tool(tool_use_content)
    
    print(f"Using Tool [{tool_use_content.name}]: \033[32m{tool_result}\033[0m\n")
    
    send_tool_result(tool_result, tool_use_content.id, messages)
    
    return messages
  
if __name__ == "__main__":
  first_message = ask_user("Tell me about the time/seats you'd like to book.")
  messages_history = send_message(first_message)