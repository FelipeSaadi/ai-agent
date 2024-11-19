import csv
from datetime import datetime

def book_table(table_name: str, time: str, reservation_name: str) -> bool:
  input_time = datetime.strptime(time, '%H:%M')
  
  with open('data/bookings.csv', 'r') as file:
    reader = csv.reader(file)
    bookings = list(reader)
    
  for booking in bookings:
    booking_time = datetime.strptime(booking['time'], '%H:%M')
    
    if booking_time == input_time and table_name in booking:
      if booking[table_name] == "":
        booking[table_name] = reservation_name
        
        with open('data/bookings.csv', 'w', newline="") as file:
          fieldsnames = reader.fieldnames
          writer = csv.DictWriter(file, fieldnames=fieldsnames)
          writer.writeheader()
          writer.writerows(bookings)
          
        return (
          f"Booking Success: {table_name} at {time} for {reservation_name}"
        )
      else:
        return (
          f"Booking Failed: {table_name} at {time} is already booked"
        )
  return (
    f"Booking Failed: {table_name} at {time} is not found"
  )