from django.shortcuts import get_object_or_404, render

from masters.filters import EventFilter

# Create your views here.


from .models import *
from vendor.models import *
from .forms import *
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from .serializers import *

from users.permissions import *

from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count




      


@login_required(login_url='login_admin')
def add_event(request):

    if request.method == 'POST':

        forms = event_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_event')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_event.html', context)
    
    else:

        forms = event_Form()

        context = {
            'form': forms
        }
        return render(request, 'add_event.html', context)

        

@login_required(login_url='login_admin')
def update_event(request, event_id):

    if request.method == 'POST':

        instance = event.objects.get(id=event_id)

        forms = event_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_event')
        else:
            print(forms.errors)
    
    else:

        instance = event.objects.get(id=event_id)
        forms = event_Form(instance=instance)

        context = {
            'form': forms
        }
        return render(request, 'add_event.html', context)

        

@login_required(login_url='login_admin')
def delete_event(request, event_id):

    event.objects.get(id=event_id).delete()

    return HttpResponseRedirect(reverse('list_event'))


@login_required(login_url='login_admin')
def list_event(request):

    data = event.objects.all()
    context = {
        'data': data
    }
    return render(request, 'list_event.html', context)


from django.http import JsonResponse

class get_event(ListAPIView):
    queryset = event.objects.all()
    serializer_class = event_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventFilter  # enables filtering on all fields


    def get_queryset(self):
        return event.objects.filter(start_date__gte=now()).order_by('start_date')


@login_required(login_url='login_admin')
def add_state(request):

    if request.method == "POST":
        form = StateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_state')
        else:
            context = {"form": form}
            return render(request, 'add_state.html', context)  # reuse simple form template
    else:
        form = StateForm()
        context = {"form": form}
        return render(request, 'add_state.html', context)


@login_required(login_url='login_admin')
def update_state(request, state_id):
    instance = get_object_or_404(State, id=state_id)
    if request.method == "POST":
        form = StateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('list_state')
    else:
        form = StateForm(instance=instance)
    return render(request, 'add_state.html', {"form": form})


@login_required(login_url='login_admin')
def list_state(request):
    data = State.objects.all().order_by('name')
    return render(request, 'list_state.html', {"data": data})  # reuse listing template


@login_required(login_url='login_admin')
def delete_state(request, state_id):
    State.objects.filter(id=state_id).delete()
    return HttpResponseRedirect(reverse('list_state'))


class get_state(ListAPIView):
    queryset = State.objects.all().order_by('name')
    serializer_class = StateSerializer
    filter_backends = [DjangoFilterBackend]





@login_required(login_url='login_admin')
def list_notification_campaigns(request):

    data = NotificationCampaign.objects.all()
    context = {
        'data': data
    }
    return render(request, 'list_notification_campaigns.html', context)



import requests
from django.conf import settings

from users.models import DeviceToken

from firebase_admin import messaging

def send_push_notification(user, title, body, campaign_id):
    print('I am here')

    device_token = DeviceToken.objects.get(user=user)

    if device_token:

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={
                "campaign_id": str(campaign_id),
            },
            token=device_token,
        )

        try:
            response = messaging.send(message)
            print("✅ Successfully sent message:", response)
        except Exception as e:
            print("❌ Error sending message:", e)




from django.contrib import messages
from django.utils import timezone
from datetime import timedelta



def approve_notification_campaign(request, pk):
    campaign = get_object_or_404(NotificationCampaign, pk=pk)
    campaign.status = "active"
    campaign.save()

    # send push notifications to all followers
    followers = User.objects.filter()  # adjust as per your relation
    print(f"🔔 Starting notification sending for campaign={campaign.id}, followers={followers.count()}")

    for follower_relation in followers:
        follower = follower_relation  # get actual user object
        try:
            response = send_push_notification(
                user=follower,
                title=campaign.campaign_name,
                body=campaign.description,
                campaign_id=campaign.id
            )
            print(f"✅ Notification sent to user_id={follower.id}, username={follower.username}, response={response}")
        except Exception as e:
            print(f"❌ Failed to send notification to user_id={follower.id}, username={follower.username}, error={e}")

    messages.success(request, "Campaign approved and notification sent.")
    return redirect("list_notification_campaigns")



def reject_notification_campaign(request, pk):
    campaign = get_object_or_404(NotificationCampaign, pk=pk)
    campaign.status = "rejected"
    campaign.rejection_reason = request.POST.get("reason", "Not approved")
    campaign.save()

    messages.error(request, "Campaign rejected.")
    return redirect("list_notification_campaigns")



def add_testimonials(request):
    
    if request.method == "POST":

        forms = testimonials_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_testimonials')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_testimonials.html', context)
    
    else:

        # create first row using admin then editing only

        

        return render(request, 'add_testimonials.html', { 'form' : testimonials_Form()})

def update_testimonials(request, testimonials_id):
    
    instance = testimonials.objects.get(id = testimonials_id)

    if request.method == "POST":

        forms = testimonials_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_testimonials')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_testimonials.html', context)

    
    else:

        # create first row using admin then editing only

        forms = testimonials_Form(instance=instance)
                
        context = {
            'form': forms
        }
        
        return render(request, 'add_testimonials.html', context)


def list_testimonials(request):

    data = testimonials.objects.all()

    return render(request, 'list_testimonials.html', {'data' : data})


def delete_testimonials(request, testimonials_id):

    data = testimonials.objects.get(id = testimonials_id).delete()

    return redirect('list_testimonials')



from django.views import View


class get_testimonials(ListAPIView):
    queryset = testimonials.objects.all()
    serializer_class = testimonials_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'  # enables filtering on all fields


def add_city(request):
    
    if request.method == "POST":

        forms = cityForm(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_city')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_city.html', context)
    
    else:

        # create first row using admin then editing only

        

        return render(request, 'add_city.html', { 'form' : cityForm()})

def update_city(request, city_id):
    
    instance = city.objects.get(id = city_id)

    if request.method == "POST":

        forms = cityForm(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_city')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_city.html', context)

    
    else:

        # create first row using admin then editing only

        forms = cityForm(instance=instance)
                
        context = {
            'form': forms
        }
        
        return render(request, 'add_city.html', context)


def list_city(request):

    data = city.objects.all()

    return render(request, 'list_city.html', {'data' : data})


def delete_city(request, city_id):

    data = city.objects.get(id = city_id).delete()

    return redirect('list_city')


class get_city(ListAPIView):
    queryset = city.objects.all()
    serializer_class = city_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'  # enables filtering on all fields


from django.views import View


class get_testimonials(ListAPIView):
    queryset = testimonials.objects.all()
    serializer_class = testimonials_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'  # enables filtering on all fields


def add_product_main_category(request):
    if request.method == 'POST':
        form = MainCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_product_main_category')  # redirect to your list page or wherever needed
    else:
        form = MainCategoryForm()
    return render(request, 'main_category_form.html', {'form': form, 'title': 'Add Main Category'})


def update_product_main_category(request, product_main_category_id):
    main_category = get_object_or_404(MainCategory, pk=product_main_category_id)
    if request.method == 'POST':
        form = MainCategoryForm(request.POST, instance=main_category)
        if form.is_valid():
            form.save()
            return redirect('list_product_main_category')
    else:
        form = MainCategoryForm(instance=main_category)
    return render(request, 'main_category_form.html', {'form': form, 'title': 'Update Main Category'})



def list_product_main_category(request):

    data = MainCategory.objects.annotate(categories_count=Count('categories'))

    return render(request, 'main_category_list.html', {'data' : data})


def delete_product_main_category(request, product_main_category_id):

    data = MainCategory.objects.get(id = product_main_category_id).delete()

    return redirect('list_product_main_category')



class get_product_main_category(ListAPIView):
    queryset = MainCategory.objects.all()
    serializer_class = product_main_category_serializer




def add_product_category(request):
    
    if request.method == "POST":

        forms = product_category_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_product_category')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_product_category.html', context)


    else:

        # create first row using admin then editing only

        

        return render(request, 'add_product_category.html', { 'form' : product_category_Form()})

def update_product_category(request, product_category_id):
    
    instance = product_category.objects.get(id = product_category_id)

    if request.method == "POST":

        forms = product_category_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_product_category')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_product_category.html', context)
    
    else:

        # create first row using admin then editing only

        forms = product_category_Form(instance=instance)

        return render(request, 'add_product_category.html', {'form' : forms})


def list_product_category(request):

    data = product_category.objects.select_related('main_category').all()

    return render(request, 'list_product_category.html', {'data' : data})


def delete_product_category(request, product_category_id):

    data = product_category.objects.get(id = product_category_id).delete()

    return redirect('list_product_category')



class get_product_category(ListAPIView):
    queryset = product_category.objects.all()
    serializer_class = product_category_serializer




def add_product_subcategory(request):
    
    if request.method == "POST":

        forms = product_subcategory_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_product_subcategory')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_product_subcategory.html', context)


    else:

        # create first row using admin then editing only

        

        return render(request, 'add_product_subcategory.html', { 'form' : product_subcategory_Form()})

def update_product_subcategory(request, product_subcategory_id):
    
    instance = product_subcategory.objects.get(id = product_subcategory_id)

    if request.method == "POST":

        forms = product_subcategory_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_product_subcategory')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_product_subcategory.html', context)
    
    else:

        # create first row using admin then editing only

        forms = product_subcategory_Form(instance=instance)

        return render(request, 'add_product_subcategory.html', {'form' : forms})


def list_product_subcategory(request):

    data = product_subcategory.objects.all()

    return render(request, 'list_product_subcategory.html', {'data' : data})


def delete_product_subcategory(request, product_subcategory_id):

    data = product_subcategory.objects.get(id = product_subcategory_id).delete()

    return redirect('list_product_subcategory')






class get_product_subcategory(ListAPIView):
    serializer_class = product_subcategory_serializer

    def get_queryset(self):
        queryset = product_subcategory.objects.all()
        category_id = self.request.query_params.get("category_id")  # ?category_id=1

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset



from django.views import View






def add_expense_category(request):
    
    if request.method == "POST":

        forms = expense_category_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_expense_category')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_expense_category.html', context)


    else:

        # create first row using admin then editing only

        

        return render(request, 'add_expense_category.html', { 'form' : expense_category_Form()})

def update_expense_category(request, expense_category_id):
    
    instance = expense_category.objects.get(id = expense_category_id)

    if request.method == "POST":

        forms = expense_category_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_expense_category')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_expense_category.html', context)
    
    else:

        # create first row using admin then editing only

        forms = expense_category_Form(instance=instance)

        return render(request, 'add_expense_category.html', {'form' : forms})


def list_expense_category(request):

    data = expense_category.objects.all()

    return render(request, 'list_expense_category.html', {'data' : data})


def delete_expense_category(request, expense_category_id):

    data = expense_category.objects.get(id = expense_category_id).delete()

    return redirect('list_expense_category')



class get_expense_category(ListAPIView):
    queryset = expense_category.objects.all()
    serializer_class = expense_category_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'  # enables filtering on all fields


def add_size(request):
    
    if request.method == "POST":

        forms = size_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_size')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_size.html', context)


    else:

        # create first row using admin then editing only

        

        return render(request, 'add_size.html', { 'form' : size_Form()})

def update_size(request, size_id):
    
    instance = size.objects.get(id = size_id)

    if request.method == "POST":

        forms = size_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_size')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_size.html', context)
    
    else:

        # create first row using admin then editing only

        forms = size_Form(instance=instance)

        return render(request, 'add_size.html', {'form' : forms})


def list_size(request):

    data = size.objects.all()

    return render(request, 'list_size.html', {'data' : data})


def delete_size(request, size_id):

    data = size.objects.get(id = size_id).delete()

    return redirect('list_size')



class get_size(ListAPIView):
    queryset = size.objects.all()
    serializer_class = size_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'  # enables filtering on all fields


def add_color(request):

    if request.method == "POST":

        forms = color_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_color')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_color.html', context)


    else:

        return render(request, 'add_color.html', {'form': color_Form()})


def update_color(request, color_id):

    instance = color.objects.get(id=color_id)

    if request.method == "POST":

        forms = color_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_color')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_color.html', context)

    else:

        forms = color_Form(instance=instance)

        return render(request, 'add_color.html', {'form': forms})


def list_color(request):

    data = color.objects.all()

    return render(request, 'list_color.html', {'data': data})


def delete_color(request, color_id):

    data = color.objects.get(id=color_id).delete()

    return redirect('list_color')


class get_color(ListAPIView):
    queryset = color.objects.all()
    serializer_class = color_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


from rest_framework.response import Response

from rest_framework.views import APIView

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

 
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import JSONParser



class customer_address_ViewSet(ModelViewSet):

    permission_classes = [IsCustomer]

    serializer_class = customer_address_serializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsCustomer]  # Or use IsAuthenticated if needed

    def get_queryset(self):
        return customer_address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        

def update_customer_address(request, customer_address_id):
    
    instance = customer_address.objects.get(id = customer_address_id)

    if request.method == "POST":

        forms = customer_address_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_customer_address')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_customer_address.html', context)
    
    else:

        # create first row using admin then editing only

        forms = customer_address_Form(instance=instance)
        
        context = {
                'form': forms
            }

        return render(request, 'add_customer_address.html', context)


def list_customer_address(request):

    data = customer_address.objects.filter(user = request.user)

    return render(request, 'list_customer_address.html', {'data' : data})


def delete_customer_address(request, customer_address_id):

    data = customer_address.objects.get(id = customer_address_id).delete()

    return redirect('list_customer_address')


from django.views import View



class get_customer_address(ListAPIView):
    queryset = customer_address.objects.all()
    serializer_class = customer_address_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'  # enables filtering on all fields

    def get_queryset(self):
        return customer_address.objects.filter(user=self.request.user)


from django.forms import inlineformset_factory


def add_home_banner(request):
    
    if request.method == "POST":

        forms = home_banner_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_home_banner')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }

            return render(request, 'add_home_banner.html', context)
    
    else:

        # create first row using admin then editing only

        

        return render(request, 'add_home_banner.html', { 'form' : home_banner_Form()})

def update_home_banner(request, home_banner_id):
    
    instance = home_banner.objects.get(id = home_banner_id)

    if request.method == "POST":


        instance = home_banner.objects.get(id=home_banner_id)

        forms = home_banner_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_home_banner')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }

            return render(request, 'add_home_banner.html', context)

    
    else:

        # create first row using admin then editing only

        forms = home_banner_Form(instance=instance)
                
        context = {
            'form': forms
        }

        return render(request, 'add_home_banner.html', context)


def list_home_banner(request):

    data = home_banner.objects.all()

    return render(request, 'list_home_banner.html', {'data' : data})



@login_required(login_url='login_admin')
def vendor_list_bannercampaign(request):

    data = BannerCampaign.objects.filter(user = request.user)
    context = {
        'data': data
    }
    return render(request, 'vendor_list_bannercampaign.html', context)


@login_required(login_url='login_admin')
def approve_bannercampaign(request, banner_id):

    data = BannerCampaign.objects.get(id = banner_id)
    data.is_approved = True
    data.save()
    
    return redirect('vendor_list_bannercampaign')




def delete_home_banner(request, home_banner_id):

    data = home_banner.objects.get(id = home_banner_id).delete()

    return redirect('list_home_banner')


from django.views import View

def get_home_banner(request):
  
    data = home_banner.objects.all()  # Assuming home_banner is the model name


    serialized_data = HomeBannerSerializer(data, many=True, context={'request': request}).data
    return JsonResponse({"data": serialized_data}, status=200)


from rest_framework import status


from rest_framework import viewsets


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)



