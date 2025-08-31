from services import car_counter

df = car_counter.read_data(
    "/Users/swathiradhakrishnan/Documents/car-counter-service/sample.csv"
)
print(f"Total cars: {car_counter.total_cars(df)}")
print(f"Cars per day: {car_counter.cars_per_day(df)}")
print(f"Top 3 half-hours: {car_counter.top_n_half_hours(df, n=3)}")
print(
    f"Least 3 contiguous half-hours: {car_counter.least_n_contiguous_half_hours(df, n=3)}"
)
print(
    f"Least 5 contiguous half-hours: {car_counter.least_n_contiguous_half_hours(df, n=5)}"
)
