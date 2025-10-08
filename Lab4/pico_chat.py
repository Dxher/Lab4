from machine import UART, Pin
import uasyncio as asyncio
import time, sys, uselect

# Use UART1 on GP8 (TX) and GP9 (RX)
uart = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(9))

print("Async UART Chat ready. Type to send messages!")

# Non-blocking standard input setup
poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

# RECEIVE
# This loop checks for incoming UART data without blocking
async def uart_receiver():
    while True:
        if uart.any():                 # if any data has arrived
            data = uart.read()         # read all available bytes
            if data:                   # make sure it's not empty
                print("[Received]:", data.decode('utf-8').strip()) # decode and print
        await asyncio.sleep(0.1)       # short pause (lets other tasks run)

# SEND
# This loop waits for user input and sends it out over UART
async def user_input_sender():
    while True:
        # non-blocking "input": only read if a full line is waiting
        msg = None
        if poll.poll(0):                               # don't block
            msg = sys.stdin.readline().rstrip("\r\n")  # get the line

        if msg:                        # if message not empty
            uart.write(msg + '\n')     # send message
            print("[Sent]:", msg)
            # update last_send so keep-alive timer resets
            global last_send
            last_send = time.ticks_ms()

        await asyncio.sleep(0.1)         # yield control to receiver

# KEEP ALIVE
# This loop sends a heartbeat message every 10 seconds
last_send = time.ticks_ms()
async def keep_alive():
    global last_send
    while True:
        if time.ticks_diff(time.ticks_ms(), last_send) > 10000: # 10 seconds elapsed
            heartbeat_msg = "keep alive"
            uart.write(heartbeat_msg + '\n') # send heartbeat
            print("[Sent]:", heartbeat_msg)
            last_send = time.ticks_ms() # reset timer
        await asyncio.sleep(1)

# MAIN 
# Run both send and receive tasks at the same time
async def main():
    await asyncio.gather(
        uart_receiver(),
        user_input_sender(),
        keep_alive()
    )

# Call main
asyncio.run(main())
