import os, json

DATA_FILE = "notes.json"

# == LOAD NOTES ==
def load_notes():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# == SAVE NOTES ==
def save_notes(data):
    with open(DATA_FILE, "w", encoding="utf=8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# == DELETE NOTES ==
def delete_notes(user_id: int, index: int):
    data = load_notes()
    uid = str(user_id)

    if uid in data and 0 <= index < len(data[uid]):
        data[uid].pop(index)
        save_notes(data)
        return True

    return False

# == ADD NOTES ==
def add_notes(user_id: int, note: str):
    uid = str(user_id)
    data = load_notes()

    if uid not in data:
        data[uid] = []
    
    data[uid].append(note)
    save_notes(data)

#  == GET USER NOTES ==
def get_user_notes(user_id: int):
    data = load_notes()
    return data.get(str(user_id), [])

# == EDIT NOTES ==
def edit_notes(user_id: int, index: int, new_notes: str):
    data = load_notes()
    uid = str(user_id)

    if uid in data and 0 <= index < len(data[uid]):  
        data[uid][index] = new_notes
        save_notes(data) 
        return True

    return False

