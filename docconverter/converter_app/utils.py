from pdf2docx import Converter
from docx import Document
import os
import img2pdf
import pandas as pd
import speech_recognition as sr
from pydub import AudioSegment


# def powerpoint_to_pdf(input_ppt_path, output_pdf_path):
#     pass


def images_to_pdf(input_images_path, output_pdf_path):
    
    # Convert and save as a single PDF
    with open(output_pdf_path, "wb") as f:
        f.write(img2pdf.convert(input_images_path))


def csv_to_excel(input_csv_path, output_excel_path):

    # Read the CSV file and write it to an Excel file
    df = pd.read_csv(input_csv_path)
    df.to_excel(output_excel_path, index=False)


def pdf_to_word(input_pdf_path, output_docx_path):

    # Converts a PDF to a Word document using docling.

    cv = Converter(input_pdf_path)
    cv.convert(output_docx_path, start=0, end=None)
    cv.close()


def audio_to_text(audio_path):
    r = sr.Recognizer()

    # Initialize an empty string to store the recognized text
    recognized_text = ""

    # Convert audio to WAV format if needed
    audio_format = audio_path.split('.')[-1]
    if audio_format != 'wav':
        sound = AudioSegment.from_file(audio_path)
        audio_path_wav = audio_path.replace(f'.{audio_format}', '.wav')
        sound.export(audio_path_wav, format='wav')
        audio_path = audio_path_wav
        
    with sr.AudioFile(audio_path) as source:
        # Calculate the duration of the audio file
        audio_duration = source.DURATION

        # Process the audio in chunks of 60 seconds
        for i in range(0, int(audio_duration), 60):
            audio = r.record(source, duration=60, offset=i)
            try:
                text = r.recognize_google(audio)
                recognized_text += text + " "
            except sr.UnknownValueError:
                # Skip unintelligible chunks
                recognized_text += "*"

    return recognized_text.strip()

