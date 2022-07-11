fake = Faker()
from faker import Faker
from pathlib import Path
import json 
import re
import yaml

with open('sample_data.yml') as file:
    raw_config = yaml.load(file, Loader=yaml.FullLoader)

# TODO - treat int values
# TODO - treat dinamyc yaml structures

def mock_data(text):
    rep = {
            "date":fake.date(), 
            "token": fake.pystr(), 
            "string": fake.sentence(), 
            "name": fake.name(), 
            "float": str(fake.pydecimal(right_digits=2,min_value=0,max_value=100)), 
            "int": str(fake.pyint())
        }
    rep = dict((re.escape(k), v) for k, v in rep.items()) 
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
    
def iterate_dic(data):
    try:
        return {key: (mock_data(data[key]) if type(data[key]) is not list else iterate_list(data[key])) for key in data}
    except Exception as e:
        print("ERROR:",e)
        
def iterate_list(songs):
    try:
        generated_songs = []
        [generated_songs.extend(songs) for _ in range(fake.pyint(2,5))]
        # TODO - better constraint the condition to call the dic iteration
        return [{ key: (mock_data(song[key]) if type(song[key]) is str else iterate_dic(song[key])) for key in song.keys() } for song in generated_songs]
    except Exception as e:
        print("ERROR:",e)

def save_raw(data, file_name):
    base = Path(f"s3/raw/{data['release_date']}")
    jsonpath = base / file_name
    base.mkdir(parents=True,exist_ok=True)
    jsonpath.write_text(json.dumps(data))
    
def create_raw(n_files):
    try:
        mocks = [iterate_dic(raw_config) for _ in range (n_files)]
        for file in mocks:
            save_raw(file, f"album_{file['id']}.json")
    except Exception as e:
        print("ERROR mock:",e)
