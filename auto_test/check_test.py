
import os
import json
import argparse
import requests
import re

# Set environment variables
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
    parser = argparse.ArgumentParser(description='Script to process JSON configuration and other related files')
    parser.add_argument('-config', default='./module_info.json', type=str, help='Path to JSON configuration file')#json
    parser.add_argument('-error_file', default='./fix_component_code/check_errors.txt', type=str, help='Path to error file')#error_file
    parser.add_argument('-prompt', default='./auto_test/prompt_check_test.txt', type=str, help='Path to prompt function file')#prompt

    args = parser.parse_args()

    # Read the JSON configuration file
    with open(args.config, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    module_info = config['modules'][0]  
    module_name = module_info['moduleName']  
    paths = module_info['paths']  

    uvm_testbench = paths['uvm_testbench'].format(moduleName=module_name)

    test_file = f"./{uvm_testbench}/{module_name}_test.sv"
    seq_file = f"./{uvm_testbench}/{module_name}_seq.sv"
    seq_item_file = f"./{uvm_testbench}/{module_name}_seq_item.sv"

    with open(test_file, 'r', encoding='utf-8') as testf:
        test_content = testf.read()
    with open(seq_file, 'r', encoding='utf-8') as seqf:
        seq_content = seqf.read()
    with open(seq_item_file, 'r', encoding='utf-8') as trf:
        tr_content = trf.read()
    with open(args.error_file, 'r', encoding='utf-8') as errorf:
        error_content = errorf.read()
    with open(args.prompt, 'r', encoding='utf-8') as promptf:
        p_content = promptf.read()

    prompt1 = (
        f'''{test_content}'''
        f'''{seq_content}'''
        f'''{tr_content}'''
        f'''{error_content}'''
        f'''{p_content}'''
    )


    answer2 = get_request(prompt1)
    print(answer2)

    with open(r"./auto_test/answer2.md", "w", encoding='utf-8') as wf:
        wf.write(answer2)

    corrected_file_marker = f"### Corrected Code"
    if corrected_file_marker in answer2:
        marker_index = answer2.index(corrected_file_marker)
        content_after_marker = answer2[marker_index + len(corrected_file_marker):]

        content = re.findall(
            r'```systemverilog([\s\S]+?)```',
            content_after_marker,
            re.IGNORECASE
        )

        if content:
            output_file_name = f"./{uvm_testbench}/{module_name}_test.sv"
            with open(output_file_name, 'w+', encoding='utf-8') as output_file:
                output_file.write(content[0])
   	   
