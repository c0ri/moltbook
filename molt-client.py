import os
import requests
from dotenv import load_dotenv, set_key

class MoltbookClient:
    def __init__(self):
        self.base_url = "https://www.moltbook.com/api/v1"
        self.env_path = os.path.join(os.getcwd(), ".env")
        load_dotenv(self.env_path)
        
        # Load credentials from .env
        self.api_key = os.getenv("MOLTBOOK_API_KEY")
        self.agent_id = os.getenv("MOLTBOOK_ID")
        self.name = os.getenv("MOLTBOOK_NAME", "Unknown Agent")

    def _get_headers(self):
        if not self.api_key:
            return {}
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def register(self, name, description):
        """Registers agent and extracts nested 'agent' data into .env"""
        url = f"{self.base_url}/agents/register"
        payload = {"name": name, "description": description}
        
        print(f"📡 Registering '{name}'...")
        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Navigate the nested structure: data['agent']
            agent_data = data.get('agent', {})
            if not agent_data:
                print("❌ Error: No agent data found in response.")
                return False

            # Ensure .env exists
            if not os.path.exists(self.env_path):
                with open(self.env_path, 'w') as f: f.write("")

            # Map and save keys
            mapping = {
                "MOLTBOOK_ID": agent_data.get("id"),
                "MOLTBOOK_API_KEY": agent_data.get("api_key"),
                "MOLTBOOK_CLAIM_URL": agent_data.get("claim_url"),
                "MOLTBOOK_VERIFY_CODE": agent_data.get("verification_code"),
                "MOLTBOOK_NAME": agent_data.get("name")
            }

            for env_key, val in mapping.items():
                if val:
                    set_key(self.env_path, env_key, str(val))
            
            print("✅ Registration saved to .env!")
            print(f"🔗 CLAIM URL: {agent_data.get('claim_url')}")
            
            # Refresh local variables for the current session
            load_dotenv(self.env_path, override=True)
            self.__init__()
            return True

        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return False

    # --- API Interaction Methods ---
    def get_feed(self):
        try:
            res = requests.get(f"{self.base_url}/feed", headers=self._get_headers())
            return res.json().get('posts', [])
        except: return []

    def post(self, content):
        return requests.post(f"{self.base_url}/posts", 
                             json={"content": content}, headers=self._get_headers()).json()

    def comment(self, post_id, content):
        return requests.post(f"{self.base_url}/posts/{post_id}/comments", 
                             json={"content": content}, headers=self._get_headers()).json()

    def vote(self, post_id, direction="up"):
        url = f"{self.base_url}/posts/{post_id}/vote"
        return requests.post(url, json={"direction": direction}, headers=self._get_headers()).json()

    def create_submolt(self, name, description):
        return requests.post(f"{self.base_url}/submolts", 
                             json={"name": name, "description": description}, headers=self._get_headers()).json()

    def subscribe(self, submolt_id):
        return requests.post(f"{self.base_url}/submolts/{submolt_id}/subscribe", headers=self._get_headers()).json()

    def semantic_search(self, query):
        params = {"q": query, "type": "semantic"}
        return requests.get(f"{self.base_url}/search", params=params, headers=self._get_headers()).json()

# --- Main Interface ---
def run_menu():
    client = MoltbookClient()
    
    if not client.api_key:
        print("Welcome to Moltbook! No credentials found.")
        name = input("Enter Agent Name: ")
        desc = input("Enter Agent Description: ")
        if not client.register(name, desc): return

    while True:
        print(f"\n══════════════════════════════\n  MOLTBOOK: {client.name}\n══════════════════════════════")
        print("1. 📱 View Feed & Reply")
        print("2. ✍️  New Post")
        print("3. 🔍 Semantic Search")
        print("4. 🏗️  Create Submolt")
        print("5. ➕ Join Submolt (by ID)")
        print("6. 🚪 Exit")
        
        choice = input("\nSelect action: ")

        if choice == "1":
            posts = client.get_feed()
            if not posts:
                print("Feed is empty. Ensure your agent is 'claimed'.")
            else:
                for i, p in enumerate(posts[:10]):
                    author = p.get('author', {}).get('name', 'Unknown')
                    print(f"{i+1}. [{author}]: {p.get('content')}")
                
                sel = input("\nEnter # to reply/upvote, or 'b' for back: ")
                if sel.isdigit() and 0 < int(sel) <= len(posts):
                    target = posts[int(sel)-1]
                    action = input("(r)eply or (v)ote? ")
                    if action.lower() == 'r':
                        client.comment(target['id'], input("Message: "))
                        print("✅ Reply sent!")
                    elif action.lower() == 'v':
                        client.vote(target['id'], "up")
                        print("✅ Upvoted!")

        elif choice == "2":
            client.post(input("What's on your mind? "))
            print("✅ Post sent!")

        elif choice == "3":
            query = input("Search meaning: ")
            results = client.semantic_search(query)
            for p in results.get('posts', []):
                print(f"- {p['content']}")

        elif choice == "4":
            name = input("Submolt Name: ")
            desc = input("Description: ")
            res = client.create_submolt(name, desc)
            print(f"✅ Created! ID: {res.get('id')}")

        elif choice == "5":
            client.subscribe(input("Enter Submolt ID: "))
            print("✅ Subscribed!")

        elif choice == "6":
            break

if __name__ == "__main__":
    run_menu()
