from django.shortcuts import render
from django.http import FileResponse
import os
import tempfile
from .utils import pdf_to_word, images_to_pdf, audio_to_text, csv_to_excel
from django.conf import settings
import re
from .forms import EmailUsersForm
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import emailserializer, FileUploadSerializer
from django.db import IntegrityError
import uuid



class imageView(APIView):
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        images = serializer.validated_data.get('images')

        # Ensure system temporary directory is used
        temp_dir = tempfile.gettempdir()
        image_paths = []
        pdf_file_path = os.path.join(temp_dir, f"{uuid.uuid4()}.pdf")

        for image in images:
            try:
                if image.content_type in ["image/jpeg", "image/png"]:
                    unique_filename = f"{uuid.uuid4()}_{image.name}"
                    temp_local_path = os.path.join(temp_dir, unique_filename)
                else: 
                    return Response({"error": f"{image.name} is not a valid image file(.JPEG or .PNG only allowed)."}, status=status.HTTP_400_BAD_REQUEST)
        
                with open(temp_local_path, 'wb+') as temp_file:
                    for chunk in image.chunks():
                        temp_file.write(chunk)
                image_paths.append(temp_local_path)
            except Exception as e:
                return Response({'error': f'{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            # Convert Images to PDF
            images_to_pdf(image_paths, pdf_file_path)

            # download PDF
            pdf_file = open(pdf_file_path, 'rb')

            response = FileResponse(
                pdf_file, content_type='application/pdf'
                )
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(pdf_file_path)}'

            return response
        except Exception as e:
                errorp_message = f'Error converting Images: {str(e)}'
                return Response({'error': errorp_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
        finally:
            # Cleanup
            for path in image_paths:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except PermissionError:
                        pass

            if "pdf_file_path" in locals() and os.path.exists(pdf_file_path):
                try:
                    os.remove(pdf_file_path)
                except PermissionError:
                    pass


class converterView(APIView):
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data.get('file')
        if uploaded_file.content_type == 'application/pdf':
            pdf_file = serializer.validated_data['file']
            
            # Create temporary paths
            temp_dir = tempfile.gettempdir()
            temp_pdf_path = os.path.join(temp_dir, pdf_file.name)
            docx_path = temp_pdf_path.replace('.pdf', '.docx')

            # Save uploaded PDF to temp location
            with open(temp_pdf_path, 'wb+') as temp_file:
                for chunk in pdf_file.chunks():
                    temp_file.write(chunk)

            try:

                # Convert PDF to DOCX
                pdf_to_word(temp_pdf_path, docx_path)

                # download docx
                docx_file = open(docx_path, 'rb')

                response = FileResponse(
                    docx_file, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(docx_path)}'

                return response
            except Exception as e:
                errorp_message = f'Error converting PDF: {e}'
                return Response({'error': errorp_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

            finally:
                # Clean up temporary files
                for file_path in [temp_pdf_path, docx_path]:
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except PermissionError:
                            pass  # Ignore if file is still in use


        elif uploaded_file.content_type == 'text/csv':
            csv_file = serializer.validated_data['file']
            
            # Create temporary paths
            temp_dir = tempfile.gettempdir()
            temp_csv_path = os.path.join(temp_dir, csv_file.name)
            excel_path = temp_csv_path.replace('.csv', '.xlsx')

            # Save uploaded csv to temp location
            with open(temp_csv_path, 'wb+') as temp_file:
                for chunk in csv_file.chunks():
                    temp_file.write(chunk)

            try:

                # Convert CSV to xlsx
                csv_to_excel(temp_csv_path, excel_path)

                # download xlsx
                excel_file = open(excel_path, 'rb')

                response = FileResponse(
                    excel_file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(excel_path)}'

                return response
            
            
            except Exception as e:
                errorp_message = f'Error converting CSV: {e}'
                return Response({'error': errorp_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            

            finally:
                # Clean up temporary files
                for file_path in [temp_csv_path, excel_path]:
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except PermissionError:
                            pass  # Ignore if file is still in use
        
    
        elif uploaded_file.content_type == 'audio/mpeg' or uploaded_file.content_type == 'audio/wav' or uploaded_file.content_type == 'audio/webm':
            audio = serializer.validated_data['file']
        
            #temperary directory
            temp_dir = tempfile.gettempdir()
            audio_path = os.path.join(temp_dir, audio.name)

            # Save audio to local temporary directory
            with open(audio_path, 'wb+') as destination:
                for chunk in audio.chunks():
                    destination.write(chunk)
                    audio_path = destination.name
                
                
            # Convert audio to text
            audio_text = audio_to_text(audio_path)
        
            # Clean up local audio file
            os.remove(audio_path)
            return Response({'result': audio_text}, status=status.HTTP_200_OK)

        else:
            return Response({'error': f'{uploaded_file.content_type} unsuppoorted.'}, status=status.HTTP_400_BAD_REQUEST)


class emailSubscribeView(APIView):
    serializer_class = emailserializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
            try:
                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                email = request.data.get('email')
                subject = 'Welcome to our newsletter!'
                message = f'Hi {email}, welcome to our newsletter. You will be receiving updates on our products and services'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email]
                send_mail(subject, message, email_from, recipient_list, fail_silently=False)
            except IntegrityError:
                return Response({'detail':'Looks you have subscribed before.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    

