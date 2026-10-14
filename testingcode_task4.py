# Testing med laget lite datasett
# skal fungere - hetebølge
test_df_hw = pd.DataFrame({
    "date": pd.date_range("2025-07-01", periods=5),
    "temperature": [28, 29, 30, 28, 27]
})

print("test_hw:", find_heatwaves(test_df_hw))

# skal ikke fungere - periode for kort
test_df_short = pd.DataFrame({
    "date": pd.date_range("2025-07-01", periods=5),
    "temperature": [28, 29, 30, 28, 24],
})

print("test_short:", find_heatwaves(test_df_short))

# skal fungere - hetebølge fortsetter til siste dag av datasett
# Tester hetebølge som fortsetter til siste dag
test_df_new_year = pd.DataFrame({
    "date": pd.date_range("2025-12-27", periods=6),
    "temperature": [24, 28, 29, 30, 28, 27],
})

print("test_new_year:", find_heatwaves(test_df_new_year))

print("MET data:", heatwaves)

# kontroll av temperaturmålinger for registrerte hetebølger
for start_date, end_date in heatwaves:
    print(f"Heatwave: {start_date} to {end_date}")

    mask = (
        (temperature_df['date'] >= start_date)
        & (temperature_df['date'] <= end_date)
    )

    print(temperature_df.loc[mask])