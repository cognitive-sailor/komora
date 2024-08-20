import asyncio
import random

# Placeholder functions to interact with hardware (to be replaced with actual implementations)
async def read_temperature(t):
    # Simulate reading temperature from a sensor (replace with actual sensor reading code)
    await asyncio.sleep(0.5)  # Simulate delay in reading
    return t+random.randint(-2,1) # Example: return a constant temperature for now

async def turn_on_ac():
    print("AC turned ON")

async def turn_off_ac():
    print("AC turned OFF")

# Set desired temperature and hysteresis
setpoint_temperature = 8
hysteresis = 0.5

# Control function
async def control_temperature():
    ac_on = False
    initial_temperature = 20
    start = True
    while True:

        if start:
            current_temperature = await read_temperature(initial_temperature)
            start = False
        else:
            old_temperature = current_temperature
            current_temperature = await read_temperature(old_temperature)

        if current_temperature > setpoint_temperature + hysteresis and not ac_on:
            await turn_on_ac()
            ac_on = True
        elif current_temperature < setpoint_temperature - hysteresis and ac_on:
            await turn_off_ac()
            ac_on = False

        print(f"Current temperature: {current_temperature}")
        # Sleep for a short interval before the next check
        await asyncio.sleep(0.2)

# Main function
async def main():
    # Start the temperature control task
    await control_temperature()

# Run the asyncio event loop
asyncio.run(main())
