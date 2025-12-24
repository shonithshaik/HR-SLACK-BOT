import os
import json
import httpx
import asyncio
from fastapi import FastAPI, Request, BackgroundTasks
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from app.gemini import ask_gemini_fast
from app.email_utils import send_hr_email

load_dotenv()

app = FastAPI()

slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
BOT_USER_ID = os.getenv("BOT_USER_ID")
processed_event_ids = set()

@app.on_event("startup")
async def schedule_heartbeat():
    asyncio.create_task(heartbeat())

async def heartbeat():
    url = "https://hr-slack-bot-yz67.onrender.com/health"
    while True:
        try:
            async with httpx.AsyncClient() as client:
                await client.get(url)
        except Exception as e:
            print(f"Heartbeat failed: {e}")
        await asyncio.sleep(600) 

@app.get("/health")
async def health_check():
    return {"status": "alive"}

async def process_message(user_id, channel_id, current_text, thread_ts):
    try:

        user_info = slack_client.users_info(user=user_id)
        user_email = user_info['user']['profile'].get('email', 'no-email@found.com')
        user_real_name = user_info['user']['profile'].get('real_name', 'Unknown User')

        result = slack_client.conversations_replies(
            channel=channel_id,
            ts=thread_ts,
            limit=10  
        )
        
        messages = result.get("messages", [])
        history_context = ""
        for msg in messages:
            role = "Bot" if msg.get("user") == BOT_USER_ID else "User"
            history_context += f"{role}: {msg.get('text')}\n"

        full_prompt = f"CONVERSATION HISTORY:\n{history_context}\nNEW QUESTION: {current_text}"
        
        answer = ask_gemini_fast(full_prompt)

        if "NOT_FOUND" in answer:
            print(f"Sending escalation email for {user_real_name}...")
            send_hr_email(user_id, user_email, current_text)
            
            answer = f"I couldn't find a specific answer in our HR docs, so I've escalated this to the team. They will email you directly at {user_email}!"
        
        slack_client.chat_postMessage(
            channel=channel_id,
            text=f"<@{user_id}> {answer}",
            thread_ts=thread_ts
        )
    except SlackApiError as e:
        print(f"Slack API Error: {e.response['error']}")
    except Exception as e:
        print(f"General Error: {e}")


@app.post("/slack/events")
async def handle_events(request: Request, background_tasks: BackgroundTasks):
    raw_body = await request.body()
    data = json.loads(raw_body)

    if "challenge" in data:
        return {"challenge": data["challenge"]}

    if request.headers.get("x-slack-retry-num"):
        return {"status": "ignored_retry"}

    event_id = data.get("event_id")
    if event_id in processed_event_ids:
        return {"status": "already_processed"}
    processed_event_ids.add(event_id)

    event = data.get("event", {})
    
    if event.get("bot_id") or event.get("subtype") == "bot_message":
        return {"status": "ignored_bot"}

    user_id = event.get("user")
    channel_id = event.get("channel")
    text = event.get("text")
    thread_ts = event.get("thread_ts") or event.get("ts") 

    is_mention = event.get("type") == "app_mention"
    is_dm = event.get("channel_type") == "im"
   
    is_thread_followup = event.get("type") == "message" and "thread_ts" in event

    if is_mention or is_dm or is_thread_followup:
        background_tasks.add_task(process_message, user_id, channel_id, text, thread_ts)
        return {"status": "accepted"}

    return {"status": "ignored"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)