class Event:
    def __init__(self, time: str, title: str, description: str):
        self.time = time
        self.title = title
        self.description = description

    def format_event(self) -> str:
        return f"🕙 *{self.time}* — *{self.title}*\n_{self.description}_\n"

class Schedule:
    def __init__(self, events: list = None):
        self.events = events if events is not None else []

    def format_schedule(self) -> str:
        if not self.events:
            return "⚠ Пока нет запланированных мероприятий."

        header = "📅 *Расписание мероприятий:*\n\n"

        body = ""
        for event in self.events:
            body += event.format_event()

        return header + body
