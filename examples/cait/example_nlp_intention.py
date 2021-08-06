# Python code generated by CAIT's Visual Programming Interface

import cait.essentials

intention = None
entities = None
first_entity = None

def setup():
    cait.essentials.initialize_component('nlp', 'english_default')
    
def main():
    global intention, entities, first_entity
    intention = cait.essentials.analyse_text('I am Michael')
    print('Intention topic is: ' + str(intention['topic']))
    entities = intention['entities']
    first_entity = entities[0]
    print('Entity name is: ' + str(first_entity['entity_name']))
    print('Entity value is: ' + str(first_entity['entity_value']))

if __name__ == "__main__":
    setup()
    main()