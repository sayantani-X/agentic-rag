from config import client, LLM_MODEL


class MemoryManager:

    def __init__(self, max_history=5):

        self.history = []
        self.max_history = max_history

        self.last_mode = None
        self.last_resource = None

    # -------------------------
    # ADD INTERACTION
    # -------------------------

    def add(self, user_query, assistant_answer):

        self.history.append({
            "user": user_query,
            "assistant": assistant_answer
        })

        if len(self.history) > self.max_history:
            self.summarize()

    # -------------------------
    # GET HISTORY STRING
    # -------------------------

    def get_history_text(self):

        return "\n".join([
            f"User: {h['user']}\nAssistant: {h['assistant']}"
            for h in self.history
        ])

    # -------------------------
    # SUMMARIZATION
    # -------------------------

    def summarize(self):

        try:
            prompt = f"""
Summarize the following conversation briefly while preserving key information:

{self.get_history_text()}
"""

            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )

            summary = response.choices[0].message.content

            # replace history with summary
            self.history = [{
                "user": "Summary",
                "assistant": summary
            }]

        except:
            # fallback: truncate
            self.history = self.history[-self.max_history:]

    # -------------------------
    # TRACK MODE
    # -------------------------

    def set_mode(self, mode):

        if mode in ["CONTEXT_QA", "IMAGE_QA", "WIKIPEDIA_SEARCH"]:
            self.last_mode = mode

    def get_mode(self):
        return self.last_mode

    # -------------------------
    # TRACK RESOURCE
    # -------------------------

    def set_resource(self, resource):
        self.last_resource = resource

    def get_resource(self):
        return self.last_resource

    # -------------------------
    # RESET MEMORY
    # -------------------------

    def reset(self):

        self.history = []
        self.last_mode = None
        self.last_resource = None

        print("\nMemory cleared.\n")