from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import json
from datetime import date, datetime
import copy

# Create a FastAPI application instance
app = FastAPI()

# Define a function to return a description of the app
def get_app_description():
    return (
        "Welcome to the Calendar Service API... "
        "This API accepts calendar events comprised of a date-time and description, in JSON format, and saves them persistently to an events_calendar.json file. "
        "On request, the API returns these saved calendar events, in a JSON format aligned to the format used during event input, based on user specified criteria."
    )

# Define the root endpoint (home) to return the app description
@app.get("/")
async def home():
    return {"message": get_app_description()}

# Define a Pydantic model for calendar event data
class CalendarEvent(BaseModel):
    description: str
    time: str
    id: int = Field(default=0, ge=0,
                       description="Using a default id value of 0, or an id value already assigned to an event in file events_calendar.json at that point in time, with API endpoint POST results in an id value auto-assignment equal to the smallest positive integer not already existing as an id value in file events_calendar.json."
                     )

# Open and read the JSON file that acts as a persistent store of calendar events
with open('events_calendar.json', 'r') as file:
    calendar = json.load(file)   #json,load(file) yields a Python dict obj; this dict is a list of current event dict objs in file events_calendar.json
calendar = calendar['events']   #converts calendar dict object to a listthe loaded dict obj to a list obj


# Define a custom serialization function for datetime objects
def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat("T", "seconds")
# json_dcal = json.dumps(dcal, default=serialize_datetime, indent=2)


@app.post('/events', response_model=CalendarEvent)
async def create_event(event: CalendarEvent):
    global calendar

    n = len(calendar)
    curr_event_ids = [calendar[i]['id'] for i in range(n)]
    minima = min(set(range(1, 1000001)) - set(curr_event_ids))
    if (event.id == 0) or (event.id in curr_event_ids):
        event.id = minima

    return_event = copy.deepcopy(event)
    calendar.append(event.dict())

    calendar = sorted(calendar, key=lambda x: x['id'])   #calendar is still a lit of event dicts
    dcal = {"events": calendar}
    json_dcal = json.dumps(dcal, indent=2)
    with open('events_calendar.json', 'w') as outfile:
        outfile.write(json_dcal)

    return return_event   #{'event': new_event}


#Get date ranged events in calendar
@app.get('/events', response_model=list[CalendarEvent])
async def get_events(datetime_format: str | None = '%Y-%m-%dT%H:%M:%S',
                     from_time: str | None = datetime.combine(date.today(), datetime.min.time()).isoformat("T", "seconds"),
                     to_time: str | None = datetime.now().isoformat("T", "seconds")
                     ):
    if not datetime_format or (datetime_format != '%Y-%m-%dT%H:%M:%S'):
        datetime_format = '%Y-%m-%dT%H:%M:%S'

    from_time_dt, to_time_dt = datetime.fromisoformat(from_time), datetime.fromisoformat(to_time)
    return_calendar = copy.deepcopy(calendar)
    for e in return_calendar:
        e['time'] = datetime.fromisoformat(e['time'])
        if not (from_time_dt <= e['time'] <= to_time_dt):
            del e['time']

    ret_calendar = [e for e in return_calendar if len(e) == 3]
    for e in ret_calendar:
        e['time'] = e['time'].isoformat("T", "seconds")
    ret_calendar = [CalendarEvent.model_validate_json(json.dumps(e, indent=2)) for e in ret_calendar]
    return ret_calendar


#Get a calendar event by its ID
@app.get('/events/{id}', response_model=CalendarEvent)
async def get_event(id: int, datetime_format: str | None = '%Y-%m-%dT%H:%M:%S'):
    if not datetime_format or (datetime_format != '%Y-%m-%dT%H:%M:%S'):
        datetime_format = '%Y-%m-%dT%H:%M:%S'

    #calendar is a list of event dicts
    event = next((e for e in calendar if e['id'] == id), None)
    if event is None:
        raise HTTPException(status_code=404, detail=f'Event with id={id} not found')

    event = CalendarEvent.model_validate_json(json.dumps(event, indent=2))
    return event


if __name__ == "__main__":
	import uvicorn

	#Run the FastAPI application on the specified host and port
	uvicorn.run(app, host="127.0.0.1", port=8000)
