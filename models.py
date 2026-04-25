from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    capacity = Column(Integer)
    has_projector = Column(Boolean, default=False)
    
class MeetingRequest(Base):
    __tablename__ = 'meeting_requests'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    attendees = Column(Integer)
    needs_projector = Column(Boolean, default=False)
    status = Column(String, default="Pending") # Pending, Scheduled, Failed

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('meeting_requests.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    
    request = relationship("MeetingRequest")
    room = relationship("Room")