from django.http import HttpResponse
from django.db.models import Q

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import status  
from rest_framework.response import Response  
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FileUploadParser
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from .serializers import UserSerializer, DocumentSerializer
from .models import CustomUser, Documents, DocAcess




#================================= Create a new User
class RegistrationUserView(APIView):

    @swagger_auto_schema(request_body=UserSerializer,responses={201: "Created Response Description"}) 
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = CustomUser.objects.get(username=request.data.get('username'))
            user.set_password(request.data.get('password'))
            user.save()
            token = Token.objects.create(user=user)
            return Response({
                "token": token.key,
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




#======================================= User login with token
class LoginUserView(APIView):

    @swagger_auto_schema(request_body=UserSerializer,responses={201: "Created Response Description"})
    def post(self, request):
        try:
            user = CustomUser.objects.get(username=request.data.get('username'))
            if not user.check_password(request.data.get('password')):
                return Response({"details": "Not found the user"}, status=status.HTTP_404_NOT_FOUND)
            token, create = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(instance=user)
            return Response({
                "token": token.key,
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as E:
            return Response({"details":"User Not found"}, status=status.HTTP_404_NOT_FOUND)
        


#===================================== Document get and create
class DocumentsView(APIView):
    authentication_classes = [ SessionAuthentication,TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (FileUploadParser,)

    @swagger_auto_schema(responses={200: DocumentSerializer(many=True)})
    def get(self, request):
        documents = Documents.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    

    @swagger_auto_schema(request_body=DocumentSerializer,esponses={201: "Created Response Description"})
    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


#===================================== Documnent CRUD
class DocumentCRUD(APIView):
    authentication_classes = [SessionAuthentication,TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def target_document(self, pk):
        try:
            return Documents.objects.get(id=pk)
        except Exception as E:
            return None
        
    @swagger_auto_schema(responses={200: DocumentSerializer(many=True)})
    def get(self, request, pk):
        document = self.target_document(pk)
        serializer = DocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_302_FOUND)
    
    @swagger_auto_schema(request_body=DocumentSerializer,esponses={201: "Created Response Description"})
    def put(self, request, pk):
        document = self.target_document(pk)
        print(request.user)
        if document.creator != request.user:
            return Response("No permission to update.", status=status.HTTP_403_FORBIDDEN)
        serializer = DocumentSerializer(document, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @swagger_auto_schema(responses={204: "No Content"})
    def delete(self, request, pk):
        document = self.target_document(pk)
        if document is None:
            return Response({
                "status": "Content Not Found!"
            },status=status.HTTP_404_NOT_FOUND)
        if document.creator != request.user:
            return Response("No permission to delete.", status=status.HTTP_403_FORBIDDEN)

        document.delete()
        return Response({
            "status": "Content Deleted Successfully"
        },status=status.HTTP_204_NO_CONTENT)


#================================================= Document Download
class DocumentDownload(APIView):
    authentication_classes = [SessionAuthentication,TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: "Ok"})
    def get(self, request, pk):
        try:
            target_doc = Documents.objects.get(id=pk)
            if target_doc.creator == request.user or target_doc.share_with.filter(id=request.user.id).exists() or request.user.is_staff:
                doc_path = target_doc.file.path
                with open(doc_path, 'rb') as file:
                    response = HttpResponse(file.read(), content_type='application/octet-stream')
                    response['Content-Disposition'] = f'attachment; filename="{target_doc.title}.{target_doc.format}"'
                    return response
            else:
                try:
                    access = DocAcess.objects.get(document=target_doc,  user=request.user)
                    if access.editable:
                        doc_path = target_doc.file.path
                        with open(doc_path, 'rb') as file:
                            response = HttpResponse(file.read(), content_type='application/octet-stream')
                            response['Content-Disposition'] = f'attachment; filename="{target_doc.title}.{target_doc.format}"'
                            return response
                    else:
                        return Response({"status": "Reserved"}, status=status.HTTP_306_RESERVED)
                except Exception as E:
                    return Response({"status": "bad request"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as E:
            return Response({"status": "Content Not Found!"}, status=status.HTTP_404_NOT_FOUND)
        

#================================================== Document Share View
class DocumentShareView(APIView):
    authentication_classes = [SessionAuthentication,TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=DocumentSerializer,esponses={201: "Created Response Description"})
    def post(self, request, pk):
        doc = Documents.objects.get(id=pk)
        if doc.creator != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        users = request.data.get('users', [])
        users = CustomUser.objects.filter(id__in=users)
        doc.share_with.add(*users)
        doc.save()
        return Response({"status": "Docutment Shared"}, status=status.HTTP_200_OK)


#================================================== Document search view
class DocumentSearchView(APIView):
    authentication_classes = [SessionAuthentication,TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(responses={200: DocumentSerializer(many=True)})
    def get(self, request):
        query = request.query_params.get('q', '')
        all_docs = Documents.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(format__icontains=query) |
            Q(created_at__icontains=query),
            creator=request.user
        )
        serializer = DocumentSerializer(all_docs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)