# Python code generated by CAIT's Visual Programming Interface

import cait.essentials

def setup():
    cait.essentials.initialize_component('voice', mode='on_devie')
    
def main():
    cait.essentials.say('Hello, world!')

if __name__ == "__main__":
    setup()
    main()