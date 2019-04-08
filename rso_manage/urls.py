from django.urls import path
from django.conf.urls import include
from . import views

urlpatterns = [
    path('', views.rso_list, name='rso_list'),
    path('rso_registration', views.AddRSO, name='rso_registration'),
    path('<rso_name>/profile', views.rso_profile, name='profile_for_rso'),
    path('<rso_name>/register', views.register, name='register_for_rso'),
    path('<rso_name>/unregister', views.unregister, name='rso_unregister'),
    path('<rso_name>/delete', views.rso_delete, name='delete_rso'),
    path('<rso_name>/add_tag', views.add_tag, name='tag_event'),
    path('<rso_name>/makeadmin/<username>', views.makeadmin, name='make_admin'),
    path('<rso_name>/removeadmin/<username>', views.removeadmin, name='remove_admin'),
<<<<<<< HEAD
=======
    # path('<rso_name>/member_distribution', views.member_distribution, name='profile_for_rso'),
    path('<rso_name>/rso_year_distribution', views.rso_year_distribution, name='rso_year_distribution')
>>>>>>> 75d642effe995d00c7c9a2172dd33b43bf9a47a3

]
