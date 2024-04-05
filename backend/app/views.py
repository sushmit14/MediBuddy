from django.shortcuts import render
from adrf.views import APIView
from .models import *
from rest_framework.response import Response
from .serializer import *
from django.http import JsonResponse
from django.http import HttpResponse
from datetime import datetime
import json
import random
from PyPDF2 import PdfReader
from docx import Document
from pptx import Presentation
from openpyxl import load_workbook
from langchain.document_loaders.text import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores.chroma import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
import os
import string
from tqdm import tqdm 
import pickle
from openai import OpenAI
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import cloudinary
import cloudinary.uploader
from django.http import JsonResponse
from rest_framework.views import APIView
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
storeContext = True
class ReactView(APIView):

    serializer_class = ReactSerializer

    def post(self, request):

        serializer = ReactSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


  

class Upload(APIView):
    def post(self, request):
        try:
            
            cloudinary.config( 
            cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), 
            api_key = os.getenv('CLOUDINARY_API_KEY'),
            api_secret = os.getenv('CLOUDINARY_API_SECRET')
            )
            if 'file' not in request.FILES:
                return JsonResponse({"error": "No file found in request."}, status=400)
            
            file_to_upload = request.FILES['file']
            
            # Upload the file to Cloudinary
            uploaded_file = cloudinary.uploader.upload(file_to_upload, use_filename=True,access_mode='public')
            storeContext = False

            # Get the URL of the uploaded file from Cloudinary response
            uploaded_file_url = uploaded_file['secure_url']
            
            
            return JsonResponse({"message": "PDF file uploaded to Cloudinary", "file_url": uploaded_file})
        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=400)
        
class UploadPdf(APIView):
    # index = None  # Class attribute to store the index

    def post(self, request):
        try:
            # Get the uploaded file from the request
            uploaded_file = request.FILES['file']
           
            save_path = "D:\Sushmit Dasgupta\Web Development\django-proj\project\Drug_Disease.txt"  # Change this to the desired path
            

            loader = TextLoader(save_path)
            print("creating index")
            index = VectorstoreIndexCreator(vectorstore_kwargs={ "persist_directory": "D:/Sushmit Dasgupta/Web Development/django-proj/project/app/disease_40k"}).from_loaders([loader])
            print("index created")

            response = JsonResponse({"message": "File uploaded successfully."})
            response["Access-Control-Allow-Origin"] = "http://localhost:3005"
            response["Access-Control-Allow-Credentials"] = "true"
            
            return JsonResponse({"message": "PDF file uploaded, text extracted, and index created successfully"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

queries = []     
class SearchQuery(APIView):
    # def __init__(self):
        # self.queries = []
        # self.q=0
    def clean_text(self,raw_text):
            printable = set(string.printable)
            return ''.join(filter(lambda x: x in printable, raw_text))
    def fun1(self):
        openai_embeddings = OpenAIEmbeddings()
        # if is_disease_to_drug_mapping:           
        persistent_index_path = "D:/Sushmit Dasgupta/Web Development/django-proj/project/app/disease_40k"
        # else:
        #     persistent_index_path = "D:/Sushmit Dasgupta/Web Development/django-proj/project/app/symptoms"
        index = VectorStoreIndexWrapper(vectorstore=Chroma(embedding_function = openai_embeddings, persist_directory=persistent_index_path))
        return index
    
    def fun2(self):
        openai_embeddings = OpenAIEmbeddings()
        persistent_index_path = "D:/Sushmit Dasgupta/Web Development/django-proj/project/app/symptoms"
        index = VectorStoreIndexWrapper(vectorstore=Chroma(embedding_function = openai_embeddings, persist_directory=persistent_index_path))
        return index
    
    def is_string_contained(self,main_string, string_array):
        for string in string_array:
            if string in main_string:
                return True
        return False
    
    def jaccard_similarity(self,word, string):
        word_set = set(word)
        string_set = set(string.split())
        
        intersection = len(word_set.intersection(string_set))
        union = len(word_set.union(string_set))
        
        similarity = intersection / union if union != 0 else 0.0
        return similarity
    
    def preprocess_text(self,text):
    # Tokenize the text
        tokens = word_tokenize(text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [token for token in tokens if token.lower() not in stop_words]
        
        # Lemmatize tokens
       
        lemmatizer = WordNetLemmatizer()
        lemmatized_tokens = [lemmatizer.lemmatize(token.lower()) for token in filtered_tokens]
        
        return lemmatized_tokens

    def wordnet_similarity(self,word, string):
        word_synsets = wn.synsets(word)
        string_synsets = [synset for token in self.preprocess_text(string) for synset in wn.synsets(token)]
        
        max_similarity = 0.0
        
        for word_synset in word_synsets:
            for string_synset in string_synsets:
                similarity = word_synset.path_similarity(string_synset)
                if similarity is not None and similarity > max_similarity:
                    max_similarity = similarity
        
        return max_similarity
            
    def post(self, request):
        try:
            # Clear the queries list and reset q to 0
            queries = []
            print("Query list emptied")
            return HttpResponse("Queries list cleared and q reset to 0")
        except Exception as e:
            return HttpResponse(f"Error clearing queries list and resetting q: {str(e)}")
        
    def get(self, request):
        openai_embeddings = OpenAIEmbeddings()
        
        try:
            query = request.GET.get('query', '')
            word = "symptom"
            similarity = self.jaccard_similarity(word,query)
            print(similarity)
            querypr = query + " If the above query is not a medical question, strictly return only 1."
            medicine_syn = ['medicine','drug','medication','treatment','cure','remedy', 'medicament']
            if self.is_string_contained(query.lower(), medicine_syn): 
                index = self.fun1()
                query += " Provide DrugBank IDs and answer confidently. "
                print("diseases")
            else:
                index = self.fun2()
                query += " Find mild diseases having the given subset of symptoms. If no mild diseases match, only then check other diseases."
                print("symptoms")

           
            print(querypr)
            response = client.chat.completions.create(
                model = 'gpt-3.5-turbo',
                messages = [{'role': 'user', 'content': querypr}],
                # functions = custom_functions,
                # function_call = 'auto'
            )
            if response.choices[0].message.content == '0':
                response = "This query is out of scope for the current chatbot."
                return JsonResponse({"response": response})
            
            query2 = ""
            cnt = 0
            for i in queries:
                # print(i, type(i))
                if cnt %2 == 0:
                    query2 = query2 + "Question: "+i
                else:
                    query2 = query2 + "Answer: "+i
                cnt += 1           
            query2 += query
            # print(query2)
            print(f"Received query: '{query}'")           
            response2 = index.query(query2,llm=ChatOpenAI(model="gpt-4-1106-preview"))
            # print(response)
            if len(queries) == 3:
                queries.pop(0)
                queries.pop(0)
            # print(type(response))
            print("\n\n\n", storeContext, "\n\n\n")
            if(storeContext):
                queries.append(query)
                queries.append(str(self.clean_text(response2)))
            print(queries)
            return JsonResponse({"response": response2})

        except Exception as e:
            print("Exception:", e)
            return JsonResponse({"error": str(e)}, status=400)
        
def testing(self, request):
    print("Testing the Django backend")
    print(request.data)
    return Response({"message": "Testing successful"})