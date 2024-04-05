from datetime import datetime, timedelta


def generate_timestamps(start_time_str, end_time_str, n):
    # Convert start and end time strings to datetime objects
    start_time = datetime.strptime(start_time_str, "%H:%M")
    end_time = datetime.strptime(end_time_str, "%H:%M")

    # Calculate time difference between start and end time
    time_diff = end_time - start_time
    if n=
    if n==2:

    # Calculate time interval between timestamps
    interval = time_diff / (n - 1)

    # Generate N timestamps
    timestamps = [start_time + i * interval for i in range(n)]

    # Format timestamps as strings in 24-hour format
    timestamps_str = [time.strftime("%H:%M") for time in timestamps]

    return timestamps_str


# Example usage
start_time_str = "08:00"
end_time_str = "16:00"
n = 5

timestamps = generate_timestamps(start_time_str, end_time_str, n)
print(timestamps)
