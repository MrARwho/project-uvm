
import os
import json
import argparse
import requests

os.environ["GEMINI_API_KEY"] = "AIzaSyDQgrrN0ty29wqsz2Xv0jKlF_JGdMwRVP8"

model = "gemini-2.5-pro"


def get_request(prompt, temperature=0.2, max_new_tokens=4096, model=model):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={os.environ['GEMINI_API_KEY']}"
    
    query = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_new_tokens
        }
    }

    response = requests.post(url, json=query)
    result = response.json()

    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return result

if __name__ == '__main__':
    
	# Use argparse to get the JSON configuration file path
    parser = argparse.ArgumentParser(description='Script for handling JSON configuration and other related files')
    parser.add_argument('-config', default='./module_info.json', type=str, help='Path to JSON configuration file') #json
    parser.add_argument('-exfun', default='./auto_function/example_function.txt', type=str, help='Path to example function file') #example_function
    parser.add_argument('-prompt', default='./auto_function/prompt_function.txt', type=str, help='Path to prompt function file')  #prompt

    args = parser.parse_args()

    # Read the JSON configuration file
    with open(args.config, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    module_info = config['modules'][0] 
    module_name = module_info['moduleName']  # Module name
    paths = module_info['paths']  # Path information
    print(f"Extracted module_name in auto_function: {module_name}")

    spec_path = paths['spec'].format(moduleName=module_name)

    # Read file contents
    with open(spec_path, 'r', encoding='utf-8') as spec_file:
        spec_content = spec_file.read()
    with open(args.exfun, 'r', encoding='utf-8') as exfun_file:
        ex_content = exfun_file.read()
    with open(args.prompt, 'r', encoding='utf-8') as prompt_file:
        p_content = prompt_file.read()

    # Concatenate prompt
    prompt1 = (
        f'''{spec_content}'''
        f'''{ex_content}'''
        f'''{p_content}'''
    )

    answer1 = get_request(prompt1)
    print(answer1)


    output_file_name = f"./auto_function/{module_name}_function.txt"
    with open(output_file_name, 'w+', encoding='utf-8') as output_file:
        output_file.write(answer1)

