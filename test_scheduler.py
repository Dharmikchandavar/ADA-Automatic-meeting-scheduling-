from datetime import datetime, timedelta

# Mock classes to mimic our database models
class MockRoom:
    def __init__(self, id, capacity, has_projector):
        self.id = id
        self.capacity = capacity
        self.has_projector = has_projector

class MockMeeting:
    def __init__(self, id, attendees, needs_projector, start, end):
        self.id = id
        self.attendees = attendees
        self.needs_projector = needs_projector
        self.start_time = start
        self.end_time = end

# Import your backtracking functions
from scheduler import schedule_meetings_backtrack

def run_tests():
    print("--- Running Scheduler Tests ---")
    
    # 1. Setup Mock Rooms
    rooms = [
        MockRoom(id=1, capacity=5, has_projector=False),  # Small room
        MockRoom(id=2, capacity=20, has_projector=True)   # Boardroom
    ]
    
    # 2. Setup Time Slots
    today = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    slot_1_start = today
    slot_1_end = today + timedelta(hours=1)
    
    # 3. Setup Mock Meetings (Notice: Meeting 1 & 2 happen at the same time)
    requests = [
        # Small meeting, needs projector
        MockMeeting(id=101, attendees=4, needs_projector=True, start=slot_1_start, end=slot_1_end),
        # Large meeting, no projector
        MockMeeting(id=102, attendees=15, needs_projector=False, start=slot_1_start, end=slot_1_end)
    ]
    
    # 4. Initialize assignments dictionary
    assignments = {room.id: [] for room in rooms}
    
    # 5. Execute Backtracking
    print("Attempting to schedule...")
    success = schedule_meetings_backtrack(0, requests, rooms, assignments)
    
    # 6. Evaluate Results
    if success:
        print("✅ SUCCESS! All meetings scheduled without conflict.")
        for room_id, meetings in assignments.items():
            print(f"Room {room_id} bookings:")
            for m in meetings:
                print(f"  -> Meeting {m.id} ({m.attendees} people)")
    else:
        print("❌ FAILED. Could not resolve schedule.")

if __name__ == "__main__":
    run_tests()