
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
    parser.add_argument('-config', default='./module_info.json', type=str, help='Path to JSON configuration file')#json:dut
    parser.add_argument('-func', default='./auto_function/{module_name}_function.txt', type=str, help='Path to function file')#function
    parser.add_argument('-testc', default='./auto_testcase/{module_name}_testcase.txt', type=str, help='Path to testcase file')#testcase
    parser.add_argument('-tr_file', default='./auto_seq_item/{module_name}_seq_item.sv', type=str, help='Path to transaction file')#transcation
    parser.add_argument('-mon_file', default='./auto_monitor/{module_name}_monitor.sv', type=str, help='Path to mon file')#mon
    parser.add_argument('-prompt', default='./auto_seq/prompt_seq.txt', type=str, help='Path to prompt function file')#prompt
    parser.add_argument('-prompt_event', default='./auto_seq/prompt_event_seq.txt', type=str, help='Path to event prompt function file')#event prompt

    args = parser.parse_args()

    # Read the JSON configuration file
    with open(args.config, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    module_info = config['modules'][0]  
    module_name = module_info['moduleName']  # Module name
    paths = module_info['paths']  # Path information
    print(f"Extracted module_name in auto_seq: {module_name}")

    spec_path = paths['spec'].format(moduleName=module_name)
    func_file_path = args.func.format(module_name=module_name)
    testc_file_path = args.testc.format(module_name=module_name)
    tr_file_path = args.tr_file.format(module_name=module_name)
    mon_file_path = args.mon_file.format(module_name=module_name)

    with open(spec_path, 'r', encoding='utf-8') as specf:
        spec_content = specf.read()
    with open(func_file_path, 'r', encoding='utf-8') as funcf:
        func_content = funcf.read()
    with open(testc_file_path, 'r', encoding='utf-8') as testcf:
        testc_content = testcf.read()
    with open(tr_file_path, 'r', encoding='utf-8') as trf:
        tr_content = trf.read()
    with open(mon_file_path, 'r', encoding='utf-8') as monf:
        mon_content = monf.read()
    
    if 'uvm_event' in mon_content:
        prompt_file = args.prompt_event
        print("Using event sequence prompt file")
    else:
        prompt_file = args.prompt
        print("Using normal sequence prompt file")
    
    with open(prompt_file, 'r', encoding='utf-8') as promptf:
        p_content = promptf.read()

    prompt1 = (
        f'''{spec_content}'''
        f'''{func_content}'''
        f'''{testc_content}'''
        f'''{tr_content}'''
        f'''{mon_content}'''
        f'''{p_content}'''
    )

    answer1 = get_request(prompt1)
    print(answer1)

    with open(r"./auto_seq/answer1.md", "w", encoding='utf-8') as wf:
        wf.write(answer1)

    content = re.findall(
        r'```systemverilog([\s\S]+?)```',
        answer1,
        re.IGNORECASE
    )
    if content:
        output_file_name = f"./auto_seq/{module_name}_seq.sv"
        with open(output_file_name, 'w+', encoding='utf-8') as output_file:
            output_file.write(content[0])
