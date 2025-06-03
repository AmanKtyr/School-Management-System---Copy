from .models import AcademicSession, AcademicTerm, SiteConfig, CollegeProfile as CollegeProfileModel


def site_defaults(request):
    current_session = AcademicSession.objects.get(current=True)
    current_term = AcademicTerm.objects.get(current=True)
    vals = SiteConfig.objects.all()
    contexts = {
        "current_session": current_session.name,
        "current_term": current_term.name,
    }
    for val in vals:
        contexts[val.key] = val.value

    return contexts


def global_college_profile(request):  
    try:
        profile = CollegeProfileModel.objects.first()  
    except CollegeProfileModel.DoesNotExist:
        profile = None
    return {'profile': profile}