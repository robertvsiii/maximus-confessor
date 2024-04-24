from openai import OpenAI
from tesserae.db import TessMongoConnection
from tesserae.db.entities import Translation

unit_type = 'line'
model = "gpt-4-turbo"

# Initialize openAI client and database connection
with open('api_key.txt','r') as f:
    api_key = f.read()
client = OpenAI(api_key=api_key)
chat_history = [{"role": "system", "content": "You are a Byzantine Greek to English translator."}]
connection = TessMongoConnection('127.0.0.1', 27017, None, None, db='maximus')

def main():
    title = input("Title: ")
    text_id = connection.find('texts',title=title)[0].id

    last_translated = connection.aggregate('translations',[{'$match': {'text': text_id, 'unit_type': unit_type}}, 
                                               {"$project": {"_id": 0, "index": 1, "tags": 1}}],
                                              encode=False)
    start_tag = input("Starting tag: ").strip()
    if start_tag:
        current_index = connection.find('units',unit_type=unit_type,text=text_id,tags=start_tag)[0].index
    else:
        if len(last_translated) > 0:
            print('Starting from last translation at '+last_translated[-1].tags[0])
            current_index = last_translated[-1].index
        else:
            print('Starting translation from the beginning')
            current_index = 0

    translating = True
    while translating:

        current_unit = connection.find('units',text=text_id,unit_type=unit_type,index=current_index)[0]
        chat_history.append({"role": "user", "content": current_unit.snippet})

        response = client.chat.completions.create(model=model,messages=chat_history)
        machine_trans = response['choices'][0]['message']['content']
        print("Latest translation result: ")
        print(machine_trans)

        accept = input("Accept translation (y/n)? ")
        if accept == 'y':
            final_model = model
            final_trans = machine_trans
        else:
            final_model = 'RAM'
            final_trans = input("Corrected translation (s to skip): ")

        if final_trans != 's':
            chat_history.append({"role": "assistant", "content": final_trans})
            notes = input("Translation notes: ")
            translation = Translation(text=text_id,snippet=user_trans,notes=notes.strip(),model=final_model,index=current_index,tags=current_unit.tags)
            out = connection.insert('translations',translation)
        else:
            chat_history = chat_history[:-1]

        current_index += 1
        translating = input("Continue? (blank to stop) ").strip()


if __name__ == "__main__":
    main()