from django.shortcuts import get_object_or_404, render

from masters.filters import EventFilter
from vendor.filters import productFilter

# Create your views here.


from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from .serializers import *

from users.permissions import *
from django.db.models import Sum

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework import viewsets, permissions


from django_filters.rest_framework import DjangoFilterBackend

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import vendor_store, StoreCoverMedia
from .serializers import VendorStoreSerializer
from customer.models import Order, OrderItem


from rest_framework.decorators import action


class VendorStoreAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get the logged-in vendor's store"""
        try:
            store = vendor_store.objects.get(user=request.user)
            serializer = VendorStoreSerializer(store)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except vendor_store.DoesNotExist:
            return Response({"detail": "Store not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        """Update the logged-in vendor's store. Same API accepts cover_media (multiple files). Type inferred from Content-Type."""
        try:
            store = vendor_store.objects.get(user=request.user)
            serializer = VendorStoreSerializer(store, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(user=request.user)
                # Single key: cover_media; or legacy cover_photos + cover_videos. Type inferred from Content-Type.
                files = request.FILES.getlist('cover_media') or request.FILES.getlist('cover_media[]')
                if not files:
                    cover_photos = request.FILES.getlist('cover_photos') or request.FILES.getlist('cover_photos[]')
                    cover_videos = request.FILES.getlist('cover_videos') or request.FILES.getlist('cover_videos[]')
                    for f in cover_photos:
                        files.append((f, 'image'))
                    for f in cover_videos:
                        files.append((f, 'video'))
                else:
                    files = [(f, 'video' if (getattr(f, 'content_type', '') or '').lower().startswith('video/') else 'image') for f in files]
                if files:
                    store.cover_media.all().delete()
                    for i, item in enumerate(files):
                        f, media_type = item if isinstance(item, tuple) else (item, 'image')
                        StoreCoverMedia.objects.create(store=store, media_type=media_type, media=f, order=i)
                out = VendorStoreSerializer(store, context={'request': request}).data
                return Response(out, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except vendor_store.DoesNotExist:
            return Response({"detail": "Store not found."}, status=status.HTTP_404_NOT_FOUND)      

@login_required(login_url='login_admin')
def add_coupon(request):

    if request.method == 'POST':

        forms = coupon_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms = forms.save(commit=False)
            forms.user = request.user  # assign user here
            forms.save()
            return redirect('list_coupon')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_coupon.html', context)
    
    else:

        forms = coupon_Form()

        context = {
            'form': forms
        }
        return render(request, 'add_coupon.html', context)

        

@login_required(login_url='login_admin')
def update_coupon(request, coupon_id):

    if request.method == 'POST':

        instance = coupon.objects.get(id=coupon_id)

        forms = coupon_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms = forms.save(commit=False)
            forms.user = request.user  # assign user here
            forms.save()
            return redirect('list_coupon')
        else:
            print(forms.errors)
    
    else:

        instance = coupon.objects.get(id=coupon_id)
        forms = coupon_Form(instance=instance)

        context = {
            'form': forms
        }
        return render(request, 'add_coupon.html', context)

        

@login_required(login_url='login_admin')
def delete_coupon(request, coupon_id):

    coupon.objects.get(id=coupon_id).delete()

    return HttpResponseRedirect(reverse('list_coupon'))


@login_required(login_url='login_admin')
def list_coupon(request):

    data = coupon.objects.filter(user = request.user)
    context = {
        'data': data
    }
    return render(request, 'list_coupon.html', context)


@login_required(login_url='login_admin')
def add_bannercampaign(request):

    if request.method == 'POST':

        forms = BannerCampaignForm(request.POST, request.FILES)

        if forms.is_valid():
            forms = forms.save(commit=False)
            forms.user = request.user  # assign user here
            forms.save()
            return redirect('list_bannercampaign')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_bannercampaign.html', context)
    
    else:

        forms = BannerCampaignForm()

        context = {
            'form': forms
        }
        return render(request, 'add_bannercampaign.html', context)

        

@login_required(login_url='login_admin')
def update_bannercampaign(request, party_id):

    if request.method == 'POST':

        instance = BannerCampaign.objects.get(id=party_id)

        forms = BannerCampaignForm(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_bannercampaign')
        else:
            print(forms.errors)
    
    else:

        instance = BannerCampaign.objects.get(id=party_id)
        forms = BannerCampaignForm(instance=instance)

        context = {
            'form': forms
        }
        return render(request, 'add_bannercampaign.html', context)

        

@login_required(login_url='login_admin')
def delete_bannercampaign(request, bannercampaign_id):

    BannerCampaign.objects.get(id=bannercampaign_id).delete()

    return HttpResponseRedirect(reverse('list_bannercampaign'))


@login_required(login_url='login_admin')
def list_bannercampaign(request):

    data = BannerCampaign.objects.filter(user = request.user)
    context = {
        'data': data
    }
    return render(request, 'list_bannercampaign.html', context)



from customer.serializers import *


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product').all().order_by('-id')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """Restrict update to only allowed fields"""
        instance = self.get_object()
        allowed_fields = {"status", "delivery_boy", "is_paid"}
        data = {k: v for k, v in request.data.items() if k in allowed_fields}

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """PATCH behaves same as restricted PUT"""
        return self.update(request, *args, **kwargs)


    @action(detail=False, methods=['get'], url_path='delivery-boy/assigned-orders')
    def delivery_for_delivery_boy(self, request):
        """
        List all orders assigned to the logged-in delivery boy.
        Matches orders where order.delivery_boy.account_user == request.user.
        """
        qs = (Order.objects
              .filter(delivery_boy__account_user=request.user)
              .prefetch_related('items__product')
              .distinct()
              .order_by('-id'))
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

from django.db import transaction
from django.shortcuts import get_object_or_404

from io import BytesIO
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.units import mm
from reportlab.lib import colors
from .models import product

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, KeepInFrame, PageBreak
)


from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.graphics.barcode import code128
from reportlab.lib.utils import ImageReader
from num2words import num2words
from datetime import datetime


class AssignDeliveryBoyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        delivery_boy_id = request.data.get("delivery_boy_id")
        if not delivery_boy_id:
            return Response({"error": "delivery_boy_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            delivery_boy = DeliveryBoy.objects.get(id=delivery_boy_id, user=request.user)
        except DeliveryBoy.DoesNotExist:
            return Response({"error": "Delivery boy not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            order = Order.objects.prefetch_related("items__product").get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.items.exists():
            all_items_belong = all(getattr(item.product, "user_id", None) == request.user.id for item in order.items.all())
            if not all_items_belong:
                return Response({"error": "Forbidden: order contains items from other vendors"}, status=status.HTTP_403_FORBIDDEN)

        order.delivery_boy = delivery_boy
        # Generate a 6-digit numeric OTP
        import random
        from django.utils import timezone
        order.delivery_otp = f"{random.randint(0, 999999):06d}"
        order.delivery_otp_generated_at = timezone.now()
        order.save(update_fields=["delivery_boy", "delivery_otp", "delivery_otp_generated_at"])

        return Response(OrderSerializer(order, context={"request": request}).data, status=status.HTTP_200_OK)


def generate_barcode(request):
    # Example product details (replace these with DB data)

    if request.method == "POST":

        ids = request.POST.getlist("selected_products")
        products = product.objects.filter(id__in=ids, is_active=True)

        if not products.exists(): 
            return HttpResponse("No products selected", status=400) 
       

        try: 
            company = vendor_store.objects.get(user=request.user) 
            company_name = company.name or "COMPANY NAME" 
        except vendor_store.DoesNotExist: 
            company_name = "COMPANY NAME"
        
       


        # Dynamically set layout size
        # if user_settings and user_settings.barcode_size == "50x100":
        #     PAGE_WIDTH = 100 * mm
        #     PAGE_HEIGHT = 50 * mm
        #     barcode_height = 18 * mm
        #     font_title = 10
        #     font_text = 8
        #     font_price = 9
        # else:
        #     PAGE_WIDTH = 50 * mm
        #     PAGE_HEIGHT = 25 * mm
        #     barcode_height = 10 * mm
        #     font_title = 7
        #     font_text = 5
        #     font_price = 6

        PAGE_WIDTH = 100 * mm
        PAGE_HEIGHT = 50 * mm
        barcode_height = 18 * mm
        font_title = 10
        font_text = 9
        font_price = 9

        # Create PDF

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

        for i in products:
            item_name = i.name
            mrp = i.mrp
            discount = i.wholesale_price
            sale_price = i.sales_price
            package_date = datetime.now().strftime("%d/%m/%Y")
            note = "The small note here"
            barcode_value = i.id

          
            # Margin padding
            x_margin = 2 * mm
            y_margin = 2 * mm

            # Draw rounded border
            p.setStrokeColor(colors.black)
            p.roundRect(x_margin, y_margin, PAGE_WIDTH - 2 * x_margin, PAGE_HEIGHT - 2 * y_margin, 3 * mm, stroke=1, fill=0)

            # Starting coordinates
            x_left = x_margin + 5
            y_top = PAGE_HEIGHT - y_margin - 8

           # === Company Name (Top Center) ===
            p.setFont("Helvetica-Bold", font_title + 2)
            p.drawCentredString(PAGE_WIDTH / 2, y_top - 4, company_name)

            # Add extra vertical gap below company name
            company_name_gap = 10  # ⬅️ increase this for more distance
            content_start_y = y_top - 4 - company_name_gap

            # === Left Side (Item / MRP / Discount) ===
            p.setFont("Helvetica-Bold", font_text)
            line_gap = 12  # spacing between each text line
            start_y = content_start_y - 10  # ⬅️ start content a bit below the heading

            # Item
            p.drawString(x_left, start_y, "Item:")
            p.setFont("Helvetica", font_text)
            p.drawString(x_left + 28, start_y, str(item_name))

            # MRP
            p.setFont("Helvetica-Bold", font_text)
            p.drawString(x_left, start_y - line_gap, "MRP:")
            p.setFont("Helvetica", font_text)
            p.drawString(x_left + 28, start_y - line_gap, f"{mrp:.2f}")

            # Discount
            p.setFont("Helvetica-Bold", font_text)
            p.drawString(x_left, start_y - 2 * line_gap, "Discount:")
            p.setFont("Helvetica", font_text)
            p.drawString(x_left + 45, start_y - 2 * line_gap, str(discount if discount else "None"))

            # === NOTE BOX (Anchored near bottom left) ===
            note_box_height = 12 * mm
            note_box_y = y_margin + 8 * mm  # padding from bottom
            p.setFont("Helvetica-Bold", font_text)
            p.drawString(x_left, note_box_y + 14 * mm, "Note:")  # was 12 * mm
            p.rect(x_left, note_box_y-2, 45 * mm, 12 * mm)
            p.setFont("Helvetica", font_text - 1)
            p.drawString(x_left + 5, note_box_y + note_box_height / 2 - 3, note)

            # === RIGHT SIDE (Package Date / Barcode / Sale Price / In Word) ===
            right_start_x = PAGE_WIDTH - (x_margin + 45 * mm)

            # Add this vertical offset to push everything down
            right_section_offset = 25  # ⬅️ increase this for more gap from the top
            right_top_y = y_top - right_section_offset

            # Package Date
            p.setFont("Helvetica", font_text)
            p.drawString(right_start_x, right_top_y, f"Package Date - {package_date}")

            # Barcode (centered nicely below package date)
            barcode_top_gap = 5 * mm  # vertical gap between date and barcode
            barcode = code128.Code128(barcode_value, barHeight=barcode_height, barWidth=0.6)

            barcode_x = PAGE_WIDTH - x_margin - 40 * mm
            barcode_y = right_top_y - barcode_top_gap - barcode_height
            barcode.drawOn(p, barcode_x, barcode_y)

            # Sale Price (pushed below barcode)
            price_gap = 10  # distance between barcode and Sale Price
            p.setFont("Helvetica-Bold", font_price)
            p.drawString(right_start_x, barcode_y - price_gap, f"Sale Price: {sale_price:.2f}")

            # In Word — right-aligned with the note box bottom
            p.setFont("Helvetica", font_text - 1)
            inword_text = f"In Word: {num2words(sale_price)}"
            text_width = p.stringWidth(inword_text, "Helvetica", font_text - 1)
            p.drawString(PAGE_WIDTH - x_margin - text_width - 5, note_box_y - 12, inword_text)
            # Finish up
            p.showPage()
        p.save()

        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')


    else:

        data = product.objects.filter(user=request.user, is_active=True)
        context = {
            'data': data
        }
        return render(request, 'list_product_barcode.html', context)

        


from django.http import JsonResponse


class get_product(ListAPIView):
    queryset = product.objects.filter(is_active=True)
    serializer_class = product_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'  # enables filtering on all fields
    filterset_class = productFilter  # enables filtering on all fields




class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = product_serializer
    permission_classes = [IsVendor]

    def get_queryset(self):
        return product.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)



from rest_framework.decorators import action


class ReelViewSet(viewsets.ModelViewSet):
    queryset = Reel.objects.all()
    serializer_class = ReelSerializer
    permission_classes = [IsVendor]

    def get_queryset(self):
        # Return only products of logged-in user
        return Reel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign logged-in user to the product
        serializer.save(user=self.request.user)


from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

class CouponViewSet(viewsets.ModelViewSet):
    queryset = coupon.objects.all()
    serializer_class = coupon_serializer
    permission_classes = [IsVendor]
    parser_classes = [MultiPartParser, FormParser, JSONParser] 

    def get_queryset(self):
        # Return only products of logged-in user
        return coupon.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign logged-in user to the product
        serializer.save(user=self.request.user)



from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

class DeliveryBoyLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response({"error": "email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Our User model authenticates by mobile; implement email-based login manually
        from users.models import User
        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Ensure this account corresponds to a delivery boy profile
        delivery_boy = DeliveryBoy.objects.filter(account_user=user).first()
        if not delivery_boy:
            return Response({"error": "Not a delivery boy account"}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "mobile": user.mobile,
                "email": user.email,
            },
            "delivery_boy": {
                "id": delivery_boy.id,
                "name": delivery_boy.name,
                "mobile": delivery_boy.mobile,
                "email": delivery_boy.email,
            },
        }
        return Response(data, status=status.HTTP_200_OK)


class DeliveryBoyLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Best-effort blacklist if app is installed; otherwise instruct client to discard tokens
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                # Will raise if blacklist app not installed; ignore gracefully
                try:
                    token.blacklist()
                except Exception:
                    pass
            except Exception:
                pass
        return Response({"message": "Logged out"}, status=status.HTTP_200_OK)

class AcceptOrderAPIView(APIView):
    """
    POST /vendor/orders/<order_id>/accept/
    Vendor accepts the order. Only order status set to 'accepted'; OrderItem statuses unchanged.
    Auth: vendor JWT. Order must contain only this vendor's products.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        items = list(order.items.all())
        if not items:
            return Response({"error": "No items in order"}, status=status.HTTP_400_BAD_REQUEST)
        if not all(getattr(i.product, "user_id", None) == request.user.id for i in items):
            return Response({"error": "Forbidden: order contains items from other vendors"}, status=status.HTTP_403_FORBIDDEN)
        order.status = "accepted"
        order.save(update_fields=["status"])
        return Response(OrderSerializer(order, context={"request": request}).data, status=status.HTTP_200_OK)


class RejectOrderAPIView(APIView):
    """
    POST /vendor/orders/<order_id>/reject/
    Vendor rejects the order. Order items set to 'cancelled', order status to 'cancelled', product stock restored.
    Cannot reject if order is already completed. Auth: vendor JWT.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        items = list(order.items.all())
        if not items:
            return Response({"error": "No items in order"}, status=status.HTTP_400_BAD_REQUEST)
        if not all(getattr(i.product, "user_id", None) == request.user.id for i in items):
            return Response({"error": "Forbidden: order contains items from other vendors"}, status=status.HTTP_403_FORBIDDEN)
        if order.status == "completed":
            return Response({"error": "Cannot reject after order is completed"}, status=status.HTTP_400_BAD_REQUEST)
        for i in items:
            i.status = "cancelled"
            i.save(update_fields=["status"])
            p = i.product
            p.stock = (p.stock or 0) + i.quantity
            p.save(update_fields=["stock"])
        order.status = "cancelled"
        order.save(update_fields=["status"])
        return Response(OrderSerializer(order, context={"request": request}).data, status=status.HTTP_200_OK)


class ReadyToDispatchOrderAPIView(APIView):
    """
    POST /vendor/orders/<order_id>/ready-to-dispatch/
    Vendor marks the order as ready to dispatch. Sets order status to 'ready_to_dispatch'.
    Auth: vendor JWT. Order must contain only this vendor's products.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        items = list(order.items.all())
        if not items:
            return Response({"error": "No items in order"}, status=status.HTTP_400_BAD_REQUEST)
        if not all(getattr(i.product, "user_id", None) == request.user.id for i in items):
            return Response({"error": "Forbidden: order contains items from other vendors"}, status=status.HTTP_403_FORBIDDEN)
        order.status = "ready_to_dispatch"
        order.save(update_fields=["status"])
        return Response(OrderSerializer(order, context={"request": request}).data, status=status.HTTP_200_OK)


class CommonOrderStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        """
        Update order status to: accepted | rejected | cancelled_by_vendor.
        OrderItem statuses only set to 'cancelled' when rejecting/cancelling; accepted is order-level only.
        Cannot cancel if order is already completed. Vendor ownership required.
        """
        new_status = (request.data.get("status") or "").strip()
        allowed_statuses = {
            "accepted",
            "rejected",
            "cancelled_by_vendor",
        }
        if new_status not in allowed_statuses:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.prefetch_related("items__product").get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        items = list(order.items.all())
        if not items:
            return Response({"error": "No items in order"}, status=status.HTTP_400_BAD_REQUEST)

        if not all(getattr(i.product, "user_id", None) == request.user.id for i in items):
            return Response({"error": "Forbidden: order contains items from other vendors"}, status=status.HTTP_403_FORBIDDEN)

        if new_status in ("rejected", "cancelled_by_vendor") and order.status == "completed":
            return Response({"error": "Cannot cancel after order is completed"}, status=status.HTTP_400_BAD_REQUEST)

        if new_status == "accepted":
            order.status = "accepted"
            order.save(update_fields=["status"])
        else:
            for i in items:
                i.status = "cancelled"
                i.save(update_fields=["status"])
                p = i.product
                p.stock = (p.stock or 0) + i.quantity
                p.save(update_fields=["stock"])
            order.status = "cancelled"
            order.save(update_fields=["status"])

        return Response(OrderSerializer(order, context={"request": request}).data, status=status.HTTP_200_OK)


class ConfirmDeliveryByOTPAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        """
        Delivery boy marks order as reached/delivered. No OTP required.
        Marks all items as delivered and completes the order.
        Only the assigned delivery boy can confirm.
        """
        try:
            order = Order.objects.prefetch_related("items__product", "delivery_boy").get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Only assigned delivery boy can confirm delivery
        if not order.delivery_boy or getattr(order.delivery_boy, "account_user_id", None) != request.user.id:
            return Response({"error": "Forbidden: not assigned delivery boy"}, status=status.HTTP_403_FORBIDDEN)

        # Complete order (delivery status lives on Order only; OrderItem statuses unchanged)
        order.status = "delivered"
        order.delivery_otp = None
        order.save(update_fields=["status", "delivery_otp"])

        return Response(OrderSerializer(order, context={"request": request}).data, status=status.HTTP_200_OK)


        

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response



# -------------------------------
# Store Reviews (vendor moderation)
# -------------------------------
from customer.models import Review
from customer.serializers import ReviewSerializer


class StoreReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        qs = Review.objects.select_related('order_item__product', 'user')
        # Default: vendor sees own store's reviews
        qs = qs.filter(order_item__product__user=self.request.user)

        # Optional filter: admin can pass store_user_id to view specific store
        store_user_id = self.request.query_params.get('store_user_id')
        if store_user_id:
            qs = Review.objects.filter(order_item__product__user_id=store_user_id)

        is_visible = self.request.query_params.get('is_visible')
        if is_visible is not None:
            val = str(is_visible).lower() in ('true', '1', 'yes')
            qs = qs.filter(is_visible=val)

        return qs.order_by('-created_at')

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Only the vendor owning the product (or superuser) can toggle visibility
        if (getattr(instance.order_item.product, 'user', None) != request.user) and (not request.user.is_superuser):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        is_visible = request.data.get('is_visible', None)
        if is_visible is None:
            return Response({"error": "is_visible is required"}, status=status.HTTP_400_BAD_REQUEST)

        instance.is_visible = str(is_visible).lower() in ('true', '1', 'yes')
        instance.save(update_fields=['is_visible'])
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)


class BannerCampaignViewSet(viewsets.ModelViewSet):
    queryset = BannerCampaign.objects.all()
    serializer_class = BannerCampaignSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        redirect_to = self.request.data.get('redirect_to')

        if redirect_to == 'store':
            try:
                store = vendor_store.objects.get(user=self.request.user)
            except vendor_store.DoesNotExist:
                raise ValidationError({"store": "Vendor store not found for this user."})
            serializer.save(user=self.request.user, store=store, product=None)
        else:
            serializer.save(user=self.request.user, store=None, product=None)



class DeliveryBoyViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryBoySerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return DeliveryBoy.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        from users.models import User
        username = (self.request.data.get("username") or "").strip()
        password = self.request.data.get("password")
        mobile = (self.request.data.get("mobile") or "").strip()
        email = self.request.data.get("email") or ""

        # Login identifier: use username if provided, else mobile (for login: send same value as "username")
        login_identifier = username if username else mobile

        account_user = None
        if login_identifier and password:
            # Create login account: User uses mobile as USERNAME_FIELD, so we store login_identifier in mobile for delivery boy login
            if User.objects.filter(mobile=login_identifier).exists():
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"username": "This username/mobile is already taken for login."})
            account_user = User.objects.create_user(
                mobile=login_identifier,
                password=password,
                email=email or None,
            )
            account_user.is_deliveryboy = True
            account_user.save(update_fields=["is_deliveryboy"])
        serializer.save(user=self.request.user, account_user=account_user, username=username or mobile or None, mobile=mobile, email=email)

    def perform_update(self, serializer):
        from users.models import User
        instance = serializer.instance
        username = (self.request.data.get("username") or "").strip()
        password = self.request.data.get("password")
        mobile = (self.request.data.get("mobile") or instance.mobile or "").strip()
        email = self.request.data.get("email", instance.email) or ""

        login_identifier = username if username else mobile
        account_user = getattr(instance, "account_user", None)

        if login_identifier and password:
            if account_user:
                # Update existing login account - skip uniqueness check if login id unchanged (e.g. only updating password)
                if login_identifier != account_user.mobile:
                    if User.objects.filter(mobile=login_identifier).exists():
                        from rest_framework.exceptions import ValidationError
                        raise ValidationError({"username": "This username/mobile is already taken for login."})
                account_user.mobile = login_identifier
                account_user.set_password(password)
                account_user.email = email or None
                account_user.save(update_fields=["mobile", "password", "email"])
            else:
                # Create login account (was created without one)
                if User.objects.filter(mobile=login_identifier).exists():
                    from rest_framework.exceptions import ValidationError
                    raise ValidationError({"username": "This username/mobile is already taken for login."})
                account_user = User.objects.create_user(mobile=login_identifier, password=password, email=email or None)
                account_user.is_deliveryboy = True
                account_user.save(update_fields=["is_deliveryboy"])

        save_kwargs = {"username": username or mobile or instance.username, "mobile": mobile, "email": email}
        if account_user is not None and not getattr(instance, "account_user_id", None):
            save_kwargs["account_user"] = account_user
        serializer.save(**save_kwargs)


class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  
    def get_queryset(self):
        # Show all offers related to the user's requests or their own offers
        user = self.request.user
        return Offer.objects.filter(
            models.Q(request__user=user) | models.Q(seller=user)
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class StoreOfferViewSet(viewsets.ModelViewSet):
    """Create Offer form API: offer title, description, type (Discount % / Free Delivery), valid from/to, discount value, applicable products/categories, eligibility."""
    serializer_class = StoreOfferSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return StoreOffer.objects.filter(user=self.request.user).prefetch_related(
            'applicable_products', 'applicable_categories'
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SpotlightProductViewSet(viewsets.ModelViewSet):
    """Vendor spotlight products: list, create, update, delete. Only own products can be added."""
    serializer_class = SpotlightProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SpotlightProduct.objects.filter(user=self.request.user).select_related('product').order_by('id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


        