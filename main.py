from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime

# Import our custom modules
import models
from database import engine, SessionLocal

# Initialize database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Meeting Room Scheduler API")

# Tell FastAPI where to find static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 0. Serve Frontend Dashboard ---
@app.get("/")
def read_root():
    return FileResponse("static/index.html")

# --- 1. Admin Endpoint: Add a Room ---
@app.post("/rooms/")
def create_room(name: str, capacity: int, has_projector: bool, db: Session = Depends(get_db)):
    new_room = models.Room(name=name, capacity=capacity, has_projector=has_projector)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return {"message": f"Room '{name}' created successfully!", "room_id": new_room.id}

# --- 2. Employee Endpoint: Real-Time Request & Schedule ---
@app.post("/requests/")
def create_and_schedule_request(
    title: str, attendees: int, needs_projector: bool, 
    start_str: str, end_str: str, db: Session = Depends(get_db)
):
    start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
    end_time = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
    
    rooms = db.query(models.Room).all()
    if not rooms:
        raise HTTPException(status_code=400, detail="System Error: No rooms exist. Admin must add rooms first.")

    # ==========================================
    # SMART CONFLICT DETECTION
    # ==========================================
    
    # 1. Absolute Capacity Check
    max_sys_capacity = max([r.capacity for r in rooms])
    if attendees > max_sys_capacity:
        raise HTTPException(status_code=409, detail=f"Conflict: Attendees ({attendees}) exceed our largest available room (Max capacity: {max_sys_capacity}).")

    # 2. Projector Check
    projector_rooms = [r for r in rooms if r.has_projector]
    if needs_projector and not projector_rooms:
        raise HTTPException(status_code=409, detail="Conflict: Projector requested, but zero rooms in the system have one.")

    # 3. Filter rooms that meet BOTH physical requirements
    valid_physical_rooms = [r for r in rooms if r.capacity >= attendees and (not needs_projector or r.has_projector)]
    
    if not valid_physical_rooms:
        max_proj_cap = max([r.capacity for r in projector_rooms])
        raise HTTPException(status_code=409, detail=f"Conflict: No room has BOTH a projector and capacity for {attendees}. The largest room with a projector holds {max_proj_cap}.")

    # 4. Check for Time Overlaps ONLY on physically capable rooms
    assigned_room = None
    for room in valid_physical_rooms:
        overlap = False
        room_bookings = db.query(models.Booking).filter(models.Booking.room_id == room.id).all()
        
        for b in room_bookings:
            existing_req = b.request
            latest_start = max(start_time, existing_req.start_time)
            earliest_end = min(end_time, existing_req.end_time)
            if latest_start < earliest_end:
                overlap = True
                break # Time conflict found, check next room
                
        if not overlap:
            assigned_room = room
            break

    # ==========================================
    # HANDLE FINAL RESULT
    # ==========================================
    if assigned_room:
        # SUCCESS: Create Booking
        new_request = models.MeetingRequest(
            title=title, attendees=attendees, needs_projector=needs_projector,
            start_time=start_time, end_time=end_time, status="Scheduled"
        )
        db.add(new_request)
        db.commit() 
        db.refresh(new_request)
        
        new_booking = models.Booking(request_id=new_request.id, room_id=assigned_room.id)
        db.add(new_booking)
        db.commit()
        
        return {"message": f"Success! Scheduled in {assigned_room.name}."}
    else:
        # FAILURE: If we reached here, it means physical constraints passed, but ALL valid rooms were booked.
        room_names = ", ".join([r.name for r in valid_physical_rooms])
        raise HTTPException(status_code=409, detail=f"Conflict: Time slot booked. Rooms matching your needs ({room_names}) are occupied at this time. Please select a different time.")

# --- 3. Dashboard Endpoint: View Bookings ---
@app.get("/bookings/")
def get_all_bookings(db: Session = Depends(get_db)):
    bookings = db.query(models.Booking).join(models.MeetingRequest).order_by(models.MeetingRequest.start_time.asc()).all()
    result = []
    for b in bookings:
        result.append({
            "booking_id": b.id,
            "room_name": b.room.name,
            "meeting_title": b.request.title,
            "start_time": b.request.start_time,
            "end_time": b.request.end_time
        })
    return result