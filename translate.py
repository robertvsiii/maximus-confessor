from openai import OpenAI
import anthropic
from tesserae.db import TessMongoConnection
from tesserae.db.entities import Translation

def main():
    api = 'anthropic'
    unit_type = 'line'
    cutoff = .5

    connection = TessMongoConnection('127.0.0.1', 27017, None, None, db='maximus')

    if api == 'openai':
        model = "gpt-4-turbo"
        with open('api_key.txt','r') as f:
            api_key = f.read()
        client = OpenAI(api_key=api_key)
        client.messages = client.chat.completions
        chat_history = [{"role": "system", "content": "You are a Byzantine Greek to English translator."}]
        kwargs = {'model':model}
    elif api =='anthropic':
        model = "claude-3-haiku-20240307"
        with open('api_key_anth.txt','r') as f:
            api_key = f.read()
        client = anthropic.Anthropic(api_key=api_key)
        chat_history = []
        kwargs = {'model': model, 'system': "You are a Byzantine Greek to English translator.", 'max_tokens': 1024}

    title = input("Title: ")
    text_id = connection.find('texts',title=title)[0].id

    #Load and sort existing translations
    saved_translations = connection.find('translations',text=text_id,unit_type=unit_type)
    trans_dict = {saved_translations[k].index: saved_translations[k] for k in range(len(saved_translations))}
    trans_idx = list(trans_dict.keys())
    trans_idx.sort()
    saved_translations = [trans_dict[i] for i in trans_idx]

    #Append last five to chat history
    for translation in saved_translations[-5:]:
        original = connection.find('units',text=text_id,unit_type=unit_type,index=translation.index)[0]
        chat_history.append({"role": "user", "content": original.snippet})
        chat_history.append({"role": "assistant", "content": translation.snippet})

    start_tag = input("Starting tag: ").strip()
    if start_tag:
        current_index = connection.find('units',unit_type=unit_type,text=text_id,tags=start_tag)[0].index
    else:
        if len(saved_translations) > 0:
            print('Starting from last translation')
            current_index = trans_idx[-1]+1
        else:
            print('Starting translation from the beginning')
            current_index = 0

    translating = True
    while translating:

        current_unit = connection.find('units',text=text_id,unit_type=unit_type,index=current_index)[0]
        chat_history.append({"role": "user", "content": current_unit.snippet})
        context = connection.find('matches',source_unit = current_unit.id)

        print(title+' '+current_unit.tags[0])
        print(current_unit.snippet)

        response = client.messages.create(messages=chat_history,**kwargs)
        if api == 'opaenai':
            machine_trans = response.choices[0].message.content
        elif api == 'anthropic':
            machine_trans = response.content[0].text
        with open('temp.txt', 'w') as f:
            f.write(machine_trans)
        print('---')
        print('Possible references: ')
        for reference in context:
            if reference.score > cutoff:
                ref_unit = connection.find('units',_id=reference.target_unit)[0]
                ref_title = connection.find('texts',_id=ref_unit.text)[0].title
                print(ref_title+' '+ref_unit.tags[0]+' (score '+str(reference.score)+')')
                print(ref_unit.snippet)
                print(' ')
        print('---')

        correct = input("Corrected translation (y/n)? ")
        if correct == 'n':
            final_model = model
        else:
            final_model = 'RAM'

        with open('temp.txt', 'r') as f:
            final_trans = f.read()


        chat_history.append({"role": "assistant", "content": final_trans})
        notes = input("Translation notes: ")
        translation = Translation(unit=current_unit.id,text=text_id,snippet=final_trans,notes=notes.strip(),model=final_model,index=current_index,tags=current_unit.tags,unit_type=unit_type)
        out = connection.insert(translation)

        current_index += 1
        translating = input("Continue? (blank to stop) ").strip()


if __name__ == "__main__":
    main()
