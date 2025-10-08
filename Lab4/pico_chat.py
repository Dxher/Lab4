from machine import UART, Pin
import time

# Set up UART
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))


print("Chat ready. Type a message and press Enter:")

# Record the current time that a message has not been sent(in milliseconds)
last_send = time.ticks_ms()

while True:
    # RECEIVE
    if uart.any(): # Check if any data has arrived
        data = uart.read() # read all available bytes
        if data: # make sure something was actually read
            print("Received:", data.decode('utf-8'))

    # SEND
    msg = input("You: ")
    if msg: # if the user typed something
        uart.write(msg + "\n") # send it over UART
        last_send = time.ticks_ms() # reset the timer

    # KEEP ALIVE
    if last_send > 10000: # every 10 seconds
        uart.write("keep alive \n") # send the keep-alive message
        last_send = time.ticks_ms() # reset timer again

    time.sleep(0.1) # pause briefly, good for cpu
