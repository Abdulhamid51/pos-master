from api.models import UserProfile, Course
def add_custom_data(request):
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.filter(user=request.user).first()
    else:
        user_profile = UserProfile.objects.none()
    return {'custom_user_profile': user_profile}


def course_context(request):
    course = Course.objects.last()
    kurs = course.som if course else 0
    return {
        'kurs_dollar':str(kurs).replace(',','')
    }