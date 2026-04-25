def is_valid(meeting, room, current_room_bookings):
    # 1. Check Capacity
    if room.capacity < meeting.attendees:
        return False
    
    # 2. Check Equipment
    if meeting.needs_projector and not room.has_projector:
        return False
        
    # 3. Check Time Overlaps
    for booking in current_room_bookings:
        # Two intervals overlap if: max(start1, start2) < min(end1, end2)
        latest_start = max(meeting.start_time, booking.start_time)
        earliest_end = min(meeting.end_time, booking.end_time)
        if latest_start < earliest_end:
            return False # Conflict found!
            
    return True

def schedule_meetings_backtrack(req_index, requests, rooms, assignments):
    # Base Case: All meetings have been successfully assigned
    if req_index == len(requests):
        return True
        
    current_meeting = requests[req_index]
    
    # Recursive Step: Try placing the current meeting in every available room
    for room in rooms:
        if is_valid(current_meeting, room, assignments[room.id]):
            # Action: Temporarily assign the meeting
            assignments[room.id].append(current_meeting)
            
            # Recurse: Try to schedule the next meeting
            if schedule_meetings_backtrack(req_index + 1, requests, rooms, assignments):
                return True
                
            # Backtrack: It didn't work out, remove the meeting and try the next room
            assignments[room.id].pop()
            
    # Fail State: No room could accommodate this meeting without breaking the chain
    return False