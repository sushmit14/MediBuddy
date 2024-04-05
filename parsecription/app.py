import csv
from time import time
import tabula
import fitz  # PyMuPDF, imported as fitz for backward compatibility reasons
from PIL import Image
import pytesseract
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
# import mysql.connector
# import pyfiglet
# import os
# import openai
import json
# from langchain.agents import tool
from pydantic import BaseModel, Field
# from langchain.tools.render import format_tool_to_openai_function
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
# from langchain.schema.output_parser import StrOutputParser
# from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
# from langchain.prompts import HumanMessagePromptTemplate
# from langchain_core.messages import SystemMessage
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from typing import List
from pydantic import BaseModel, Field
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.chat_models import ChatOpenAI
from typing import Optional
import re
import torch
from transformers import BertTokenizer, BertForTokenClassification
from utils import *
import os 

os.environ['OPENAI_API_KEY'] = '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'
'''

file_path = "Report.pdf"
doc = fitz.open(file_path)  # open document
i=0
for page in doc:
    pix = page.get_pixmap()  # render page to an image
    pix.save(f"page_{i}.png")
    i+=1
'''
start_time_str = "07:00"
end_time_str = "21:00"
mid_time_str = "13:00"

# pdf_path = 'P1.pdf'


# # LLM CODE

# model = ChatOpenAI()


# functions = [
#     convert_pydantic_to_openai_function(MedInfo),
#     convert_pydantic_to_openai_function(PatientInfo),
#     # convert_pydantic_to_openai_function(DoctorInfo),
#     convert_pydantic_to_openai_function(OtherInfo)
# ]
# parser = model.bind(functions=functions)

# # BERT FOR NER
# tokenizer = BertTokenizer.from_pretrained(
#     'medical-ner-proj/bert-medical-ner-proj')
# model = BertForTokenClassification.from_pretrained(
#     'medical-ner-proj/bert-medical-ner-proj')
# # NER Labels
# id2label = {
#     "0": "B_person",
#     "1": "B_problem",
#     "2": "B_pronoun",
#     "3": "B_test",
#     "4": "B_treatment",
#     "5": "I_person",
#     "6": "I_problem",
#     "7": "I_test",
#     "8": "I_treatment",
#     "9": "O"
# }


# def filterLines(textLines):
#     result = []
#     for textLine in textLines:
#         tokenized_input = tokenizer(textLine, return_tensors="pt")
#         outputs = model(**tokenized_input)
#         # Process the outputs to get NER predictions
#         predictions = torch.argmax(outputs.logits, dim=2)
#         for i in range(len(predictions[0])):
#             # print("Token: ", textLine[i], " Label: ",id2label[str(predictions[0][i].item())])
#             if id2label[str(predictions[0][i].item())] == 'B_test' or id2label[str(predictions[0][i].item())] == 'B_treatment':
#                 result.append(textLine)
#                 # print(textLine)
#                 break
#     return result


class Request(BaseModel):
    url: str
    isPrescription: bool


parser = ParserModel()
nerFilter = NERFilter()
explainerModel = ExplainerModel()
app = FastAPI()


@app.get("/")
def welcome():
    return "Welcome to Parsecription API"


@app.get("/test")
def test():
    return {"Status": "Running"}


@app.post("/parse-prescription")
def parsePrescription(R: Request):
    start = time()
    url = R.url
    # print(url)parsescription\P1.pdf
    print(url)
    destination_path = 'parsescription/prescriptiondownload.pdf'
    download_pdf(url, destination_path)
    text = pdf_to_text(destination_path)

    # Define the replacement patterns
    patterns = {'tab': 'tablet', 'cap': 'capsule',
                "TAB": "tablet", "Cap": "capsule", "Tab": "tablet"}
    # Create a regular expression pattern for matching the keys in the dictionary
    pattern = re.compile(r'\b(?:' + '|'.join(re.escape(key)
                         for key in patterns.keys()) + r')\b')
    # Replace the matched patterns with their corresponding values
    text = pattern.sub(lambda match: patterns[match.group(0)], text)
    textSplit = splitter(text)

    filteredTextLines = nerFilter.filter(textSplit)
    # print(filteredTextLines)
    if (len(filteredTextLines) == 0):
        # print("Not a Medical Document")
        return json.dumps({"Error": "Invalid Document"})
    print("Parsing...")
    ParsedResult = {'MedInfo': [], 'PatientInfo': []}
    # print(filteredTextLines)
    for i in filteredTextLines:
        response = parser.invoke(i)
        # print(response)
        if (response.content == ''):
            outer_dict = response.additional_kwargs['function_call']
            arguments_dict = json.loads(outer_dict['arguments'])
            outer_dict['arguments'] = arguments_dict
            try:
                if (outer_dict['name'] == 'MedInfo' and arguments_dict['frequency']):
                    print("Record Type: ", outer_dict['name'])
                    print(outer_dict['arguments'])
                    print()
                    ParsedResult[outer_dict['name']].append(
                        outer_dict['arguments'])
                elif (outer_dict['name'] == 'PatientInfo'):
                    print("Record Type: ", outer_dict['name'])
                    print(outer_dict['arguments'])
                    print()
                    ParsedResult[outer_dict['name']].append(
                        outer_dict['arguments'])

            except:
                if (outer_dict['name'] == 'PatientInfo'):
                    print("Record Type: ", outer_dict['name'])
                    print(outer_dict['arguments'])
                    print()
                    ParsedResult[outer_dict['name']].append(
                        outer_dict['arguments'])

    # Exit if invalid
    if ParsedResult['MedInfo'] == [] and ParsedResult['PatientInfo'] == []:
        print("Not a Medical Document")
        ParsedResult = {"Error": "Invalid Document"}
        end = time()
        ParsedResult['processingTime'] = end-start
        # print("YAY")
        return json.dumps(ParsedResult)
    # return json.dumps(ParsedResult)
    print("Medicine Consumption Times: ")
    for i in range(len(ParsedResult['MedInfo'])):
        # print("Entry")
        # print(ParsedResult['MedInfo'][i])
        freq = ParsedResult['MedInfo'][i]["frequency"]
        # print(freq)
        L = generate_timestamps(
            start_time_str=start_time_str, end_time_str=end_time_str, mid_time_str=mid_time_str, n=freq)
        # print("Entry2")
        print("Medicine: ", ParsedResult['MedInfo'][i]['name'], end=' ')
        print("Estimated Times: ", L)
        print()
        ParsedResult['MedInfo'][i]['timestamps'] = L

    try:
        weight = {}
        height = {}
        bp = {}
        bloodSugar = {}
        pulseRate = {}
        for i in ParsedResult['PatientInfo']:
            try:
                height['val0'] = i['height']
            except:
                pass
            try:
                weight['val0'] = i['weight']
            except:
                pass
            try:
                bp['val0'] = i['bp_systolic']
                bp['val1'] = i['bp_diastolic']
            except:
                pass
            try:
                bloodSugar['val0'] = i['blood_sugar_pp']
                bloodSugar['val1'] = i['blood_sugar_fasting']
            except:
                pass
            try:
                pulseRate['val0'] = i['heart_rate']
            except:
                pass

        ParsedResult['weight'] = weight
        ParsedResult['height'] = height
        ParsedResult['pulseRate'] = pulseRate
        ParsedResult['bp'] = bp
        ParsedResult['bloodSugar'] = bloodSugar
    except:
        pass

    end = time()
    ParsedResult['processingTime'] = end-start
    # print("YAY")
    return json.dumps(ParsedResult)


@app.post("/parse-report")
def parseReport(R: Request):
    start = time()
    url = R.url
    destination_path = 'parsecription/reportdownload.pdf'
    download_pdf(url, destination_path)
    ''' Table Parser'''
    filename = 'CSVgg.csv'
    dfs = tabula.read_pdf(destination_path, pages='all', stream=True)
    f = open(filename, 'w')
    for df in dfs:
        df.to_csv(f, index=False)
        f.write("\n")
    f.close()

    # download_pdf(url, destination_path)
    # text = pdf_to_text(destination_path)
    # Check Validity
    # textSplit = splitter(text)
    # for i in textSplit:
    #     print(i)
    # filteredTextLines = nerFilter.filter(textSplit)
    # print(filteredTextLines)
    # if (len(filteredTextLines) == 0):
    # print("Not a Medical Document")
    # return json.dumps({"Error": "Invalid Document"})
    # ParsedResult = {'MedInfo': [], 'PatientInfo': [], 'MedicalConditions': []}
    # # print(filteredTextLines)
    # print(filteredTextLines)
    # for i in filteredTextLines:
    #     response = parser.invoke(i)
    #     # print(response)
    #     if (response.content == ''):
    #         outer_dict = response.additional_kwargs['function_call']
    #         arguments_dict = json.loads(outer_dict['arguments'])
    #         outer_dict['arguments'] = arguments_dict
    #         try:
    #             if (outer_dict['name'] == 'MedInfo' and arguments_dict['frequency']):
    #                 print("Record Type: ", outer_dict['name'])
    #                 print(outer_dict['arguments'])
    #                 print()
    #                 ParsedResult[outer_dict['name']].append(
    #                     outer_dict['arguments'])
    #             elif (outer_dict['name'] == 'PatientInfo'):
    #                 print("Record Type: ", outer_dict['name'])
    #                 print(outer_dict['arguments'])
    #                 print()
    #                 ParsedResult[outer_dict['name']].append(
    #                     outer_dict['arguments'])
    #             # elif (outer_dict['name'] == 'TestResult'):
    #             #     print("Record Type: ", outer_dict['name'])
    #             #     print(outer_dict['arguments'])
    #             #     print()
    #             #     ParsedResult[outer_dict['name']].append(
    #             #         outer_dict['arguments'])
    #             # elif (outer_dict['name'] == 'MedicalConditions'):
    #             #     print("Record Type: ", outer_dict['name'])
    #             #     print(outer_dict['arguments'])
    #             #     print()
    #             #     ParsedResult[outer_dict['name']].append(
    #             #         outer_dict['arguments'])

    #         except:
    #             if (outer_dict['name'] == 'PatientInfo'):
    #                 print("Record Type: ", outer_dict['name'])
    #                 print(outer_dict['arguments'])
    #                 print()
    #                 ParsedResult[outer_dict['name']].append(
    #                     outer_dict['arguments'])
    # print(ParsedResult)
    # Exit if invalid
    # if ParsedResult['MedInfo'] == [] and ParsedResult['PatientInfo'] == [] and ParsedResult['MedicalConditions'] == []:
    #     print("Not a Medical Document")
    #     ParsedResult = {"Error": "Invalid Document"}
    #     end = time()
    #     ParsedResult['processingTime'] = end-start
    #     # print("YAY")
    #     return json.dumps(ParsedResult)

    ParsedResult = {'MedInfo': [], 'PatientInfo': [], 'TestResult': []}
    # Process the Table
    with open('CSVgg.csv', newline='') as csvfile:
        # Create a CSV reader object
        csv_reader = csv.reader(csvfile)
        # Iterate over each row in the CSV file
        for row in csv_reader:
            # print(row)
            row = ','.join(row)
            response = parser.invoke(row)
            # print(response)
            if (response.content == ''):
                try:
                    outer_dict = response.additional_kwargs['function_call']
                    arguments_dict = json.loads(outer_dict['arguments'])
                    # print(outer_dict['name'])
                    outer_dict['arguments'] = arguments_dict

                    if (outer_dict['name'] == 'MedInfo' and arguments_dict['frequency']):
                        print("Record Type: ", outer_dict['name'])
                        print(outer_dict['arguments'])
                        print()
                        ParsedResult[outer_dict['name']].append(
                            outer_dict['arguments'])
                    elif (outer_dict['name'] == 'PatientInfo'):
                        print("Record Type: ", outer_dict['name'])
                        print(outer_dict['arguments'])
                        print()
                        ParsedResult[outer_dict['name']].append(
                            outer_dict['arguments'])
                    elif (outer_dict['name'] == 'TestResult'):

                        if (outer_dict['arguments']['flag'] == 'Abnormal'):
                            print("Record Type: ", outer_dict['name'])
                            print(outer_dict['arguments'])
                            print()
                            ParsedResult[outer_dict['name']].append(
                                outer_dict['arguments'])
                    # elif (outer_dict['name'] == 'MedicalConditions'):
                    #     print("Record Type: ", outer_dict['name'])
                    #     print(outer_dict['arguments'])
                    #     print()
                    #     ParsedResult[outer_dict['name']].append(
                    #         outer_dict['arguments'])

                except:
                    pass
                    # if (outer_dict['name'] == 'PatientInfo'):
                    #     print("Record Type: ", outer_dict['name'])
                    #     print(outer_dict['arguments'])
                    #     print()
                    #     ParsedResult[outer_dict['name']].append(
                    #         outer_dict['arguments'])

    # result = explainerModel.invoke(text)
    # print("Summary: ")
    # print(text)
    end = time()
    # print("YAY")
    if (ParsedResult['TestResult'] == []):
        print("Not a Medical Document")
        return json.dumps({
            "Error": "Not a Medical Document",
            "processingTime": end-start
        })
    file_path = 'output.txt'
    # Convert dictionary to JSON-formatted string
    json_string = json.dumps(ParsedResult, indent=4)
    # Write JSON-formatted string to text file
    with open(file_path, 'w') as text_file:
        text_file.write(json_string)
    return json.dumps({
        "Results": ParsedResult['TestResult'],
        "processingTime": end-start
    })

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows requests from any origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
