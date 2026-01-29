import django_filters
from doctor.models import doctor
from django.contrib.auth.models import User


class DoctorFilter(django_filters.FilterSet):
    # Doctor fields
    name = django_filters.CharFilter(lookup_expr="icontains")
    gender = django_filters.CharFilter(lookup_expr="iexact")
    phone_number = django_filters.CharFilter(lookup_expr="icontains")
    clinic_name = django_filters.CharFilter(lookup_expr="icontains")
    clinic_phone_number = django_filters.CharFilter(lookup_expr="icontains")
    email = django_filters.CharFilter(lookup_expr="icontains")

    house_building = django_filters.CharFilter(lookup_expr="icontains")
    locality = django_filters.CharFilter(lookup_expr="icontains")
    pincode = django_filters.CharFilter(lookup_expr="icontains")
    state = django_filters.CharFilter(lookup_expr="icontains")
    city = django_filters.CharFilter(lookup_expr="icontains")
    country = django_filters.CharFilter(lookup_expr="icontains")

    designation = django_filters.CharFilter(lookup_expr="icontains")
    title = django_filters.CharFilter(lookup_expr="icontains")
    degree = django_filters.CharFilter(lookup_expr="icontains")
    specializations = django_filters.CharFilter(lookup_expr="icontains")
    education = django_filters.CharFilter(lookup_expr="icontains")
    about_doctor = django_filters.CharFilter(lookup_expr="icontains")

    experience_years = django_filters.NumberFilter()
    rating = django_filters.NumberFilter()
    review_count = django_filters.NumberFilter()
    remark = django_filters.CharFilter(lookup_expr="icontains")
    is_active = django_filters.BooleanFilter()

    # Related User fields
    user__username = django_filters.CharFilter(lookup_expr="icontains")
    user__first_name = django_filters.CharFilter(lookup_expr="icontains")
    user__last_name = django_filters.CharFilter(lookup_expr="icontains")
    user__email = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = doctor
        fields = [
            # doctor fields
            "name", "gender", "phone_number", "clinic_name", "clinic_phone_number",
            "email", "house_building", "locality", "pincode", "state", "city", "country",
            "designation", "title", "degree", "specializations", "education", "about_doctor",
            "experience_years", "rating", "review_count", "remark", "is_active",
            # user fields
            "user__username", "user__first_name", "user__last_name", "user__email",
        ]
