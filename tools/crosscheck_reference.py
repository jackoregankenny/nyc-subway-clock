import sys
from google.transit import gtfs_realtime_pb2
m = gtfs_realtime_pb2.FeedMessage(); m.ParseFromString(open(sys.argv[1], 'rb').read())
arr = set()
for e in m.entity:
    if e.is_deleted or not e.HasField('trip_update'): continue
    tu = e.trip_update
    if tu.trip.route_id != sys.argv[2] or tu.trip.schedule_relationship in (3, 7): continue
    for s in tu.stop_time_update:
        if s.stop_id != sys.argv[3] or s.schedule_relationship == 1: continue
        t = s.arrival.time if s.HasField('arrival') and s.arrival.time else (s.departure.time if s.HasField('departure') else 0)
        if t > 0: arr.add(t)
print(" ".join(str(t) for t in sorted(arr)[:8]) + (" " if arr else ""))
