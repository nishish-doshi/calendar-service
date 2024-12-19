calendar-service

The aim of this project is to write a simple calendar service. 
The service accepts calendar events comprised of a date-time and description, in JSON format, and saves them persistently into a text (.json) file. 
On request, the service should return the saved calendar events in a JSON format aligned to the input one. The full protocol implemented by the service is provided below.


Protocol Endpoints
• /events (POST): Accepts events in event payload format. Returns the inserted event as a JSON object.
• /events/[?datetime_format=] (GET): Returns the named event in event payload format. The optional query parameter datetime_format is described in arguments. Returns the event with matching id as a JSON object.
• /events[?][datetime_format=][&][from_time=][&][to_time=] (GET): Returns all events falling within a date range. Where the date range defaults to "today" at 00:00:00 to now. The optional query parameters are described in arguments. Returns a list of matching event JSON objects. 


Event Payload Format 
The format for insertion and return of calendar events is:
{
  "description": "",
  "time": "",
  "id": ""
}
where the id field not only contained in queries.


Arguments
• datetime_format: Date-time format for parsing/printing of dates. Compatible with strptime /strftime format specification. The default value for this argument is %Y-%m-%dT%H:%M:%S, e.g. 2024-01-01T00:00:00.
• from_time: Specifies the start of a date range. The expected date time format is governed by the value/default of the datetime_format argument. Defaults to start of the current day.
• to_time: Specifies the end of a date range. The expected date time format is governed by the value/default of the datetime_format argument. Defaults to the datetime of request receipt.
