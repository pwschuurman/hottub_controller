// For the ATTiny85
#include <avr/interrupt.h>
#include <util/atomic.h>
#include <avr/io.h>
//#include <util/delay.h>
#define XTAL 8000000L
#define DELAY_FREQ 1

volatile uint32_t buffer = 0;
volatile unsigned char buffer_counter = 0;
volatile unsigned char start_enable = 0;
volatile unsigned char temp = 104;
volatile unsigned char status = 5;
volatile unsigned char control = 10;

// Stores the current button, if one is currently pressed.
volatile unsigned char cur_button;

#define DATA_PIN PD4
#define ENABLE_PIN PD3
#define CLK_PIN PD2

#define DI_PIN PB5
#define DO_PIN PB6
#define SCLK_PIN PB7

#define TEMP_UP_BUTTON   0
#define TEMP_DOWN_BUTTON 1
#define LIGHT_BUTTON     2
#define PUMP_BUTTON      3

#define TEMP_UP_PIN PD0
#define TEMP_DOWN_PIN PD1
#define PUMP_PIN PA0
#define LIGHT_PIN PA1

#define DEBUG_PIN PB4
// External Interrupt Request 0
// This is the CLOCK Interrupt
// Whenever we receive an interrupt here, we should accept a bit into buffer.
ISR(INT0_vect)
{
    // If we previously received the command to start receiving data, then we
    // should push this bit into the byte buffer.
    if(start_enable) {
        buffer_counter++;
        buffer = (buffer << 1) | ((PIND & _BV(DATA_PIN))!=0);
    }

    // Reset the interrupt flag
    EIFR |= _BV(INTF0);
}

// External Interupt Request 1
// This is the ENABLE Interrupt
// Whenever we receive an interrupt here, we should enable data reception.
ISR(INT1_vect)
{
    // Toggle that pin
    // Start up
    if((PIND & _BV(ENABLE_PIN))==0)
    {
        // We detected a falling edge!, start recording data.
        start_enable = 1;
        //buffer_counter = 0;
        //buffer = 0;
    } else {
        // We detected a leading edge. Buffer has valid data now.
        start_enable = 0;
        if(buffer_counter>=32) {
            // Temperature is BCD encoded.
            temp =
              (((buffer >> 16) & 0x0F) * 100) +
              (((buffer >> 12) & 0x0F) * 10) +
              ((buffer >> 8) & 0x0F);
            status = (buffer >> 23) & 0x1F;
            buffer = 0;
            buffer_counter = 0;
        }
    }

    // Reset the interrupt flag
    EIFR |= _BV(INTF1);
}

void stop_timer(void)
{
    // Disable Timer1 Compare Interrupt
    TIMSK &= ~_BV(OCIE1A);
}

void unpress_button(unsigned char button_num)
{
    switch(button_num)
    {
        // Float these high (Hi-Z)
        case TEMP_UP_BUTTON:
            DDRD &= ~_BV(TEMP_UP_PIN);
            break;
        case TEMP_DOWN_BUTTON:
            DDRD &= ~_BV(TEMP_DOWN_PIN);
            break;
        case PUMP_BUTTON:
            DDRA &= ~_BV(PUMP_PIN);
            break;
        case LIGHT_BUTTON:
            DDRA &= ~_BV(LIGHT_PIN);
            break;
    }
}

ISR(TIMER1_COMPA_vect)
{
    // Stop the Timer
    stop_timer();

    // Unpress button
    unpress_button(cur_button);
}

// Initialize the timer to run at CLK/256.
void start_timer(void)
{
    // Set Clock Prescalar CLK/256. Since the clock frequency is around 8MHz,
    // This means that 3125 * 256 = 800000 cycles ~= 0.1ms.
    TCCR1B = _BV(CS13) | _BV(CS10);

    // Reset Timer
    TCNT1=0;
    OCR1A = 3125;

    // Enable Compare Timer1 Interrupt Enable
    TIMSK |= _BV(OCIE1A);
}

void press_button(unsigned char button_num)
{
    switch(button_num)
    {
        // Sink these Low (Open Drain)
        case TEMP_UP_BUTTON:
            DDRD |= _BV(TEMP_UP_PIN);
            break;
        case TEMP_DOWN_BUTTON:
            DDRD |= _BV(TEMP_DOWN_PIN);
            break;
        case PUMP_BUTTON:
            DDRA |= _BV(PUMP_PIN);
            break;
        case LIGHT_BUTTON:
            DDRA |= _BV(LIGHT_PIN);
            break;
    }
    cur_button = button_num;
    start_timer();
}

// This is the SPI interrupt vector.
// This is used for communicating with the Raspberry Pi.
// Data gets transmitted using one byte on the SPI, and then the next byte sent
// back is the response.
ISR(USI_OVERFLOW_vect)
{
    unsigned char data;
    data = USIDR;
    switch(data)
	{
        case 0x11:
            // Press Temp Up Button
            USIDR=0;
            press_button(TEMP_UP_BUTTON);
            break;
        case 0x12:
            // Press Temp Down Button
            USIDR=0;
            press_button(TEMP_DOWN_BUTTON);
            break;
        case 0x13:
            // Press Pump Command
            USIDR=0;
            press_button(PUMP_BUTTON);
            break;
        case 0x14:
            // Press Light Button
            USIDR=0;
            press_button(LIGHT_BUTTON);
            break;
        case 0x21:
            // Echo out the Control
            ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
            {
                USIDR = control;
            }
            break;
        case 0x22:
            // Echo the Temperature
            ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
            {
                USIDR = temp;
            }
            break;
        case 0x23:
            // Echo the Status bits
            ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
            {
                USIDR = status;
            }
            break;
        case 0x24:
            // Echo the current buffer count (used for debugging).
            USIDR = buffer_counter;
            break;
	}

    // Reset the SPI Flag
    USISR = _BV(USIOIF);
}

// Configure the keypad pins. These are hooked up in a high impedence state,
// using an I2C line.
void init_keypad_pins(void)
{
    // Set Keypad pins as outputs
    DDRD &= ~_BV(TEMP_UP_PIN) & ~_BV(TEMP_DOWN_PIN);
    DDRA &= ~_BV(LIGHT_PIN) & ~_BV(PUMP_PIN);

    // Don't bother setting pullups as these already have pullups

    // Set 1 for all the outputs
    PORTD &= ~_BV(TEMP_UP_PIN) & ~_BV(TEMP_DOWN_PIN);
    PORTA &= ~_BV(LIGHT_PIN) & ~_BV(PUMP_PIN);
}

// Configure the SPI ports, for accepting data from the Raspberry Pi.
void init_spi(void)
{
    // Set DDRB (Controls Input/Output of Port B)
    // DO Pin is configured for output
    DDRB |= _BV(DO_PIN);

    // All other pins as input
    //DDRB &= ~_BV(DI_PIN) & ~_BV(SCLK_PIN);

    // Pullups on Input Pins
    //PORTB |= _BV(DI_PIN) | _BV(SCLK_PIN);

    // Enable USI Interrupt
    // Set Three Wire Mode (USIWM = 01)
    // Set USICS = 11 (External Negative Edge) counter=External
    USICR = _BV(USIOIE) | _BV(USIWM0) | _BV(USICS1);// | _BV(USICS0);

    // Clear overflow flag
    USISR = _BV(USIOIF);
}

// Configure the external interrupt for receiving data from the hot tub
// controller.
void init_external(void)
{
    // Set DDRD (Controls Input/Output for Port B)
    // Set CLK, DATA and ENABLE as Inputs
    DDRD &= ~_BV(CLK_PIN) & ~_BV(DATA_PIN) & ~_BV(ENABLE_PIN);

    // Don't use Pullup Resistors (Hot Tub Already has them).
    // This puts the external into Hi-Z configuration
    PORTD &= ~_BV(CLK_PIN) & ~_BV(DATA_PIN) & ~_BV(ENABLE_PIN);

    // Allow External Interrupts on Int0 and Int1
    // Clock Interrupt: ISC0 = 11 (Rising Edge)
    // Enabled/Disable Interrupt: ISC1 = 01 (Any change)
    MCUCR |= _BV(ISC10) | _BV(ISC01) | _BV(ISC00);
    MCUCR &= ~_BV(ISC11);

    // Enable Int0 and Int1 interrupts
    GIMSK |= _BV(INT0) | _BV(INT1);

    // Clear Overflow Flag
    EIFR |= _BV(INTF1) | _BV(INTF0);
}

// Initialize the clock used for button presses.
void init_clock(void)
{
    // Set Enable bit, and then set to 1 divisor
    CLKPR=0x80;
    CLKPR=0x00;
}

void init_debug(void)
{
    // All other pins as input
    DDRB |= _BV(DEBUG_PIN);

    // Set as high
    PORTB |= _BV(DEBUG_PIN);
}

void init(void)
{
    // Init Debug
    // init_debug();

    // Init Clock
    init_clock();

    // Init the SPI
    init_spi();

    // Init the External
    init_external();

    // Init the keypad pins
    init_keypad_pins();

    // Enable Global Interrupts
    sei();
}

int main(void)
{
    init();

    // Everything is handled by interrupts!
    while(1) {}

    return 0;
}
